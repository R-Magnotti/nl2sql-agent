'''
This script is to precompute all the column name vector embeddings for easy cosine-similariy computing for the RAG agent.

- only run when oltp data changes (i.e. adds new columns), or at scheduled intervals. doesn't need to be run every time the user submits a query.
'''

import os
import numpy as np
from dotenv import load_dotenv
from google.cloud import bigquery
import sys
import psycopg  ## for postgresql operation in python

## embedding model
from sentence_transformers import SentenceTransformer
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

load_dotenv() ##read from .env file

PROJECT = os.getenv("GCP_PROJECT_ID")
DATASET = os.getenv("BQ_DATASET", "nl2sql_dev")

client = bigquery.Client(project=PROJECT)

def iter_columns(dataset=DATASET, tables_only=True):
    """yield (table_name, col_name, col_desc) for every column in the dataset."""
    #  client.list_tables() returns an iterator of TableListItem
    for item in client.list_tables(dataset):    
        
        ## marts are TABLE, staging models are VIEW -- skip the views or you embed the same column twice under two names
        if tables_only and item.table_type != "TABLE":
            continue
        
        table = client.get_table(item.reference)
        for field in table.schema:
            yield table.table_id, field.name, field.description or ""

col_names, col_descs = [], []

for table_name, col_name, col_desc in iter_columns():
    print(f"{table_name}.{col_name}\t{col_desc}")
    col_names.append(f"{table_name}.{col_name}")    ## so table name is prefix of col name
    col_descs.append(col_desc)  
    
texts = [f"{n}: {d}" for n, d in zip(col_names, col_descs)]

## normalizes the len to L2 norm len of 1, making cos similarity faster
vecs = embed_model.encode(texts, normalize_embeddings=True) 

''' new way of saving vecs in pgvector '''
from pgvector.psycopg import register_vector

conn = psycopg.connect(os.getenv("POSTGRES_URL"))
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(conn)   ## lets psycopg send numpy arrays as pgvector vectors
cursor = conn.cursor()   ## after register_vector: a cursor only gets the adapters its connection had when it was made
## size comes from the vectors themselves: 384 for all-minilm
cursor.execute(f"CREATE TABLE IF NOT EXISTS column_catalog (id SERIAL PRIMARY KEY, name TEXT, description TEXT, embedding vector({vecs.shape[1]}))")
cursor.execute("TRUNCATE column_catalog")   ## full rebuild each run, not another copy on top
cursor.executemany("INSERT INTO column_catalog (name, description, embedding) VALUES (%s, %s, %s)", [(name, desc, vec) for name, desc, vec in zip(col_names, col_descs, vecs)])
conn.commit()

## read it back and check it. vectors come back as pgvector Vector objects, .to_numpy() makes them arrays again
saved = np.array([vec.to_numpy() for (vec,) in cursor.execute("SELECT embedding FROM column_catalog")])
assert len(saved) == len(col_names), "row count doesn't match the columns embedded"
assert np.allclose(np.linalg.norm(saved, axis=1), 1.0), "vectors not normalized"
print(f"ok: {saved.shape[0]} columns, dim {saved.shape[1]}")

cursor.close()
conn.close()

''' old way of saving vecs in npz file '''
## col_names[i], col_descs[i], joint embedding
# np.savez_compressed("column_catalog.npz", col_names=np.array(col_names), col_descs=np.array(col_descs), embeddings=vecs)
# print(f"\nsaved {len(col_names)} columns to column_catalog.npz")