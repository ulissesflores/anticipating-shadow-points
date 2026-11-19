"""The papers quote the derived numbers, and none of the withdrawn claims.

``test_paper_numbers.py`` locks the numbers in the data; this file locks them
in the prose, so a paper cannot drift from ``output/results.json`` unnoticed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PAPER = Path(__file__).resolve().parent.parent / "paper"


def unit(value: float) -> str:
    """Format a value that cannot exceed 1 the APA 7 way: two decimals, no leading zero (.11)."""
    return f"{value:.2f}".removeprefix("0")


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
    assert "no measurable benefit" in paper
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
            assert f"{block['bits']:.2f} ({block['share'] * 100:.1f}%)" in note


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
    assert f"Jaccard of {unit(fx['e2_red_rate_limit_best_jaccard'])}" in paper
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
    assert f"precision {unit(cm['precision'])}, recall {unit(cm['recall'])}" in note


def test_iron_law_11_quotes_shares_and_conditional_rates(results):
    """Binary bits, May's Wilson interval and the decline share among exit-0 trials match."""
    note = text("graceful-refusals.md")
    jul = results["iron_law_11"]["july_2026"]
    d = jul["outcome_information"]["author"]["delivered"]
    assert f"{d['exit_code']['bits']:.2f} of {d['entropy_bits']:.2f} bits" in note
    lo, hi = results["iron_law_11"]["may_2026"]["detector_silent_refusals"]["wilson95"]
    assert (
        f"95% CI [{round(lo * 100)}, {round(hi * 100)}]" in note
    )  # APA 7 form since paper version 2.4
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
    assert f"from {unit(before)} to {unit(after)}" in paper
    w = fx["layer3_window_distinct_words"]
    assert f"{w['min']} to {w['max']} distinct content words (median {w['median']})" in paper
    n, short = fx["expected_points"], fx["expected_points_at_most_10_tokens"]
    assert f"{short} of the {n} expected points" in paper
    core = results["iron_law_11"]["july_2026"]["core_silent_refusals"]
    assert f"{core['k']} ({pct(core)})" in paper


def test_preprint_quotes_the_2026_11_study():
    """Section 5.5 quotes the study's numbers as ``results.json`` holds them."""
    import json

    study = json.loads((PAPER.parent / "benchmark/study-2026-11/results.json").read_text())
    gem, grok = study["gemini"], study["grok"]
    paper = " ".join(text("asp-preprint.md").split())
    for cond, pct in (("RED-plain", "56%"), ("RED-risk", "66%"), ("GREEN", "48%")):
        assert f"{gem['overall'][cond]:.0%}" == pct and pct in paper
    for cond, pct in (("RED-plain", "57%"), ("RED-risk", "70%"), ("GREEN", "54%")):
        assert f"{grok['overall'][cond]:.0%}" == pct and pct in paper
    assert f"−{unit(abs(gem['primary']['delta_bar']))} (primary judge)" in paper
    assert f"−{unit(abs(grok['primary']['delta_bar']))} (second judge)" in paper
    sec = gem["secondary"]["RED-risk - RED-plain"]
    sys.path.insert(0, str(PAPER / "tools"))
    from apa_stats import p_text  # APA 7, canon v1.6: "= .001", never "= 0.0014"

    assert f"+{unit(sec['delta_bar'])} (p {p_text(sec['p'])})" in paper
    assert "91.9% of 855 item decisions" in paper


EQUATIONS = (
    r"\[ \frac{p + \frac{z^{2}}{2n} \pm z\sqrt{\frac{p(1-p)}{n} + \frac{z^{2}}{4n^{2}}}}"
    r"{1 + \frac{z^{2}}{n}} \]",
    r"\[ H = -\sum_{i} p_{i} \log_{2} p_{i} \]",
    r"\[ \frac{I}{H} = \frac{H - H_{c}}{H} \]",
)


@pytest.mark.parametrize(
    "name",
    [
        "graceful-refusals.md",
        *(f"i18n/graceful-refusals.{lang}.md" for lang in ("pt-BR", "es", "it")),
    ],
)
def test_iron_law_11_prints_the_same_three_equations_in_every_edition(name):
    """Equations 1 to 3 are the same symbols, each alone on its line, in the four sources."""
    lines = text(name).splitlines()
    assert [line for line in lines if line.startswith(r"\[")] == list(EQUATIONS)


def test_iron_law_11_equations_give_the_sealed_numbers(results):
    """Equations 1 to 3, computed as printed from the sealed counts, give the sealed numbers."""
    from math import log2, sqrt

    jul = results["iron_law_11"]["july_2026"]

    def entropy(counts):
        """Equation 2: entropy in bits of a table of counts."""
        return -sum(c / sum(counts) * log2(c / sum(counts)) for c in counts if c)

    z = 1.959963984540054  # the 97.5th percentile of the normal curve, printed as 1.96
    for reading in ("author", "codebook", "core", "detector"):
        block = jul[f"{reading}_silent_refusals"]
        n, p = block["n"], block["k"] / block["n"]
        centre, half = p + z**2 / (2 * n), z * sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
        limits = [(centre + sign * half) / (1 + z**2 / n) for sign in (-1, 1)]  # Equation 1
        assert [round(x, 4) for x in limits] == block["wilson95"]
    for labels in ("author", "codebook"):
        info = jul["outcome_information"][labels]
        n = info["outcomes"]
        total = sum(n.values())
        h = entropy(n.values())
        assert round(h, 4) == info["entropy_bits"]
        # the exit code makes two groups: exit 1 (cut, blocked) and exit 0 (declined, done)
        groups = [[n["cut"], n["blocked"]], [n["declined"], n["done"]]]
        h_c = sum(sum(g) / total * entropy(g) for g in groups)
        assert round((h - h_c) / h, 4) == info["exit_code"]["share"]  # Equation 3
        # stop_reason adds the split of cut from blocked; declined and done stay together
        h_c = (n["declined"] + n["done"]) / total * entropy(groups[1])
        assert round((h - h_c) / h, 4) == info["exit_code_and_stop_reason"]["share"]
        assert round(h_c, 4) == info["residual_bits"]


def test_preprint_prints_the_jaccard_the_matcher_computes():
    """Equation 1 of the preprint is the score of layer 3, with the threshold the text gives."""
    sys.path.insert(0, str(PAPER.parent / "benchmark" / "src"))
    from asp_benchmark.adjudicator import JACCARD_THRESHOLD, _jaccard

    equation = r"\[ J = \frac{|A \cap B|}{|A \cup B|} \]"
    for name in ("asp-preprint.md", *(f"i18n/asp-preprint.{x}.md" for x in ("pt-BR", "es", "it"))):
        assert [ln for ln in text(name).splitlines() if ln.startswith(r"\[")] == [equation], name
    a, b = {"rate", "limit", "retry", "logs"}, {"rate", "limit", "backoff"}
    assert _jaccard(a, b) == len(a & b) / len(a | b) == 2 / 5
    assert JACCARD_THRESHOLD == 0.30
    assert "A match needs a score of at least .30." in text("asp-preprint.md")
