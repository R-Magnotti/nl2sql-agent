import re
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer
import re
import sqlglot

with open(Path(__file__).resolve().parent / "config.json") as f:
    config = json.load(f)

THRESHOLD = config["check_ambiguity"]["threshold"]
TOP_K = config["check_ambiguity"]["top_k"]
RETRIES = config["answer_question"]["retries"]   ## how many times to regenerate sql that puts a column on the wrong table

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
func to search the column catalog in postgres (pgvector) and return topk most cosine similar results
input: embedded user input query constituent / chunk (vector from embed_model), k : int
output: topk (column name, cosine score) pairs, best first : [(col_name:str, score:float), ..., (col_name:str, score:float)]
'''
## postgres connection + model load once at import, not once per call. Vector_search runs for every
## constituent in the question, and opening a new connection each time is a lot of overhead.

## .env is at the repo root, next to precompute_col_embeddings.py. path is relative to THIS file, not the pwd
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

## autocommit: each query is its own transaction. without it the agent holds a lock on column_catalog
## between searches, and the TRUNCATE in precompute_col_embeddings.py waits until the agent exits
pg_conn = psycopg.connect(os.environ["POSTGRES_URL"], autocommit=True)
register_vector(pg_conn)   ## lets psycopg send numpy arrays as pgvector vectors

embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def vector_search(chunk_vec, k):
    ## <=> is cosine distance (1 - cosine similarity), so the closest columns come first
    return pg_conn.execute(
        "SELECT name, 1 - (embedding <=> %(vec)s) FROM column_catalog ORDER BY embedding <=> %(vec)s LIMIT %(k)s",
        {"vec": chunk_vec, "k": k},
    ).fetchall()

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

## every real "table.column" in the warehouse, and the tables they belong to.
## read once at import, so restart the agent after re-running precompute_col_embeddings.py
catalog_columns = {name for (name,) in pg_conn.execute("SELECT name FROM column_catalog")}
catalog_tables = {name.split(".")[0] for name in catalog_columns}

## in: "table.column" names from get_columns_used
## out: one line per column that isn't in its table, saying where it really lives. empty = all good
def wrong_table_columns(columns_used):
    problems = []
    for name in columns_used:
        table, _, column = name.rpartition(".")
        ## bare names (multi-table query) and CTE/subquery aliases can't be checked against the catalog
        if table not in catalog_tables or name in catalog_columns:
            continue
        homes = sorted(c.split(".")[0] for c in catalog_columns if c.split(".")[1] == column)
        where = f"it is in {', '.join(homes)}" if homes else "and no table has it"
        problems.append(f"{table} has no column {column}; {where}")
    return problems

## in: dict of tokens and their probs, e.g. {"A": 0.02, "B": 0.90, "C": 0.03, "X": 0.05}
## out: (True if ambiguous else False, margin = top 1 prob - top 2 prob)
## function: judge if top 1 token prob is within THRESHOLD (from config file) of top 2 token prob
def judge_ambiguous(target_tokens):
    top_1, top_2 = sorted(target_tokens.values(), reverse=True)[:2]
    margin = top_1 - top_2
    return margin <= THRESHOLD, margin