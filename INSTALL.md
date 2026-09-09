# Install

Python 3.11.

```bash
conda create -n nl2sql python=3.11 && conda activate nl2sql
pip install -r requirements.txt
```

That covers every Python dependency. Three things it can't.

## Ollama

The LLM judges in `evals/` call a local Ollama server. Not a pip
package — install the app from [ollama.com](https://ollama.com), then:

```bash
ollama serve                    # leave running
ollama pull qwen3:0.6b          # 522 MB
ollama pull qwen3:4b            # 2.5 GB
ollama pull qwen3:4b-instruct   # shares qwen3:4b's weights, ~13 KB extra
ollama pull gemma3:4b           # 3.3 GB
```

Skip this and the judges are dropped from the run with a message; the embedding
comparison still works.

## Embedding models

Pulled from HuggingFace on first use into `~/.cache/huggingface` — no action
needed, but budget ~11 GB and a slow first run. `Qwen3-Embedding-4B` alone is
~8 GB and loads in bfloat16 to fit in 16 GB of RAM.

## BigQuery

```bash
gcloud auth application-default login
cp .env.example .env             # then fill in GCP_PROJECT_ID and BQ_DATASET
```

## If dbt fights torch

`dbt-bigquery` pins its dependencies tightly and can conflict with
`transformers`/`torch` during resolution. If pip can't solve it, put dbt in its
own environment — nothing in `agent/` imports it:

```bash
conda create -n dbt python=3.11 && conda activate dbt && pip install dbt-bigquery
```
