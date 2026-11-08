# nl2sql-agent

Ask a data warehouse questions in plain English. When the question is ambiguous, get asked back instead of getting a guess.

## 🌟 Highlights

- Asks instead of guessing. A logprob-margin gate flags any phrase in the question that could mean more than one column.
- An analytics stack underneath, a BigQuery warehouse, a dbt-tested star schema and aggregate marts (no toy schema).
- The raw data ships dirty on purpose, duplicates, nulls, orphan keys, impossible dates. Every drop in the dbt models is a written rule.
- Runs on local models through Ollama, llama3.1:8b writes the SQL, qwen3:4b-instruct is the critic and qwen3:8b runs the agent. No API keys, no cost, and no question, schema or row goes to an outside AI provider.
- Swap the backend with env vars, any OpenAI-compatible endpoint works.

## ℹ️ Overview

A lot of text-to-SQL demos skip the two things that make the problem hard in production, messy data and ambiguous questions. This project builds both in.

The question gets split into phrases, each phrase pulls its closest columns from pgvector, and a small critic model picks a column for each one. When the critic's top two picks are too close to call, the phrase gets flagged as ambiguous instead of guessed, and phrased back to the user as a clarification question. Once every phrase has a column, a local LLM writes the BigQuery SQL, sqlglot checks it, and BigQuery runs it.

February is the classic case. Calendar February and fiscal February give different numbers, so the right move is to ask which one you mean.

The pieces are three tools, `check_ambiguity`, `answer_question` and `describe_data`, served over MCP. A local agent runs the clarification loop and answers in plain English.

## 🚀 Usage

Start the MCP server, then talk to the agent in a second terminal. Both run from the repo root.

```bash
python agent/mcp_server.py --http   ## terminal 1: serves the three tools at http://127.0.0.1:8000/mcp
python agent/mcp_client.py          ## terminal 2: chat with the agent
```

Without `--http` the server talks over stdio instead, for MCP clients that start it themselves, like Claude Desktop or the MCP Inspector.

To call the tools directly, run Python from the `agent/` folder.

```python
from RAG_agent import check_ambiguity, answer_question

question = "Which quarter had the highest sales?"

check_ambiguity(question)
answer_question(question, {"Which quarter": "dim_date.fiscal_quarter",
                           "the highest sales": "fact_sales.sales_amount"})
```

`check_ambiguity` gives back each phrase with its verdict, its top 3 columns and their scores. `answer_question` takes a column for each phrase and gives back the SQL and the rows.

And here's the ambiguity straight from the warehouse.

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

Same question, two answers about $6K apart, and both are fair readings. An agent that picks one without asking is guessing.

## ⚙️ How it works

1. **Preprocess.** Every warehouse column gets one string built from its table name, column name and description, embedded with `all-MiniLM-L6-v2` and stored in a pgvector table. The descriptions are empty for now, so it's names only. MiniLM is small and fast, retrieval only has to get the right column into the top 3, and the critic makes the actual call.
2. **Parse.** benepar parses the question and keeps the phrases that can point at a column - noun phrases like "the highest sales", prepositional phrases like "in February 2024", wh-phrases like "which quarter" and adverb phrases like "monthly".
3. **Retrieve.** Each phrase gets embedded with the same model, and pgvector returns its 3 closest columns by cosine similarity. It's an exact search, at 74 columns there's no need for an index.
4. **Judge.** One call to a small critic model (qwen3:4b-instruct) covers every phrase. Each phrase gets its candidates as lettered options, A to C, plus X for no match, and the critic answers with a letter per phrase at temperature 0. The logprobs at each letter turn into a probability for every option, and when the top two are within 0.1 of each other the phrase is ambiguous.
5. **Report.** `check_ambiguity` returns every phrase with its verdict (clear, ambiguous or no match), its pick and the scores behind it. Nothing gets asked or guessed here.
6. **Clarify.** When a phrase comes back ambiguous, the caller asks the user which one they meant, offering only the candidates `check_ambiguity` returned, then passes that pick to `answer_question`. For a no-match phrase, the caller tells the user nothing in the data covers it. The caller is usually the agent, which also decides when more asking stops helping. Called from Python, it's you.
7. **Answer.** `answer_question` takes a column for each phrase. llama3.1:8b writes the SQL with six worked examples in its prompt, sqlglot checks it's valid BigQuery SQL, and BigQuery runs it. A bad query comes back as an error with the stage that failed.

## 🧪 Evals

```bash
pytest evals -v         ## ~11GB of embedder weights, hundreds of ollama calls
python -m evals.report  ## the same evals as a table instead of pass/fail
```

The evals ask which model the agent should use for the decide-or-ask call, over 41 gold-labelled cases. The write-up is in [DECISIONS.md](DECISIONS.md) and the harness is in [evals/README.md](evals/README.md).

## ⬇️ Installation

You need a GCP project with a BigQuery dataset (the free sandbox works), gcloud auth, a dbt profile pointing at it, Docker and [Ollama](https://ollama.com).

Install the Python packages.

```bash
pip install -r requirements.txt
python -c "import benepar; benepar.download('benepar_en3')"   ## parser model, one time
```

Build the warehouse.

```bash
## load the four CSVs as *_raw tables (one bq load per file)
bq load --autodetect nl2sql_dev.fact_sales_raw data/fact_sales.csv
## ... repeat for the three dims

cd dbt_models
dbt build        ## 10 models, 14 tests, dependency order
```

Set up `.env` at the repo root.

```
GCP_PROJECT_ID=your-project-id
BQ_DATASET=nl2sql_dev
POSTGRES_URL=postgresql://postgres:devpassword@localhost:5433/nl2sql
```

Build the column catalog.

```bash
docker compose up -d                  ## postgres with pgvector, port 5433
python precompute_col_embeddings.py   ## embeds every warehouse column into postgres
```

Get the models.

```bash
ollama serve                   ## in its own terminal
ollama pull llama3.1:8b        ## SQL model, ~5 GB, one time
ollama pull qwen3:4b-instruct  ## critic model, ~2.5 GB, one time
ollama pull qwen3:8b           ## agent model, ~5 GB, one time
```

Then start the server and the agent like in Usage.

For a different model or backend, set `LLM_BASE_URL`, `LLM_MODEL` and `LLM_API_KEY`. The critic and the SQL model read the same ones for now. The agent's model is set in `agent/mcp_client.py`.

## 📊 The data

Four synthetic CSVs, with the mess baked in on purpose.

| table        | rows                      | role                                                 |
| ------------ | ------------------------- | ---------------------------------------------------- |
| fact_sales   | 66,234 raw / 65,902 clean | weekly sales containing units, revenue, promo flag   |
| dim_date     | 104                       | one row per week, calendar + 4-4-5 fiscal attributes |
| dim_product  | 61                        | 4 categories, 12 subcategories, 7 brands             |
| dim_retailer | 15                        | 5 channels, 5 regions                                |

The gap between raw and clean comes from 300 duplicate rows, 30 orphan product keys (a foreign key pointing at a row that doesn't exist) and 2 orphan date keys. Every drop is a written rule in the dbt models, and the orphan keys are tested on every build. Mart revenue reconciles to fact revenue exactly ($17,119,610.91). The column definitions and the full mess are in [data/README.md](data/README.md).

## 🗺️ Roadmap

Next up, roughly in order.

1. Gate fixes, a similarity floor so near misses get flagged, the raw tables out of the catalog, and a check that the SQL only uses the picked columns
2. An eval harness, about 40 gold questions with their right answers, run end to end on the old pipeline and the new one
3. Column descriptions in the dbt YAML
4. A semantic layer, so computed metrics like average selling price (revenue over units) get defined once in dbt and the matcher can find them
5. Airflow, with incremental daily loads

## 💭 Feedback

If you spot something broken or have ideas, open an issue.