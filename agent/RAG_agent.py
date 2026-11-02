'''
the two tools the agent calls. the fixed steps stay as code in here, and the agent makes the
clarification calls (DECISIONS.md: "Code for the fixed steps, an agent for the clarification calls")

check_ambiguity(question): chunk the question, vector search each chunk, and have the critic judge each one.
    reports the evidence and never asks anyone
answer_question(question, columns): takes the agent's phrase -> column picks, generates the sql,
    checks it with sqlglot, runs it on bigquery

neither one raises: a stage that fails comes back as error = {"stage": ..., "message": ...}
'''

import json

from prompt_user_question import t
import generator_model
from agent_utils import is_valid_sql, get_columns_used, TOP_K
from NLU import NLU
from deliberate import deliberate
from google.cloud import bigquery

## clients load once at import, not once per call
ollama_client = generator_model.load_client()
bq_client = bigquery.Client()


## the error both tools hand back instead of raising: which stage failed, and why
def stage_error(stage, e):
    return {"stage": stage, "message": f"{type(e).__name__}: {e}"}


## in: user question (str)
## out: {"question", "phrases": one entry per chunk (built in deliberate), "error": None or {"stage", "message"}}
def check_ambiguity(question):
    question = question.strip()   ## benepar's retokenizer asserts on whitespace-only tokens
    result = {"question": question, "phrases": [], "error": None}

    try:
        ## key: question segment (spacy span), value: its topk (column name, cosine score) pairs
        segment_topk_dict = NLU(question, TOP_K)
    except Exception as e:
        result["error"] = stage_error("nlu", e)
        return result

    try:
        *_, phrases = deliberate(question, segment_topk_dict)   ## the 3 buckets in front are for the notebook
        result["phrases"] = phrases
    except Exception as e:
        result["error"] = stage_error("deliberate", e)

    return result


## in: user question (str), columns: the agent's phrase -> column picks, e.g. {"Which quarter": "dim_date.fiscal_quarter"}
## out: {"status": "answered" or "error", "sql", "columns_used": the columns sqlglot finds in the sql,
##       "rows": list of dicts, "error": None or {"stage", "message"}}
def answer_question(question, columns):
    result = {"status": "error", "sql": None, "columns_used": [], "rows": [], "error": None}

    try:
        pairs = [(column, phrase) for phrase, column in columns.items()]   ## generator_model takes (column, phrase)
        ## content can come back None, "" fails validation below with sqlglot's message instead
        result["sql"] = generator_model.get_response(client=ollama_client, question=question, pairs=pairs) or ""
    except Exception as e:
        result["error"] = stage_error("generate", e)
        return result

    ## must parse, and must be a SELECT, before anything runs on bigquery
    valid, sql_error = is_valid_sql(result["sql"])
    if not valid:
        result["error"] = {"stage": "validate", "message": sql_error}
        return result
    result["columns_used"] = get_columns_used(result["sql"])

    try:
        ## a bigquery Row prints as Row((4,), {'calendar_quarter': 0}) where 0 is a position, dict() gives {'calendar_quarter': 4}
        result["rows"] = [dict(row) for row in bq_client.query(result["sql"]).result()]
    except Exception as e:
        result["error"] = stage_error("bigquery", e)
        return result

    result["status"] = "answered"
    return result


## console driver, only runs on `python RAG_agent.py`, not when a notebook or the agent imports the tools
## you stand in for the agent: pick a number for every phrase the critic couldn't settle
if __name__ == "__main__":
    report = check_ambiguity(t)   ## t is read from prompt_user_question.py
    if report["error"]:
        raise SystemExit(f"check_ambiguity failed at {report['error']['stage']}: {report['error']['message']}")

    ## clear picks go straight in, no_match phrases stay out, ambiguous and unrated ones get asked
    columns = {}
    for p in report["phrases"]:
        if p["verdict"] == "clear":
            columns[p["phrase"]] = p["pick"]
        elif p["verdict"] in ("ambiguous", "unrated"):
            print(f'\n"{p["phrase"]}" is {p["verdict"]}:')
            for n, c in enumerate(p["candidates"], 1):
                prob = "" if c["prob"] is None else f", critic {c['prob']:.2f}"
                print(f"  {n}. {c['column']}  (cosine {c['score']:.2f}{prob})")
            print("  0. none of these")

            choice = ""
            while choice not in [str(n) for n in range(len(p["candidates"]) + 1)]:
                choice = input("> ").strip()
            if choice != "0":
                columns[p["phrase"]] = p["candidates"][int(choice) - 1]["column"]

    print(f"\ncolumns: {columns}")
    print(json.dumps(answer_question(report["question"], columns), indent=2, default=str))   ## default=str: bigquery dates, decimals
