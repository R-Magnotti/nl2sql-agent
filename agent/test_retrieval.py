'''
retrieval eval: can an embedding lookup tell "answer it" from "ask about it"?

    pytest agent/test_retrieval.py -v      ## gold verdicts as pass/fail
    pytest agent/test_retrieval.py -v -k name_only
    python agent/test_retrieval.py         ## the same scores as a raw matrix

each case carries a gold verdict, and each verdict gets its own assertion:
  clear      the gap must be wide    -> agent proceeds with expected_top
  ambiguous  the gap must be narrow  -> agent asks the user which grain they meant
  refuse     nothing in the schema answers this, so its top score must come in
             under the weakest clear probe -- otherwise no cutoff can refuse it
             without also refusing a legitimate question
'''
import os

import pytest
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm

COLUMNS = {
        "fiscal_year": "A fiscal year (also known as a financial year, or sometimes budget year) is a one-year time interval whose beginning and end may be shifted with respect to the calendar year (1 January to 31 December)",
        "fiscal_month": "Any fiscal month of any Fiscal Year, which month shall generally end on the Saturday closest to the last day of each calendar month in accordance with the fiscal accounting calendar",
        "calendar_year": "A period of a year beginning and ending with the dates that are conventionally accepted as marking the beginning and end of a numbered year",
        "calendar_month": "one of the months as named in the calendar",
        "product_key": "surrogate key identifying a product, joins fact_sales to dim_product",
        "product_name": "the full display name of a product, including brand, variant, and size",
        "total_units": "total number of units sold, summed",
        "total_revenue": "total sales revenue in dollars, summed"
}

## the second variant carries the name AS WELL AS the description: the judge is
## asked to name the column it picks, which it cannot do if it was only ever
## shown prose. so this asks "does the description help the name" rather than
## "does the description work instead of the name"
VARIANTS = {"name_only": "{name}", "name_and_desc": "{name}: {desc}"}

## each entry builds its model when called, so only one set of weights is in
## memory at a time -- all three at once is about 10GB
MODELS = {
    "embed-minilm": lambda: SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"),

    "embed-qwen3-0.6b": lambda: SentenceTransformer(
        "Qwen/Qwen3-Embedding-0.6B",
        processor_kwargs={"padding_side": "left"}),      ## last-token pooling needs left pad

    "embed-qwen3-4b": lambda: SentenceTransformer(
        "Qwen/Qwen3-Embedding-4B",
        processor_kwargs={"padding_side": "left"},
        model_kwargs={"dtype": "bfloat16"}),             ## fp32 would be ~16GB of weights
}

QUERY_PROMPT = ""   ## swept 37 wordings; no instruction beat every instruction

## the gap that separates "wide enough to act on" from "close enough to ask".
## per-config because the models put gaps on different scales -- embed-minilm's median
## clear gap is 0.315, embed-qwen3-0.6b's is 0.139, so one global number cannot serve
## both. each value is the boundary that best separated clear from ambiguous on
## the case set below. that makes this a REGRESSION gate, not an accuracy
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
JUDGES = {
    "prompt-qwen3-0.6b":    "qwen3:0.6b",
    "prompt-qwen3-4b":      "qwen3:4b",
    "prompt-qwen3-4b-inst": "qwen3:4b-instruct",
    "prompt-gemma3-4b":     "gemma3:4b",
}

## the embedders score all 41 cases -- they are cheap. the judges take a forward
## pass per call, so they run this fixed subset instead: two grain probes, one
## qualified, one clear measure, one unanswerable.
JUDGE_PROBES = ["year", "month", "fiscal year", "revenue", "profit"]

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

## (probe, expected_top, expected_other, gold_verdict)
CASES = [
    ## --- time, bare terms: the core ambiguity ---
    ("year",                 "calendar_year",  "fiscal_year",    "ambiguous"),
    ("month",                "calendar_month", "fiscal_month",   "ambiguous"),
    ("february",             "calendar_month", "fiscal_month",   "ambiguous"),
    ("april",                "calendar_month", "fiscal_month",   "ambiguous"),
    ("october",              "calendar_month", "fiscal_month",   "ambiguous"),
    ("october 2024",         "calendar_month", "fiscal_month",   "ambiguous"),

    ## --- time, qualified: the qualifier should win decisively ---
    ("fiscal year",          "fiscal_year",    "calendar_year",  "clear"),
    ("fiscal month",         "fiscal_month",   "calendar_month", "clear"),
    ("fiscal february",      "fiscal_month",   "calendar_month", "clear"),
    ("fiscal april",         "fiscal_month",   "calendar_month", "clear"),
    ("fiscal october",       "fiscal_month",   "calendar_month", "clear"),
    ("fiscal october 2024",  "fiscal_month",   "calendar_month", "clear"),
    ("calendar february",    "calendar_month", "fiscal_month",   "clear"),
    ("FY2024",               "fiscal_year",    "calendar_year",  "clear"),
    ("fiscal 2024",          "fiscal_year",    "calendar_year",  "clear"),
    ("calendar 2024",        "calendar_year",  "fiscal_year",    "clear"),

    ## --- qualified with no shared token: tests semantics vs string overlap ---
    ("accounting february",  "fiscal_month",   "calendar_month", "clear"),
    ("4-4-5 february",       "fiscal_month",   "calendar_month", "clear"),

    ## --- natural phrasing: do extra tokens wreck the signal ---
    ("in february",          "calendar_month", "fiscal_month",   "ambiguous"),
    ("the month of february","calendar_month", "fiscal_month",   "ambiguous"),
    ("last month",           "calendar_month", "fiscal_month",   "ambiguous"),

    ## --- clear measures: these set the floor. if these score low,
    ##     any floor that catches profit also blocks normal questions ---
    ("revenue",              "total_revenue",  "total_units",    "clear"),
    ("total sales",          "total_revenue",  "total_units",    "clear"),
    ("dollars",              "total_revenue",  "total_units",    "clear"),
    ("units",                "total_units",    "total_revenue",  "clear"),
    ("units sold",           "total_units",    "total_revenue",  "clear"),
    ("how many units",       "total_units",    "total_revenue",  "clear"),

    ## --- clear dimensions ---
    ("product",              "product_name",   "product_key",    "clear"),
    ("product name",         "product_name",   "product_key",    "clear"),
    ("item",                 "product_name",   "product_key",    "clear"),

    ## --- second ambiguity axis: measure, not time ---
    ("sales",                "total_revenue",  "total_units",    "ambiguous"),
    ("performance",          "total_revenue",  "total_units",    "ambiguous"),
    ("how did it do",        "total_revenue",  "total_units",    "ambiguous"),

    ## --- refuse: nothing in the schema answers these.
    ##     watch top_score, not the gap ---
    ("profit",               "total_revenue",  "total_units",    "refuse"),
    ("margin",               "total_revenue",  "total_units",    "refuse"),
    ("gross margin",         "total_revenue",  "total_units",    "refuse"),
    ("cost",                 "total_revenue",  "total_units",    "refuse"),
    ("cogs",                 "total_revenue",  "total_units",    "refuse"),
    ("discount",             "total_revenue",  "total_units",    "refuse"),
    ("inventory",            "total_units",    "total_revenue",  "refuse"),
    ("customer count",       "total_units",    "total_revenue",  "refuse"),
]


BATCH = 32   ## sentence-transformers' own default. a batch this deep is what
             ## makes the fixed overhead of a forward pass worth paying


def in_batches(items, label):
    '''chunk the work so every batch is full, under one labelled bar'''
    chunks = [items[i:i + BATCH] for i in range(0, len(items), BATCH)]
    return tqdm(chunks, desc=label, leave=False)


def load(name):
    '''
    build one model, with its query instruction blanked -- 37 wordings were
    swept and none of them beat none.
    '''
    model = MODELS[name]()
    if model.prompts["query"]:
        model.prompts["query"] = QUERY_PROMPT
    return model


def score_all(model, variant, label=""):
    '''
    one score per (probe, column): embed the columns once, the probes once, then
    just dot products.

    the encoding goes over in full batches. splitting it per probe leaves every
    batch one item deep, and a barely-filled batch costs almost as much as a
    full one.
    '''
    columns = {name: VARIANTS[variant].format(name=name, desc=desc)
               for name, desc in COLUMNS.items()}
    probes = [case[0] for case in CASES]
    bar = f"{label} {variant}".strip()

    docs = model.encode(list(columns.values()), show_progress_bar=False)
    vecs = []
    for chunk in in_batches(probes, bar):
        vecs.extend(model.encode(chunk, show_progress_bar=False))
    return {probe: {name: util.cos_sim(vec, doc).item()
                    for name, doc in zip(columns, docs)}
            for probe, vec in zip(probes, vecs)}


class Scored:
    '''the scores for one (model, variant), plus the questions we ask of them.'''

    def __init__(self, model_name, variant, scores):
        self.model_name, self.variant, self.scores = model_name, variant, scores
        self.threshold = GAP[(model_name, variant)]

    def gap(self, probe, expected, rival):
        return self.scores[probe][expected] - self.scores[probe][rival]

    def top_column(self, probe):
        return max(self.scores[probe], key=self.scores[probe].get)

    def top_score(self, probe):
        return max(self.scores[probe].values())

    def clear_floor(self):
        '''the weakest clear probe. a refuse probe has to come in under this, or
        no score cutoff can separate the two.'''
        return min(self.top_score(p) for p, _, _, v in CASES if v == "clear")

    def predict(self, probe, expected, rival):
        '''
        the verdict the agent would reach from the scores alone -- the same
        decision the three assertions below check, written once so the printed
        table and the tests cannot disagree.

        note the floor is derived from the gold "clear" labels, so this is a
        diagnostic, not something deliberate.py could run at inference.
        '''
        if self.top_score(probe) < self.clear_floor():
            return "refuse"
        if abs(self.gap(probe, expected, rival)) >= self.threshold:
            return "clear"
        return "ambiguous"


@pytest.fixture(scope="session", params=MODELS, ids=MODELS)
def model(request):
    return request.param, load(request.param)


@pytest.fixture(scope="session", params=VARIANTS, ids=VARIANTS)
def scored(request, model):
    model_name, m = model
    return Scored(model_name, request.param,
                  score_all(m, request.param, model_name))


def cases(verdict):
    return [pytest.param(c, id=c[0]) for c in CASES if c[3] == verdict]


@pytest.mark.parametrize("case", cases("clear"))
def test_clear_probe_wins_decisively(case, scored):
    probe, expected, rival, _ = case
    gap = scored.gap(probe, expected, rival)
    assert gap > scored.threshold, (
        f"{probe!r}: {expected} beat {rival} by only {gap:+.3f}, under the "
        f"{scored.threshold} bar -- the agent would stop and ask about a probe "
        f"that should be unambiguous")


@pytest.mark.parametrize("case", cases("ambiguous"))
def test_ambiguous_probe_stays_close(case, scored):
    probe, expected, rival, _ = case
    gap = scored.gap(probe, expected, rival)
    assert abs(gap) < scored.threshold, (
        f"{probe!r}: {expected} vs {rival} split by {gap:+.3f}, over the "
        f"{scored.threshold} bar -- the agent would pick a grain the user "
        f"never specified instead of asking")


def ask_judge(tag, probe, column_a, column_b):
    '''one ollama call. returns (label, whatever followed it).'''
    reply = OpenAI(base_url=OLLAMA_URL, api_key="ollama").chat.completions.create(
        model=tag, temperature=0,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            query=probe, column_a=column_a, column_b=column_b)}])
    ## qwen3 thinks out loud, so keep only what follows the think block. a clear
    ## answer carries the column after the label, so split on the first space
    answer = reply.choices[0].message.content.lower().rsplit("</think>", 1)[-1]
    label, _, named = answer.replace(":", " ").strip().partition(" ")
    return label, named


def judge_cases():
    '''the CASES rows the judges run, in CASES order'''
    return [c for c in CASES if c[0] in JUDGE_PROBES]


def judge_all(tag, variant):
    '''
    probe -> the judge's verdict for one (judge, variant). a clear answer that
    names the wrong column is not clear. an unreachable ollama gives back
    None instead of taking the whole run down with it.
    '''
    template = VARIANTS[variant]
    verdicts = {}
    for probe, expected, rival, _ in tqdm(judge_cases(), desc=f"{tag} {variant}", leave=False):
        try:
            label, named = ask_judge(
                tag, probe,
                template.format(name=expected, desc=COLUMNS[expected]),
                template.format(name=rival, desc=COLUMNS[rival]))
        except Exception:
            return None       ## ollama is not up; caller drops this judge
        verdicts[probe] = label if label != "clear" or expected in named else "wrong-column"
    return verdicts


def spanned(table, groups):
    '''
    tabulate cannot merge header cells, so draw the spanning row by hand off the
    box characters it already laid down. groups is [(label, n_columns), ...]
    covering every column left to right.
    '''
    lines = table.split("\n")
    border = lines[0]                                   ## the top rule
    edges = [0] + [i for i, ch in enumerate(border) if ch == "\u252c"] + [len(border) - 1]

    bounds, col = [0], 0
    for _, n in groups:
        col += n
        bounds.append(col)

    top, label_row = "\u250c", "\u2502"
    for g, (name, _) in enumerate(groups):
        width = edges[bounds[g + 1]] - edges[bounds[g]] - 1
        top += "\u2500" * width + ("\u252c" if g < len(groups) - 1 else "\u2510")
        label_row += name.center(width) + "\u2502"

    ## the old top rule becomes the connector, with group boundaries crossed
    connector = list("\u251c" + border[1:-1] + "\u2524")
    for g in range(1, len(groups)):
        connector[edges[bounds[g]]] = "\u253c"

    return "\n".join([top, label_row, "".join(connector)] + lines[1:])


@pytest.fixture(scope="session", params=JUDGES, ids=JUDGES)
def judge(request):
    return JUDGES[request.param]


@pytest.mark.parametrize("case", [pytest.param(c, id=c[0]) for c in judge_cases()])
def test_judge_matches_gold(case, judge):
    probe, expected, rival, gold = case
    label, named = ask_judge(judge, probe, expected, rival)
    assert label == gold, (
        f"{probe!r} ({expected} vs {rival}): judge said {f'{label} {named}'.strip()!r}, "
        f"gold is {gold}")

    ## being decisive is not enough -- it has to be decisive about the right one
    if gold == "clear":
        assert expected in named, (
            f"{probe!r}: judge said clear but named {named.strip()!r}, "
            f"expected {expected}")


@pytest.mark.parametrize("case", cases("refuse"))
def test_refuse_probe_scores_under_the_clear_floor(case, scored):
    probe = case[0]
    floor, top = scored.clear_floor(), scored.top_score(probe)
    assert top < floor, (
        f"{probe!r} matched {scored.top_column(probe)} at {top:.3f}, at or above "
        f"the {floor:.3f} floor set by the weakest clear probe -- any cutoff that "
        f"refuses this also refuses a question we can actually answer")


if __name__ == "__main__":
    from tabulate import tabulate

    ## score every model once, keeping one Scored per (model, variant)
    scored = {}
    for model_name in MODELS:
        m = load(model_name)
        for variant in VARIANTS:
            scored[(model_name, variant)] = Scored(
                model_name, variant, score_all(m, variant, model_name))
        del m

    ## and one set of verdicts per (judge, variant). a judge we cannot reach is
    ## left out of the table entirely -- printing a column of misses for a server
    ## that was never asked would read as a result rather than an absence
    judged = {}
    for judge_name, tag in JUDGES.items():
        answers = {v: judge_all(tag, v) for v in VARIANTS}
        if any(a is None for a in answers.values()):
            print(f"skipping {judge_name}: nothing answering at {OLLAMA_URL}\n"
                  f"  start the server:  ollama serve\n"
                  f"  pull the model:    ollama pull {tag}")
        else:
            judged[judge_name] = answers

    ## groups drive the spanning header; the sub-headers carry no model name.
    ## every variant gets graded, so each one owns a verdict and an ok column --
    ## an embedder is name/n-vrd/n-ok/desc/d-vrd/d-ok, a judge's answer IS its
    ## verdict so it is just name/n-ok/desc/d-ok
    groups = ([("", 1), ("", 1)] + [(m, 6) for m in MODELS] + [(j, 4) for j in judged])
    headers = (["comparison", "gold"]
               + ["name", "n-vrd", "n-ok", "name+desc", "nd-vrd", "nd-ok"] * len(MODELS)
               + ["name", "n-ok", "name+desc", "nd-ok"] * len(judged))

    def mark(verdict, gold, first):
        '''ok/XX, but only on the first row of a case and only if there is a verdict'''
        return ("ok" if verdict == gold else "XX") if first and verdict else ""

    rows = []
    for probe, expected, rival, gold in CASES:
        for first, col in [(True, expected), (False, rival)]:
            row = [f"{probe} - {col}", gold if first else ""]
            for model_name in MODELS:
                name, desc = scored[(model_name, "name_only")], scored[(model_name, "name_and_desc")]
                nv = name.predict(probe, expected, rival)
                dv = desc.predict(probe, expected, rival)
                row += [round(name.scores[probe][col], 3), nv if first else "", mark(nv, gold, first),
                        round(desc.scores[probe][col], 3), dv if first else "", mark(dv, gold, first)]
            for judge_name, answers in judged.items():
                ## judges only run JUDGE_PROBES, so most rows have no verdict
                by_name = answers["name_only"].get(probe, "")
                by_desc = answers["name_and_desc"].get(probe, "")
                row += [by_name if first else "", mark(by_name, gold, first),
                        by_desc if first else "", mark(by_desc, gold, first)]
            rows.append(row)

    print(spanned(tabulate(rows, headers=headers, tablefmt="simple_outline"), groups))

    ## how often each config's verdict matched the gold label, split by gold
    def tally_row(name, variant, verdicts):
        right = {"clear": 0, "ambiguous": 0, "refuse": 0}
        total = {"clear": 0, "ambiguous": 0, "refuse": 0}
        ## judges cover only JUDGE_PROBES, so the denominator is whatever this
        ## config actually answered rather than a fixed len(CASES)
        for probe, _, _, gold in CASES:
            if probe not in verdicts:
                continue
            total[gold] += 1
            if verdicts[probe] == gold:
                right[gold] += 1
        return ([name, variant]
                + [f"{right[v]}/{total[v]}" for v in ("clear", "ambiguous", "refuse")]
                + [f"{sum(right.values())}/{sum(total.values())}"])

    tally = [tally_row(model_name, variant,
                       {p: s.predict(p, e, r) for p, e, r, _ in CASES})
             for (model_name, variant), s in scored.items()]

    tally += [tally_row(judge_name, variant, verdicts)
              for judge_name, answers in judged.items()
              for variant, verdicts in answers.items()]

    print()
    print(tabulate(tally, tablefmt="simple_outline",
                   headers=["model", "variant", "clear", "ambiguous", "refuse", "total"]))
