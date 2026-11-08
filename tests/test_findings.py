"""Every number in ``docs/findings.md``, checked against the derived results."""

from __future__ import annotations

from pathlib import Path

FINDINGS = (Path(__file__).resolve().parents[1] / "docs" / "findings.md").read_text(
    encoding="utf-8"
)


def pct(rate: float) -> str:
    """Format a rate as a whole percentage.

    Parameters
    ----------
    rate : float
        A share between 0 and 1.

    Returns
    -------
    str
        For example ``"40%"``.
    """
    return f"{round(rate * 100)}%"


def test_exit_code_table(results):
    """The July 2026 table quotes the derived counts, rates, interval and information share."""
    jul = results["iron_law_11"]["july_2026"]
    lo, hi = jul["author_silent_refusals"]["wilson95"]
    assert f"{jul['exit0']} of {jul['n']}, all with `stop_reason: end_turn`" in FINDINGS
    assert jul["exit0_stop_reasons"] == {"end_turn": jul["exit0"]}
    assert (
        f"{jul['declines_given_exit0']['author'].replace('/', ' of ')} ({pct(0.4)} of the suite"
        in FINDINGS
    )
    assert jul["author_silent_refusals"]["rate"] == 0.4
    assert f"95% Wilson CI {pct(lo)[:-1]}–{pct(hi)}" in FINDINGS
    given = {k: v.replace("/", " of ") for k, v in jul["declines_given_exit0"].items()}
    codebook, core = jul["codebook_silent_refusals"]["rate"], jul["core_silent_refusals"]["rate"]
    detector = jul["detector_silent_refusals"]
    assert f"{given['codebook']} ({pct(codebook)})" in FINDINGS
    assert f"{given['core']} ({pct(core)})" in FINDINGS
    assert f"{detector['k']} ({pct(detector['rate'])})" in FINDINGS
    info = jul["outcome_information"]["author"]["delivered"]
    bits, total, share = info["exit_code"]["bits"], info["entropy_bits"], info["exit_code"]["share"]
    assert f"{bits:.2f} of {total:.2f} bits ({share * 100:.1f}%)" in FINDINGS


def test_may_snapshot(results):
    """The May 2026 comparison quotes the locked detector's count."""
    may = results["iron_law_11"]["may_2026"]
    k, n = may["detector_silent_refusals"]["k"], may["n"]
    assert f"gave {k} of {n} ({pct(may['detector_silent_refusals']['rate'])})" in FINDINGS
    assert f"Claude Code {may['claude_code_version']}, Opus 4.7" in FINDINGS


def test_benchmark_and_matcher(results):
    """The fixture-check means and the matcher sensitivity figures."""
    fx = results["adjudicator_fixture_check_2026_05"]
    assert f"GREEN {pct(fx['green_mean'])} and RED {pct(fx['red_mean'])}" in FINDINGS
    moved = fx["tail_fix_moved_best_jaccard"]
    assert f"best score of {len(moved)} expected points" in FINDINGS
    assert all(after < 0.30 for _, after in moved.values())
    assert (
        f"{fx['expected_points_at_most_10_tokens']} of the {fx['expected_points']} expected points"
        in FINDINGS
    )
