'''
the eval as a table rather than as pass/fail:

    python -m evals.report

every model and judge against every case, scores and verdicts side by side, then
a tally of how often each config agreed with the gold label. captured runs live
in evals/reports/ -- diff a fresh one against those to see what moved.
'''
import sys

from tabulate import tabulate

from evals.config import RAW_LOG
from evals.dataset import CASES, VERDICTS
from evals.embedding import MODELS, score_everything
from evals.judging import RAW, judge_everything, replay_raw


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


def mark(verdict, gold, first):
    '''ok/XX, but only on the first row of a case and only if there is a verdict'''
    return ("ok" if verdict == gold else "XX") if first and verdict else ""


def matrix(scored, judged):
    '''
    the wide table: two rows per case, one per column in the pair.

    groups drive the spanning header; the sub-headers carry no model name.
    every variant gets graded, so each one owns a verdict and an ok column --
    an embedder is name/n-vrd/n-ok/desc/d-vrd/d-ok, a judge's answer IS its
    verdict so it is just name/n-ok/desc/d-ok
    '''
    groups = ([("", 1), ("", 1)] + [(m, 6) for m in MODELS] + [(j, 4) for j in judged])
    headers = (["comparison", "gold"]
               + ["name", "n-vrd", "n-ok", "name+desc", "nd-vrd", "nd-ok"] * len(MODELS)
               + ["name", "n-ok", "name+desc", "nd-ok"] * len(judged))

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
                by_name = answers["name_only"][probe]
                by_desc = answers["name_and_desc"][probe]
                row += [by_name if first else "", mark(by_name, gold, first),
                        by_desc if first else "", mark(by_desc, gold, first)]
            rows.append(row)

    return spanned(tabulate(rows, headers=headers, tablefmt="simple_outline"), groups)


def tally_row(name, variant, verdicts):
    '''how often one config's verdict matched the gold label, split by gold'''
    right = dict.fromkeys(VERDICTS, 0)
    total = dict.fromkeys(VERDICTS, 0)
    ## every config answers every case, so all six denominators agree
    for probe, _, _, gold in CASES:
        total[gold] += 1
        if verdicts[probe] == gold:
            right[gold] += 1
    return ([name, variant]
            + [f"{right[v]}/{total[v]}" for v in VERDICTS]
            + [f"{sum(right.values())}/{sum(total.values())}"])


def tally(scored, judged):
    rows = [tally_row(model_name, variant,
                      {p: s.predict(p, e, r) for p, e, r, _ in CASES})
            for (model_name, variant), s in scored.items()]
    rows += [tally_row(judge_name, variant, verdicts)
             for judge_name, answers in judged.items()
             for variant, verdicts in answers.items()]
    return tabulate(rows, tablefmt="simple_outline",
                    headers=["model", "variant", *VERDICTS, "total"])


def main(replay=False):
    '''
    --replay rebuilds the table from evals/results/ alone: cached scores, and the
    stored judge replies re-parsed by the current parser. no ollama, no embedder,
    no GPU. use it after changing the parser or a GAP threshold.
    '''
    scored = score_everything(verbose=True)
    judged = replay_raw() if replay else judge_everything()
    if not replay:
        print(f"raw judge replies -> {RAW_LOG} ({len(RAW)} calls)")
    print(matrix(scored, judged))
    print()
    print(tally(scored, judged))


if __name__ == "__main__":
    main(replay="--replay" in sys.argv)
