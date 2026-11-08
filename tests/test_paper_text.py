"""The papers quote the derived numbers, and none of the withdrawn claims.

``test_paper_numbers.py`` locks the numbers in the data; this file locks them
in the prose, so a paper cannot drift from ``output/results.json`` unnoticed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PAPER = Path(__file__).resolve().parent.parent / "paper"


def text(name: str) -> str:
    """Return a paper's Markdown source.

    Parameters
    ----------
    name : str
        File name inside ``paper/``.

    Returns
    -------
    str
        The file contents.
    """
    return (PAPER / name).read_text(encoding="utf-8")


def pct(block: dict) -> str:
    """Format a derived rate as the papers write it, e.g. ``40%``.

    Parameters
    ----------
    block : dict
        A ``*_silent_refusals`` block from the results.

    Returns
    -------
    str
        Whole-number percentage with a percent sign.
    """
    return f"{round(block['rate'] * 100)}%"


def test_iron_law_11_quotes_every_july_reading(results):
    """Each July reading appears in the note as ``k/50`` and as a percentage."""
    note = text("graceful-refusals.md")
    jul = results["iron_law_11"]["july_2026"]
    for reading in ("author", "codebook", "core", "detector"):
        block = jul[f"{reading}_silent_refusals"]
        assert f"{block['k']}/50" in note
        assert pct(block) in note


def test_iron_law_11_quotes_may_and_the_fair_comparison(results):
    """May's detector count and the like-for-like 60% versus 18% are stated."""
    note = text("graceful-refusals.md")
    may = results["iron_law_11"]["may_2026"]["detector_silent_refusals"]
    jul = results["iron_law_11"]["july_2026"]["detector_silent_refusals"]
    assert f"{may['k']}/50" in note
    assert f"{pct(may)} versus {pct(jul)}" in note


@pytest.mark.parametrize("name", ["graceful-refusals.md", "asp-preprint.md"])
def test_july_model_attribution(name):
    """Both papers name Fable 5 as the July session model."""
    assert "Fable 5" in text(name)


def test_preprint_labels_the_benchmark_as_mock():
    """The preprint calls the benchmark run mock and its texts fixtures."""
    paper = text("asp-preprint.md")
    assert "mock-mode" in paper
    assert "no measured effect" in paper
    assert "ten candidate transcripts in total" not in paper


def test_no_invented_issue_title():
    """The withdrawn title for anthropics/claude-code #15685 is gone."""
    assert "Exit code 0 when the agent refused to work" not in text("graceful-refusals.md")


def test_iron_law_11_quotes_outcome_information(results):
    """Table 3 quotes the information shares the data give."""
    note = text("graceful-refusals.md")
    info = results["iron_law_11"]["july_2026"]["outcome_information"]
    for labels in ("author", "codebook"):
        for channel in ("exit_code", "exit_code_and_stop_reason"):
            block = info[labels][channel]
            assert f"{block['bits']:.2f} ({round(block['share'] * 100)}%)" in note


def test_preprint_quotes_fixture_and_companion_numbers(results):
    """The preprint's instrument-check and companion numbers match the data."""
    paper = text("asp-preprint.md")
    fx = results["adjudicator_fixture_check_2026_05"]
    assert f"RED {round(fx['red_mean'] * 100)}% and GREEN {round(fx['green_mean'] * 100)}%" in paper
    assert f"{fx['permutation_offdiagonal_mean'] * 100:.1f}% (largest off-task cell" in paper
    assert f"cell {round(fx['permutation_offdiagonal_max'] * 100)}%" in paper
    assert f"every one of the {fx['matches_by_layer']['exact_name']} matches" in paper
    jul = results["iron_law_11"]["july_2026"]
    for reading in ("author", "codebook", "detector"):
        assert pct(jul[f"{reading}_silent_refusals"]) in paper
    lo, hi = jul["author_silent_refusals"]["wilson95"]
    assert f"{round(lo * 100)}–{round(hi * 100)}%" in paper


def test_preprint_quotes_overlap_and_rater_agreement(results):
    """The 0.11 window overlap and the four identical raters appear as derived."""
    paper = text("asp-preprint.md")
    fx = results["adjudicator_fixture_check_2026_05"]
    assert f"Jaccard of {fx['e2_red_rate_limit_best_jaccard']:.2f}" in paper
    identical = results["iron_law_11"]["july_2026"]["raters_identical_to_r1"]
    assert {4: "four"}[identical] + " of which returned identical labels" in paper


def test_iron_law_11_quotes_secondary_counts(results):
    """Conditional decline counts, Opus 4.8 exit-0 trials and May confusion appear as derived."""
    note = text("graceful-refusals.md")
    jul = results["iron_law_11"]["july_2026"]
    a, n = jul["declines_given_exit0"]["author"].split("/")
    assert f"of the {n} trials that exit 0, {a} are declines" in note
    o = jul["opus_48_exit0"]
    assert f"Opus 4.8 on {o['trials']} exit-0 trials, {o['author_declines']} of which" in note
    cm = results["iron_law_11"]["may_2026"]["lock_file_confusion"]
    assert f"{cm['false_alarm']} false alarms are {cm['false_alarm_turn_cap']} turn-cap" in note
    assert f"precision {cm['precision']:.2f}, recall {cm['recall']:.2f}" in note


def test_iron_law_11_quotes_shares_and_conditional_rates(results):
    """Binary bits, May's Wilson interval and the decline share among exit-0 trials match."""
    note = text("graceful-refusals.md")
    jul = results["iron_law_11"]["july_2026"]
    d = jul["outcome_information"]["author"]["delivered"]
    assert f"{d['exit_code']['bits']:.2f} of {d['entropy_bits']:.2f} bits" in note
    lo, hi = results["iron_law_11"]["may_2026"]["detector_silent_refusals"]["wilson95"]
    assert f"{round(lo * 100)}–{round(hi * 100)}%" in note
    for key in ("author", "codebook", "core"):
        k, n = map(int, jul["declines_given_exit0"][key].split("/"))
        assert f"({round(100 * k / n)}%)" in note


def test_iron_law_11_quotes_one_decimal_shares(results):
    """The residual and binary shares appear with one decimal, as derived."""
    note = text("graceful-refusals.md")
    info = results["iron_law_11"]["july_2026"]["outcome_information"]
    residual = 100 * (1 - info["author"]["exit_code_and_stop_reason"]["share"])
    assert f"residual {residual:.1f}% of the outcome" in note
    for labels in ("author", "codebook"):
        share = 100 * info[labels]["delivered"]["exit_code"]["share"]
        assert f"{share:.1f}%" in note


def test_preprint_quotes_layer3_numbers(results):
    """The tail-fix, window-size and short-point numbers of Section 5.3 match the data."""
    paper = " ".join(text("asp-preprint.md").split())
    fx = results["adjudicator_fixture_check_2026_05"]
    moved = fx["tail_fix_moved_best_jaccard"]
    assert {3: "three"}[len(moved)] + " unmatched points" in paper
    before, after = moved["RED/E2/Observability / logs"]
    assert f"from {before:.2f} to {after:.2f}" in paper
    w = fx["layer3_window_distinct_words"]
    assert f"{w['min']} to {w['max']} distinct content words (median {w['median']})" in paper
    n, short = fx["expected_points"], fx["expected_points_at_most_10_tokens"]
    assert f"{short} of the {n} expected points" in paper
    core = results["iron_law_11"]["july_2026"]["core_silent_refusals"]
    assert f"{core['k']} ({pct(core)})" in paper
