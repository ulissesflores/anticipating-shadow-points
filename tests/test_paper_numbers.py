"""Every number the two papers cite, as an assertion on the derived results.

If code or data drift, these fail before a paper can quote a stale figure.
Sources: ``paper/iron-law-11.md`` sections 3-4 and ``paper/asp-preprint.md``
section 5 (where the benchmark figures are an instrument check on constructed
fixtures, not a measurement of ASP).
"""

from __future__ import annotations

import pytest


def il11(results: dict, run: str) -> dict:
    """Return one Iron Law 11 run block.

    Parameters
    ----------
    results : dict
        Results document.
    run : str
        ``"may_2026"`` or ``"july_2026"``.

    Returns
    -------
    dict
        The run block.
    """
    return results["iron_law_11"][run]


def test_may_detector_rate_is_60_percent(results):
    """May 2026, locked phrase detector: 30/50 = 60%."""
    may = il11(results, "may_2026")
    assert may["detector_silent_refusals"]["k"] == 30
    assert may["n"] == 50
    assert may["model"] == "claude-opus-4-7"
    assert may["claude_code_version"] == "2.1.143"


def test_july_split_and_signal(results):
    """July 2026: 24 exit 0 / 26 exit 1, every exit 0 is ``end_turn``."""
    jul = il11(results, "july_2026")
    assert (jul["n"], jul["exit0"], jul["exit1"]) == (50, 24, 26)
    assert jul["exit0_stop_reasons"] == {"end_turn": 24}
    assert jul["stop_reasons"] == {"end_turn": 24, "refusal": 1, "tool_use": 25}


def test_secondary_counts(results):
    """May exit 0 = 36; July reported cost USD 10.24; two replies redacted."""
    assert results["iron_law_11"]["may_2026"]["exit0"] == 36
    assert results["iron_law_11"]["july_2026"]["total_cost_usd"] == 10.24
    assert results["iron_law_11"]["july_2026"]["redacted_replies"] == 2


def test_july_model_mix(results):
    """July 2026 ran on Fable 5; all safety prompts were answered by Opus 4.8."""
    jul = il11(results, "july_2026")
    assert jul["claude_code_version"] == ["2.1.200"]
    assert jul["session_model"] == ["claude-fable-5"]
    assert jul["answering_models"] == {"claude-fable-5": 34, "claude-opus-4-8": 16}
    assert jul["safety_answering_models"] == {"claude-opus-4-8": 12}


@pytest.mark.parametrize(
    ("reading", "k", "wilson"),
    [
        ("author", 20, [0.2761, 0.5382]),
        ("codebook", 19, [0.2586, 0.5185]),
        ("core", 12, [0.143, 0.3741]),
        ("detector", 9, [0.0977, 0.308]),
    ],
)
def test_july_silent_refusal_readings(results, reading, k, wilson):
    """The four July readings: 40% author, 38% codebook, 24% core, 18% detector."""
    block = il11(results, "july_2026")[f"{reading}_silent_refusals"]
    assert block["k"] == k
    assert block["n"] == 50
    assert block["wilson95"] == wilson


def test_july_class_counts(results):
    """Adjudicated classes sum to 50 and match the paper's breakdown."""
    assert il11(results, "july_2026")["classes"] == {
        "destructive_refusal": 1,
        "impossible_decline": 8,
        "legit_completion": 4,
        "safety_refusal": 11,
        "server_block": 1,
        "turn_cap": 25,
    }


def test_fixture_check_is_labelled_mock(results):
    """The published benchmark run is a mock run over constructed fixtures."""
    check = results["adjudicator_fixture_check_2026_05"]
    assert check["run_mode"] == "mock"
    assert "not model outputs" in check["texts_are"]


def test_fixture_check_red_green(results):
    """Adjudicator on the constructed fixtures: RED mean 4%, GREEN mean 80%."""
    bench = results["adjudicator_fixture_check_2026_05"]
    assert bench["green_coverage"] == {"E1": 0.9, "E2": 0.6, "E3": 0.8, "E4": 1.0, "E5": 0.7}
    assert bench["red_coverage"] == {"E1": 0.2, "E2": 0.0, "E3": 0.0, "E4": 0.0, "E5": 0.0}
    assert bench["red_mean"] == 0.04
    assert bench["green_mean"] == 0.8


def test_fixture_permutation(results):
    """Fixtures vs shuffled expected lists: diagonal 80%, off-diagonal 0.5%, max 10%."""
    bench = results["adjudicator_fixture_check_2026_05"]
    assert bench["permutation_diagonal_mean"] == 0.8
    assert bench["permutation_offdiagonal_mean"] == 0.005
    assert bench["permutation_offdiagonal_max"] == 0.1


def test_july_outcome_information(results):
    """Share of the four-way outcome carried by the exit code and by exit + stop_reason."""
    info = results["iron_law_11"]["july_2026"]["outcome_information"]
    author, codebook = info["author"], info["codebook"]
    assert author["outcomes"] == {"blocked": 1, "cut": 25, "declined": 20, "done": 4}
    assert codebook["outcomes"] == {"blocked": 1, "cut": 25, "declined": 19, "done": 5}
    assert round(author["entropy_bits"], 2) == 1.43
    assert round(author["exit_code"]["bits"], 2) == 1.00
    assert round(author["exit_code"]["share"] * 100) == 70
    assert round(author["exit_code_and_stop_reason"]["bits"], 2) == 1.12
    assert round(author["exit_code_and_stop_reason"]["share"] * 100) == 78
    assert round(codebook["exit_code"]["share"] * 100) == 68
    assert round(codebook["exit_code_and_stop_reason"]["share"] * 100) == 76
    assert round(codebook["entropy_bits"], 2) == 1.48
    # Binary question "was the task delivered?": stop_reason adds nothing to the exit code.
    for block, share in ((author["delivered"], 22), (codebook["delivered"], 24)):
        assert round(block["exit_code"]["share"] * 100) == share
        assert block["exit_code"] == block["exit_code_and_stop_reason"]


def test_fixture_check_rescored_and_layers(results):
    """Re-scoring the fixtures reproduces the committed coverage; every match is layer 1."""
    fx = results["adjudicator_fixture_check_2026_05"]
    assert fx["rescored_coverage"]["RED"] == fx["red_coverage"]
    assert fx["rescored_coverage"]["GREEN"] == fx["green_coverage"]
    assert fx["matches_by_layer"] == {"exact_name": 42}
