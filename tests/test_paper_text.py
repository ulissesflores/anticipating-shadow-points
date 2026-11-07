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
    note = text("iron-law-11.md")
    jul = results["iron_law_11"]["july_2026"]
    for reading in ("author", "codebook", "core", "detector"):
        block = jul[f"{reading}_silent_refusals"]
        assert f"{block['k']}/50" in note
        assert pct(block) in note


def test_iron_law_11_quotes_may_and_the_fair_comparison(results):
    """May's detector count and the like-for-like 60% versus 18% are stated."""
    note = text("iron-law-11.md")
    may = results["iron_law_11"]["may_2026"]["detector_silent_refusals"]
    jul = results["iron_law_11"]["july_2026"]["detector_silent_refusals"]
    assert f"{may['k']}/50" in note
    assert f"{pct(may)} versus {pct(jul)}" in note


@pytest.mark.parametrize("name", ["iron-law-11.md", "asp-preprint.md"])
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
    assert "Exit code 0 when the agent refused to work" not in text("iron-law-11.md")
