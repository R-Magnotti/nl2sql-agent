'''
the prompted half of the eval: ask a generative model to label the column pair
instead of scoring it.

embedders and judges both run all 41 cases, so the two halves of the table are
scored on the same rows. the embedders get there on a couple of batched forward
passes; a judge pays one ollama call per case, which is
len(CASES) x len(VARIANTS) x len(JUDGES) round trips for a full run.
'''
import json
import re

from openai import OpenAI
from tqdm import tqdm

from evals import dataset
from evals.config import JUDGE_PROMPT, OLLAMA_URL, RAW_LOG, RESULTS_DIR
from evals.dataset import CASES, VARIANTS

JUDGES = {
    "prompt-qwen3-0.6b":    "qwen3:0.6b",
    "prompt-qwen3-4b":      "qwen3:4b",
    "prompt-qwen3-4b-inst": "qwen3:4b-instruct",
    "prompt-gemma3-4b":     "gemma3:4b",
}

## every judge reply is kept verbatim alongside what the parser made of it. the
## parser is lossy -- a reply the table scores as wrong may have been a perfectly
## good answer in a shape `partition` could not read -- so the raw text is the
## only way to tell a bad judge from a bad parse.
RAW = []


## the models are asked for a bare label and mostly comply, but not always:
## qwen3:4b answers "CLEAR\ncolumn" or writes a paragraph ending "**Answer:**
## CLEAR: column". splitting on the first space read those as "clear\ncolumn" and
## "the", scoring 8 correct answers wrong. matching the label as a word instead
## costs nothing and does not care what surrounds it -- 319 of 328 replies name
## exactly one label, so there is nothing to disambiguate.
LABEL = re.compile(r"\b(clear|ambiguous|refuse)\b")


def parse_reply(raw):
    '''
    (label, the text it was found in) for one reply. the same function grades a
    live call and a reply replayed out of RAW_LOG, so the log can never drift
    from what the table says about it.

    an empty label means the model said nothing usable -- qwen3:0.6b returns a
    genuinely empty string a handful of times, which no amount of parsing fixes.
    '''
    body = raw.lower().rsplit("</think>", 1)[-1]   ## qwen3 thinks out loud; drop it
    found = LABEL.search(body)
    return (found.group(1) if found else ""), body


def ask_judge(tag, probe, column_a, column_b):
    '''one ollama call. returns (label, the text it was found in, reply verbatim).'''
    reply = OpenAI(base_url=OLLAMA_URL, api_key="ollama").chat.completions.create(
        model=tag, temperature=0,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(
            query=probe, column_a=column_a, column_b=column_b)}])
    raw = reply.choices[0].message.content
    label, named = parse_reply(raw)
    return label, named, raw


def judge_all(tag, variant):
    '''
    probe -> the judge's verdict for one (judge, variant). a clear answer that
    names the wrong column is not clear. an unreachable ollama gives back
    None instead of taking the whole run down with it.
    '''
    verdicts = {}
    for probe, expected, rival, gold in tqdm(CASES, desc=f"{tag} {variant}", leave=False):
        column_a = dataset.render(expected, variant)
        column_b = dataset.render(rival, variant)
        try:
            label, named, raw = ask_judge(tag, probe, column_a, column_b)
        except Exception:
            return None       ## ollama is not up; caller drops this judge
        verdicts[probe] = label if label != "clear" or expected in named else "wrong-column"
        RAW.append({"model": tag, "variant": variant, "probe": probe,
                    "expected": expected, "rival": rival, "gold": gold,
                    "column_a": column_a, "column_b": column_b,
                    "raw": raw,
                    "parsed_label": label, "parsed_named": named,
                    "recorded_verdict": verdicts[probe],
                    "scored_correct": verdicts[probe] == gold})
    return verdicts


def judge_everything():
    '''
    one set of verdicts per (judge, variant). a judge we cannot reach is left out
    entirely -- printing a column of misses for a server that was never asked
    would read as a result rather than an absence.
    '''
    judged = {}
    for judge_name, tag in JUDGES.items():
        answers = {v: judge_all(tag, v) for v in VARIANTS}
        if any(a is None for a in answers.values()):
            print(f"skipping {judge_name}: nothing answering at {OLLAMA_URL}\n"
                  f"  start the server:  ollama serve\n"
                  f"  pull the model:    ollama pull {tag}")
        else:
            judged[judge_name] = answers
        dump_raw()            ## after each judge, so a run that dies keeps what it asked
    return judged


def replay_raw():
    '''
    the verdicts a finished run would have produced under the CURRENT parser,
    read back out of RAW_LOG instead of asking ollama again. every stored reply
    is re-parsed and its derived fields rewritten in place, so the log never
    disagrees with the table built from it.

    this is what makes a parser change cheap: the replies are the expensive part
    and they are already on disk.
    '''
    log = json.loads(RAW_LOG.read_text())
    by_tag = {tag: name for name, tag in JUDGES.items()}
    judged, changed = {}, 0
    for r in log["records"]:
        label, named = parse_reply(r["raw"])
        verdict = label if label != "clear" or r["expected"] in named else "wrong-column"
        changed += verdict != r["recorded_verdict"]
        r["parsed_label"], r["parsed_named"] = label, named
        r["recorded_verdict"], r["scored_correct"] = verdict, verdict == r["gold"]
        judged.setdefault(by_tag[r["model"]], {}).setdefault(r["variant"], {})[r["probe"]] = verdict
    RAW_LOG.write_text(json.dumps(log, indent=2))
    print(f"replayed {len(log['records'])} stored replies, {changed} verdicts changed")
    return judged


def dump_raw():
    '''written after each judge, so a run that dies keeps what it already asked'''
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_LOG.write_text(json.dumps(
        {"judges": JUDGES, "variants": VARIANTS, "judge_prompt": JUDGE_PROMPT,
         "records": RAW}, indent=2))
