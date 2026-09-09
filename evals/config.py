'''
the knobs the retrieval eval was tuned with, and where its artifacts land.

kept apart from the runners on purpose: everything here is a number or a path
someone might change between runs, with no import cost for reading it. the model
registries live with the code that builds them -- embedding.MODELS, judging.JUDGES.
'''
import os
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent

## generated every run, gitignored: the score cache and every judge reply verbatim
RESULTS_DIR = EVALS_DIR / "results"
SCORES_LOG = RESULTS_DIR / "embed_scores.json"
RAW_LOG = RESULTS_DIR / "judge_raw.json"

## captured runs kept as reference points, committed
REPORTS_DIR = EVALS_DIR / "reports"

BATCH = 32   ## sentence-transformers' own default. a batch this deep is what
             ## makes the fixed overhead of a forward pass worth paying

QUERY_PROMPT = ""   ## swept 37 wordings; no instruction beat every instruction

## the gap that separates "wide enough to act on" from "close enough to ask".
## per-config because the models put gaps on different scales -- embed-minilm's median
## clear gap is 0.315, embed-qwen3-0.6b's is 0.139, so one global number cannot serve
## both. each value is the boundary that best separated clear from ambiguous on
## the case set in dataset.py. that makes this a REGRESSION gate, not an accuracy
## estimate: it is fitted on the same cases it scores, so it detects change,
## not generalization.
GAP = {
    ("embed-minilm",     "name_only"): 0.075,
    ("embed-minilm",     "name_and_desc"): 0.110,
    ("embed-qwen3-0.6b", "name_only"): 0.060,
    ("embed-qwen3-0.6b", "name_and_desc"): 0.030,
    ("embed-qwen3-4b",   "name_only"): 0.080,
    ("embed-qwen3-4b",   "name_and_desc"): 0.010,
}

## ollama judge: ask a generative model to label the pair instead of scoring it
OLLAMA_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")

## plain string, NOT an f-string -- the slots stay open until .format() fills
## them per case. the labels are the gold verdicts verbatim, so no mapping needed
JUDGE_PROMPT = """A user asked a question about a sales data warehouse.
The question contains the term "{query}".

The warehouse has these columns:
{column_a}, {column_b}.

Select one label:
- CLEAR: exactly one column above answers the term
- AMBIGUOUS: multiple columns are valid readings of the term
- REFUSE: no column above answers the term

Respond with the label only. If CLEAR, follow it with the column name."""
