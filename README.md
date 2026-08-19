# nl2sql-agent

Ask a data warehouse questions in plain English. When the question is ambiguous, get asked back instead of getting a guess.

## 🌟 Highlights

- A real analytics stack underneath: BigQuery warehouse, dbt-tested star schema, aggregate marts. No toy schema.
- The raw data ships dirty on purpose: duplicates, nulls, orphan keys, impossible dates. Every fix is an explicit, documented decision.
- Runs on a local model (llama3.1:8b via Ollama). No API keys, no cost.
- Swap the model or backend with env vars. Any OpenAI-compatible endpoint works.

## ℹ️ Overview

Many text-to-SQL demos skip the two things that make the problem hard in production: messy data and ambiguous questions. This project builds both in.

The pipeline goes: English question → local LLM generates BigQuery SQL → a cleanup pass fixes what the model gets wrong → BigQuery executes → answer comes back.

The end goal is the ambiguity layer. Right now, for example, the agent silently picks the calendar reading of "February," which means it's wrong for anyone who meant fiscal. The plan is a decide-or-ask policy, answer when the readings agree, ask a clarifying question when they'd give different numbers. That's the part I want to improve upon.

## 🚀 Usage

Ask it a question:

```bash
python agent/RAG_coordinator.py
```

Output:

```
Cleaned SQL query: SELECT SUM(total_revenue) FROM nl2sql_dev.agg_monthly_product_sales WHERE calendar_year = 2025 AND calendar_month = 2
Row((671247.12,), {'f0_': 0})
```

The question lives in `agent/Prompt.py` for now. Edit it, rerun.

And here's the representative example of ambiguity, straight from the warehouse:

```sql
SELECT 'calendar' AS definition, SUM(total_revenue) AS feb_2024_revenue
FROM nl2sql_dev.agg_monthly_product_sales
WHERE calendar_year = 2024 AND calendar_month = 2

UNION ALL

SELECT 'fiscal', SUM(total_revenue)
FROM nl2sql_dev.agg_fiscal_monthly_product_sales
WHERE fiscal_year = 2024 AND fiscal_month = 2
```

```
calendar   642274.51
fiscal     636233.29
```

Same question, but the results are ~$6K apart. But both make sense. An agent that picks one without asking is making a guess.

## ⬇️ Installation

You need: a GCP project with a BigQuery dataset (free sandbox works), gcloud auth, a dbt profile pointing at it, and [Ollama](https://ollama.com).

Build the warehouse:

```bash
## load the four CSVs as *_raw tables (one bq load per file)
bq load --autodetect nl2sql_dev.fact_sales_raw data/fact_sales.csv
## ... repeat for the three dims

cd dbt_models
dbt build        ## 10 models, 14 tests, dependency order
```

Run the agent:

```bash
ollama serve                 ## in its own terminal
ollama pull llama3.1:8b      ## only run one time, should be ~5 GB
pip install openai google-cloud-bigquery
python agent/RAG_coordinator.py
```

Different model or backend: set `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`.

## 📊 The data

Four CSVs in `/data`, generated with a fixed seed, so every number in this README reproduces exactly.


| table        | rows                      | role                                                 |
| ------------ | ------------------------- | ---------------------------------------------------- |
| fact_sales   | 66,234 raw / 65,902 clean | weekly sales containing units, revenue, promo flag   |
| dim_date     | 104                       | one row per week, calendar + 4-4-5 fiscal attributes |
| dim_product  | 61                        | 4 categories, 12 subcategories, 7 brands             |
| dim_retailer | 15                        | 5 channels, 5 regions                                |


The gap between raw and clean comes from 300 duplicate rows, 30 'orphan' product keys (a foreign key pointing at a row that doesn't exist), 2 orphan date keys, and every drop corresponds to a written rule in the dbt models, tested on every build. Mart revenue reconciles to fact revenue exactly ($17,119,610.91). Column definitions and the full mess documented here: `[data/README.md](data/README.md)`.

## 🗺️ Roadmap

In order:

1. Few-shot exemplars and prompt hardening, driven by failure modes I hit while building (invented columns, SQLite functions leaking into BigQuery SQL, quoted integer literals)
2. pgvector RAG over schema docs, so context is retrieved per question instead of dumped into every prompt
3. The decide-or-ask ambiguity layer
4. Eval harness with gold queries against the committed dataset



## 💭 Feedback

If you spot something broken or have ideas, open an issue.
