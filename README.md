# nl2sql-agent

A natural-language-to-SQL agent built on a real analytics stack, BigQuery, dbt, and a dimensional warehouse I designed and tested from raw data up. The interesting problem this project attacks is ambiguity. "What was February revenue?" has two defensible answers in this warehouse ($643,735.40 on the calendar definition, $637,895.06 on the fiscal 4-4-5 definition), and an agent that silently picks one is wrong half the time. The end goal is an agent that detects that ambiguity and asks a clarifying question instead of guessing.

## Why this exists

Text-to-SQL demos usually run against a clean toy schema and dodge the two things that make the problem hard in production, messy data and ambiguous questions. This project builds both in on purpose.

- The raw data ships dirty (duplicates, nulls, orphan keys, impossible dates) and the warehouse layer has to handle every defect with an explicit, documented decision.
- The date dimension carries two disagreeing calendars (calendar months and a 4-4-5 fiscal calendar, standard in CPG), so time-based questions are genuinely ambiguous the way they are at a real consumer-goods company.

## Current status

Built and verified:

- Synthetic CPG dataset: star schema, 66,234 raw fact rows at product x retailer x week grain, two years of weekly data, seasonality and promo lift baked in, deterministic seed
- BigQuery warehouse (free sandbox) with raw tables loaded via bq
- dbt project: 4 staging models, 3 dimension tables, 1 fact table, materialization configured by layer (staging as views, marts as tables)
- 12 schema tests passing: unique and not_null on every dimension key, not_null and relationship tests on every fact foreign key
- dbt docs generated
- Full row-count reconciliation of the fact table, documented below

In progress (roadmap order):

- Aggregate marts (revenue by category by month, and similar), the query surface the agent will target
- pgvector RAG over schema documentation for context retrieval
- Ambiguity detection and clarifying-question layer
- Eval harness with gold queries against the committed dataset

## The data

Four CSVs in `/data`, generated with a fixed seed so every number in this README reproduces exactly.

| table | rows | role |
|---|---|---|
| fact_sales | 66,234 raw / 65,903 clean | weekly sales events: units, revenue, promo flag |
| dim_date | 104 | one row per week, calendar and 4-4-5 fiscal attributes |
| dim_product | 61 | 4 categories, 12 subcategories, 7 brands |
| dim_retailer | 15 | 5 channels, 5 regions |

The fact file ships with a documented mess manifest: 300 duplicate rows, 250 null sales amounts, 2 impossible date keys, 30 orphan product keys. Full column definitions and the manifest live in [`data/README.md`](data/README.md).

## Stack

- **BigQuery** as the warehouse (sandbox tier, no cost)
- **dbt-core 1.12** with the BigQuery adapter for transformations, tests, and docs
- **Python** (stdlib only) for the deterministic data generator
- Planned: **pgvector** for schema-doc retrieval, **sqlglot** for SQL parsing and validation, **Docker Compose** for the agent services

## Repo structure

```
data/          four seed CSVs plus the data README and mess manifest
dbt_models/    the dbt project
  models/
    staging/   4 views, row-exact mirrors of raw
    marts/     3 dims + fact_sales + schema.yml (12 tests)
```

## Running it

Requires a GCP project with a BigQuery dataset, gcloud auth, and a dbt profile pointing at it.

```bash
# load the four CSVs as *_raw tables (one bq load per file)
bq load --autodetect nl2sql_dev.fact_sales_raw data/fact_sales.csv
# ... repeat for the three dims

cd dbt_models
dbt build        # runs all 8 models and all 12 tests in dependency order
dbt docs generate
```