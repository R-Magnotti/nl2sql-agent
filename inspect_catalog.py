'''
Quick look at the column_catalog table in postgres, without re-running the expensive
BigQuery + encoding pipeline in precompute_col_embeddings.py.

- standalone on purpose: importing precompute_col_embeddings would re-run its module-level logic.
'''

import os
import numpy as np
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

n_preview = 10

load_dotenv() ##read from .env file

conn = psycopg.connect(os.environ["POSTGRES_URL"])
register_vector(conn)   ## embeddings come back as pgvector Vector objects
rows = conn.execute("SELECT name, description, embedding FROM column_catalog ORDER BY id").fetchall()
conn.close()

if not rows:
    raise SystemExit("column_catalog is empty, run precompute_col_embeddings.py first")

col_names, col_descs, embeddings = zip(*rows)
embeddings = np.array([vec.to_numpy() for vec in embeddings])

print(f"{len(col_names)} columns with names, embeddings {embeddings.shape} {embeddings.dtype}")

## with normalize_embeddings=True these should all be ~1.0
norms = np.linalg.norm(embeddings, axis=1)
print(f"L2 norms: min={norms.min():.4f} max={norms.max():.4f}")

## how many columns actually carry a description (blank ones embed as just names)
n_described = sum(1 for desc in col_descs if desc.strip())
print(f"{n_described}/{len(col_descs)} columns have a description\n")

for name, desc in zip(col_names[:n_preview], col_descs[:n_preview]):
    print(f"{name}\t{desc}")
