'''
the embedding half of the eval: score every (probe, column) pair with a
sentence-transformers model, cache the result, and read a verdict off the gap.

nothing here is stateful beyond the on-disk score cache, so a caller can hold
one Scored per (model, variant) and ask it questions.
'''
import hashlib
import inspect
import json

import torch
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm

from evals import dataset
from evals.config import BATCH, GAP, QUERY_PROMPT, RESULTS_DIR, SCORES_LOG
from evals.dataset import CASES, COLUMNS, VARIANTS

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
    columns = {name: dataset.render(name, variant) for name in COLUMNS}
    probes = dataset.probes()
    bar = f"{label} {variant}".strip()

    docs = model.encode(list(columns.values()), show_progress_bar=False)
    vecs = []
    for chunk in in_batches(probes, bar):
        vecs.extend(model.encode(chunk, show_progress_bar=False))
    return {probe: {name: util.cos_sim(vec, doc).item()
                    for name, doc in zip(columns, docs)}
            for probe, vec in zip(probes, vecs)}


## the scores are just floats, and nothing about them changes between runs unless
## an input to the encoding does. so cache them and the embedders never load at
## all -- which is also why there is no VRAM to hand back: an 8GB bf16 embedder
## and a 3.3GB judge do not have to share a 12GB card if only one of them exists.
def score_key(model_name, variant):
    '''
    everything the encoding depends on, and nothing else. GAP is absent on
    purpose -- it is applied after scoring, so retuning it must not invalidate
    a cache entry. the device is present because bf16 on CUDA and on MPS do not
    produce the same cosines.

    the MODELS block above is hashed by its source text, so reformatting it
    invalidates every entry even when the models are identical -- worth ~11GB of
    downloads, so leave it alone unless a model really changed.
    '''
    return hashlib.sha256(json.dumps([
        inspect.getsource(MODELS[model_name]),   ## catches a changed repo id or dtype
        VARIANTS[variant], COLUMNS, dataset.probes(), QUERY_PROMPT,
        "cuda" if torch.cuda.is_available() else "cpu",
    ], sort_keys=True).encode()).hexdigest()[:16]


def read_scores():
    return json.loads(SCORES_LOG.read_text()) if SCORES_LOG.exists() else {}


def write_scores(cache):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SCORES_LOG.write_text(json.dumps(cache, indent=2))


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
        decision the assertions in test_retrieval.py check, written once so the
        printed table and the tests cannot disagree.

        note the floor is derived from the gold "clear" labels, so this is a
        diagnostic, not something agent/deliberate.py could run at inference.
        '''
        if self.top_score(probe) < self.clear_floor():
            return "refuse"
        if abs(self.gap(probe, expected, rival)) >= self.threshold:
            return "clear"
        return "ambiguous"


def score_everything(cache=None, verbose=False):
    '''
    a Scored per (model, variant), scoring only what the cache cannot answer.
    a model whose scores are all cached is never built, so it costs no VRAM and
    no time.
    '''
    cache = read_scores() if cache is None else cache
    scored = {}
    for model_name in MODELS:
        stale = [v for v in VARIANTS
                 if cache.get(f"{model_name}|{v}", {}).get("key") != score_key(model_name, v)]
        if stale:
            m = load(model_name)
            for variant in stale:
                cache[f"{model_name}|{variant}"] = {
                    "key": score_key(model_name, variant),
                    "scores": score_all(m, variant, model_name)}
            del m
            write_scores(cache)
        elif verbose:
            print(f"{model_name}: cached, not loaded")
        for variant in VARIANTS:
            scored[(model_name, variant)] = Scored(
                model_name, variant, cache[f"{model_name}|{variant}"]["scores"])
    return scored

