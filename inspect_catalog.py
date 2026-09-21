'''
Quick look at a pre-computed column_catalog.npz, without re-running the expensive
BigQuery + encoding pipeline in precompute_col_embeddings.py.

- standalone on purpose: importing precompute_col_embeddings would re-run its module-level logic.
'''

import numpy as np

catalog = "column_catalog.npz"
n_preview = 10

d = np.load(catalog)

col_names, col_descs, embeddings = d["col_names"], d["col_descs"], d["embeddings"]

print(f"{catalog}: arrays={list(d.files)}")
print(f"{len(col_names)} columns with names, embeddings {embeddings.shape} {embeddings.dtype}")

## with normalize_embeddings=True these should all be ~1.0
norms = np.linalg.norm(embeddings, axis=1)
print(f"L2 norms: min={norms.min():.4f} max={norms.max():.4f}")

## how many columns actually carry a description (blank ones embed as just names)
n_described = sum(1 for desc in col_descs if desc.strip())
print(f"{n_described}/{len(col_descs)} columns have a description\n")

for name, desc in zip(col_names[:n_preview], col_descs[:n_preview]):
    print(f"{name}\t{desc}")


