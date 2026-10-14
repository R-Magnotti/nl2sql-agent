import re
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import re
import sqlglot

## this will add DATABASE. prefix to all FROM clauses
# TODO: fails for CTEs, maybe better to use sqglot in future ...
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
output: topk column names : [col_name:str, ..., col_name:str]
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

    ## .tolist() to hand back real python strs
    return col_names[top].tolist()

## to extract critic model output pairs (number, letter),
# number is the input segment number (can get back original user input text using "chunks" variable)
# letter is the output most relevant schema option
def get_critic_picks(reply):
    return re.findall(r"(\d+) -> ([A-C])", reply)

## verify the sql generation model output is valid sql
def is_valid_sql(sql):
    try:
        tree = sqlglot.parse_one(sql, read="bigquery")
    except sqlglot.errors.SqlglotError:
        return False
    return isinstance(tree, sqlglot.exp.Select)
