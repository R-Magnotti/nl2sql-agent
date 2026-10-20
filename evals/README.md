# evals

Model-quality evals, kept apart from `tests/`. The two answer different questions:

| | `tests/` | `evals/` |
| --- | --- | --- |
| asks | is the code still correct | which model should the agent use |
| costs | seconds, no downloads | ~11GB of weights, hundreds of ollama calls |
| runs | every `pytest` | only when asked: `pytest evals` |
| output | pass/fail | a table someone reads |

## Retrieval: clear / ambiguous / refuse

Given a term from a user's question, pick the warehouse column that answers it —
or say that two readings are equally valid and the agent should ask, or that
nothing in the schema answers it at all. Two families compete over the same 41
cases: embedding lookup scored on cosine gaps, and prompted judges labelling the
column pair directly. The call this produced is written up in
[DECISIONS.md](../DECISIONS.md).

```bash
pytest evals -v                  ## gold verdicts as pass/fail
pytest evals -v -k name_only     ## one variant
pytest evals -v -k minilm        ## one model
python -m evals.report           ## the same scores as a table
```

`python -m evals.report` needs `ollama serve`; judges it cannot reach are left
out of the table with a message, and the embedding half still runs. The embedding
scores are cached in `results/embed_scores.json`, keyed on everything the
encoding depends on, so a second run loads no weights at all.

**These are regression gates, not accuracy estimates.** The `GAP` thresholds in
`config.py` and the `clear_floor` cutoff are fitted on the same 41 cases they are
then graded on. A green run means nothing moved.

## Layout

| file | holds |
| --- | --- |
| `dataset.py` | the gold set: columns, the 41 probes, the verdict each deserves |
| `config.py` | fitted thresholds, prompts, paths — the knobs, no imports |
| `embedding.py` | the embedder half: score, cache, read a verdict off the gap |
| `judging.py` | the prompted half: one ollama call per case, replies kept raw |
| `test_retrieval.py` | one assertion per gold verdict |
| `report.py` | the whole thing as a table |
| `gold_questions.md` | verified end-to-end Q→answer pairs (harness still to come) |

## Artifacts

`results/` is regenerated every run and gitignored:

- `embed_scores.json` — the cosine cache, keyed by model source, dataset and device
- `judge_raw.json` — every judge reply verbatim next to what the parser made of
  it. The parser is lossy, so this is the only way to tell a bad judge from a
  bad parse.

`reports/` holds captured runs, committed as reference points to diff against:

- `test_retrieval_out_baseline.txt` — the run the later ones are compared against
- `test_retrieval_out.txt` — the current reference table
- `test_retrieval_out.txt.raw` / `.clean.txt` — the same capture with and without
  the progress-bar noise a terminal leaves behind
