'''
retrieval eval: can an embedding lookup tell "answer it" from "ask about it"?

    pytest evals -v                  ## gold verdicts as pass/fail
    pytest evals -v -k name_only
    python -m evals.report           ## the same scores as a raw matrix

each case in dataset.CASES carries a gold verdict, and each verdict gets its own
assertion:
  clear      the gap must be wide    -> agent proceeds with expected_top
  ambiguous  the gap must be narrow  -> agent asks the user which grain they meant
  refuse     nothing in the schema answers this, so its top score must come in
             under the weakest clear probe -- otherwise no cutoff can refuse it
             without also refusing a legitimate question

these are graded against thresholds fitted on these same cases (see config.GAP),
so a green run means "nothing moved", not "the model generalises".
'''
import pytest

from evals import dataset
from evals.judging import ask_judge


def params(verdict=None):
    '''the gold rows for one verdict as pytest params, each id'd by its probe'''
    return [pytest.param(c, id=c[0]) for c in dataset.cases(verdict)]


@pytest.mark.parametrize("case", params("clear"))
def test_clear_probe_wins_decisively(case, scored):
    probe, expected, rival, _ = case
    gap = scored.gap(probe, expected, rival)
    assert gap > scored.threshold, (
        f"{probe!r}: {expected} beat {rival} by only {gap:+.3f}, under the "
        f"{scored.threshold} bar -- the agent would stop and ask about a probe "
        f"that should be unambiguous")


@pytest.mark.parametrize("case", params("ambiguous"))
def test_ambiguous_probe_stays_close(case, scored):
    probe, expected, rival, _ = case
    gap = scored.gap(probe, expected, rival)
    assert abs(gap) < scored.threshold, (
        f"{probe!r}: {expected} vs {rival} split by {gap:+.3f}, over the "
        f"{scored.threshold} bar -- the agent would pick a grain the user "
        f"never specified instead of asking")


@pytest.mark.parametrize("case", params("refuse"))
def test_refuse_probe_scores_under_the_clear_floor(case, scored):
    probe = case[0]
    floor, top = scored.clear_floor(), scored.top_score(probe)
    assert top < floor, (
        f"{probe!r} matched {scored.top_column(probe)} at {top:.3f}, at or above "
        f"the {floor:.3f} floor set by the weakest clear probe -- any cutoff that "
        f"refuses this also refuses a question we can actually answer")


@pytest.mark.parametrize("case", params())
def test_judge_matches_gold(case, judge):
    probe, expected, rival, gold = case
    label, named, _ = ask_judge(judge, probe, expected, rival)
    assert label == gold, (
        f"{probe!r} ({expected} vs {rival}): judge said {f'{label} {named}'.strip()!r}, "
        f"gold is {gold}")

    ## being decisive is not enough -- it has to be decisive about the right one
    if gold == "clear":
        assert expected in named, (
            f"{probe!r}: judge said clear but named {named.strip()!r}, "
            f"expected {expected}")
