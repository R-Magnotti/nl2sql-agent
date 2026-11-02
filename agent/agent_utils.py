import re
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import re
import sqlglot

with open(Path(__file__).resolve().parent / "config.json") as f:
    config = json.load(f)

THRESHOLD = config["threshold"]
TOP_K = config["top_k"]

## this will add DATABASE. prefix to all FROM clauses
def add_table_prefix(query: str, prefix: str = "nl2sql_dev") -> str:
    pattern = re.compile(
        r'\b(FROM|JOIN)(\s+)'   # the keyword + whitespace
        r'(?!\()'               # skip subqueries: FROM (SELECT ...)
        r'([A-Za-z_]\w*)'       # a bare table name
        r'(?![\w.])',           # not already schema-qualified
        flags=re.IGNORECASE,
    )
    return pattern.sub(rf'\1\2{prefix}.\3', query)


def clean_SQL_query_driver(query: str):
    ## fix FROM clause prefixes
    return add_table_prefix(query)

''' 
func to search pre-computed col name embeddings and return topk most cosine similar results
input: user input query constituent / chunk : str, k : int
output: topk (column name, cosine score) pairs, best first : [(col_name:str, score:float), ..., (col_name:str, score:float)]
'''
## precomputed col embeddings + model load once at import, not once per call. Vector_search runs for every
## constituent in the question, and re-reading the npz each time is a lot of overhead.

## path is relative to THIS file, not the pwd
catalog = np.load(Path(__file__).resolve().parent.parent / "column_catalog.npz")
col_names, embeddings = catalog["col_names"], catalog["embeddings"]

embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def vector_search(chunk_vec:str, k):
    ## precomputed col embedding vectors are already L2-normalized, so dot product (the "@" sign)=cosine similarity 
    scores = embeddings @ chunk_vec

    ## argsort is ascending, so flip it and take the front k
    top = np.argsort(scores)[::-1][:k]

    ## .tolist() to hand back python strs and floats
    return list(zip(col_names[top].tolist(), scores[top].tolist()))

## to extract critic model output pairs (number, letter),
# number is the input segment number (can get back original user input text using "chunks" variable)
# letter is the output most relevant schema option
def get_critic_picks(reply):
    return re.findall(r"(\d+) -> ([A-C])", reply)

## verify the sql generation model output is valid sql
## out: (True, None) if valid, else (False, error message)
def is_valid_sql(sql):
    try:
        tree = sqlglot.parse_one(sql, read="bigquery")
    except sqlglot.errors.SqlglotError as e:
        return False, str(e)
    ## sqlglot parses a DELETE or DROP just fine, so not-a-SELECT gets our own message
    if not isinstance(tree, sqlglot.exp.Select):
        return False, f"expected a SELECT, got {type(tree).__name__}"
    return True, None

## in: sql that already passed is_valid_sql
## out: sorted "table.column" names the sql reads, e.g. ["dim_date.fiscal_quarter", "fact_sales.sales_amount"]
def get_columns_used(sql):
    tree = sqlglot.parse_one(sql, read="bigquery")

    ## alias -> real table, e.g. {"f": "fact_sales"} (.name leaves off the nl2sql_dev dataset)
    tables = {table.alias_or_name: table.name for table in tree.find_all(sqlglot.exp.Table)}
    only_table = next(iter(tables.values())) if len(tables) == 1 else None   ## bare column names belong to it
    select_aliases = {alias.alias for alias in tree.find_all(sqlglot.exp.Alias)}

    used = set()
    for column in tree.find_all(sqlglot.exp.Column):
        ## "ORDER BY revenue" points back at the select alias, not at a table column
        alias_ref = (not column.table and column.name in select_aliases
                     and column.find_ancestor(sqlglot.exp.Order, sqlglot.exp.Group, sqlglot.exp.Having))
        if alias_ref:
            continue
        table = tables.get(column.table, column.table) if column.table else only_table
        used.add(f"{table}.{column.name}" if table else column.name)
    return sorted(used)

## in: dict of tokens and their probs, e.g. {"A": 0.02, "B": 0.90, "C": 0.03, "X": 0.05}
## out: (True if ambiguous else False, margin = top 1 prob - top 2 prob)
## function: judge if top 1 token prob is within THRESHOLD (from config file) of top 2 token prob
def judge_ambiguous(target_tokens):
    top_1, top_2 = sorted(target_tokens.values(), reverse=True)[:2]
    margin = top_1 - top_2
    return margin <= THRESHOLD, margin
    