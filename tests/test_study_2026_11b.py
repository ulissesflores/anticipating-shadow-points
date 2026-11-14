"""Every number the README quotes from study 2 (2026-11b), as an assertion.

The numbers are read from ``benchmark/study-2026-11b/results.json`` and ``sensitivity.json``,
which ``run_all.py`` derives again from the committed judge verdicts, and from the verdict files.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "benchmark" / "study-2026-11b"
RESULTS = json.loads((STUDY / "results.json").read_text(encoding="utf-8"))
SENSITIVITY = json.loads((STUDY / "sensitivity.json").read_text(encoding="utf-8"))
OPUS, SONNET = "claude-opus-5-5", "claude-sonnet-5-5"
TRIALS = [json.loads(x) for x in (STUDY / "runs" / "trials.jsonl").read_text().splitlines()]


def _mean(scorer: str, model: str, condition: str) -> float:
    """Return the mean of one scorer over one model and condition, rounded to two places.

    Parameters
    ----------
    scorer : str
        ``gemini``, ``grok`` or ``relevance``.
    model : str
        Model id.
    condition : str
        ``RED-plain`` or ``RED-risk``.

    Returns
    -------
    float
        The rounded mean.
    """
    xs = [
        t[scorer] for t in RESULTS["trials"] if t["model"] == model and t["condition"] == condition
    ]
    assert len(xs) == 60
    return round(sum(xs) / len(xs), 2)


def test_trials_as_collected():
    """240 trials, 60 per model and condition, no plugin, no file changed, three network errors."""
    assert len(TRIALS) == 240
    for model in (OPUS, SONNET):
        for cond in ("RED-plain", "RED-risk"):
            assert sum(t["model"] == model and t["condition"] == cond for t in TRIALS) == 60
    assert sum(t["project_files_changed"] for t in TRIALS) == 0
    assert not any(t["asp_loaded"] for t in TRIALS)
    errors = sorted(t["trial"] for t in TRIALS if t["is_error"])
    assert errors == ["t097", "t099", "t100"] == SENSITIVITY["error_trials"]
    assert {t["condition"] for t in TRIALS if t["is_error"]} == {"RED-plain"}
    seconds = {
        c: round(
            sum(t["seconds"] for t in TRIALS if t["condition"] == c and not t["is_error"])
            / sum(t["condition"] == c and not t["is_error"] for t in TRIALS)
        )
        for c in ("RED-plain", "RED-risk")
    }
    assert seconds == {"RED-plain": 50, "RED-risk": 40}


def test_primary_result_confirmed():
    """Primary judge: 46% to 58%, +11 points, p = 0.0001 pooled and within each model."""
    g = RESULTS["gemini"]
    assert RESULTS["primary_scorer"] == "gemini"
    assert g["overall"] == {"RED-risk": 0.5751, "RED-plain": 0.4611}
    assert g["delta_bar"] == 0.114
    assert g["p"] == 0.0001
    assert g["by_model"] == {OPUS: 0.1039, SONNET: 0.1242}
    assert g["p_by_model"] == {OPUS: 0.0001, SONNET: 0.0001}
    assert (g["positive_strata"], g["complete_strata"]) == (22, 24)
    assert g["decision"] == "confirmed"


def test_per_model_table():
    """The README table: coverage by model and condition for both judges."""
    assert [_mean("gemini", OPUS, c) for c in ("RED-plain", "RED-risk")] == [0.43, 0.54]
    assert [_mean("gemini", SONNET, c) for c in ("RED-plain", "RED-risk")] == [0.49, 0.61]
    assert [_mean("grok", OPUS, c) for c in ("RED-plain", "RED-risk")] == [0.48, 0.57]
    assert [_mean("grok", SONNET, c) for c in ("RED-plain", "RED-risk")] == [0.52, 0.64]


def test_second_judge_agrees():
    """Grok: 50% to 61%, +11 points, the same decision."""
    k = RESULTS["grok"]
    assert k["overall"] == {"RED-risk": 0.6075, "RED-plain": 0.5003}
    assert k["delta_bar"] == 0.1072
    assert k["p_by_model"] == {OPUS: 0.0001, SONNET: 0.0001}
    assert k["decision"] == "confirmed"


def test_sensitivity_without_error_strata():
    """Without the three strata that hold a network error the result stands: +10 and +9 points."""
    g = SENSITIVITY["gemini"]["without_strata"]
    assert (g["strata"], g["delta_bar"], g["p"]) == (21, 0.101, 0.0001)
    assert g["p_by_model"] == {OPUS: 0.0002, SONNET: 0.0001}
    k = SENSITIVITY["grok"]["without_strata"]
    assert (k["delta_bar"], k["p"]) == (0.0887, 0.0001)
    assert max(k["p_by_model"].values()) < 0.05


def test_relevance_not_lower():
    """Relevance: 69% to 74% under the fixed rule; +3 points and not significant without errors."""
    r = RESULTS["relevance"]
    assert r["overall"] == {"RED-risk": 0.739, "RED-plain": 0.6936}
    assert (r["delta_bar"], r["p"]) == (0.0455, 0.0106)
    s = SENSITIVITY["relevance"]["without_strata"]
    assert (s["delta_bar"], s["p"]) == (0.0252, 0.0914)
    assert s["delta_bar"] > 0


def test_lexical_matcher_was_blind():
    """The lexical matcher covers almost nothing in either condition."""
    assert max(RESULTS["matcher"]["overall"].values()) < 0.03


def test_judges_agree_on_items():
    """The two judges agree on 93.2% of the 2,000 item decisions."""

    def verdicts(folder: str) -> dict[str, dict]:
        """Return the verdicts of one judge keyed by trial id."""
        return {
            f.stem: json.loads(f.read_text(encoding="utf-8"))
            for f in sorted((STUDY / "judge" / folder).glob("t*.json"))
        }

    gem, grok = verdicts("gemini"), verdicts("grok")
    assert sorted(gem) == sorted(grok) and len(gem) == 240
    pairs = [
        (i in gem[t]["covered"], i in grok[t]["covered"])
        for t in gem
        for i in range(1, gem[t]["n"] + 1)
    ]
    assert len(pairs) == 2000
    assert round(sum(a == b for a, b in pairs) / len(pairs), 3) == 0.932


def test_one_cli_version():
    """Every trial ran on the same Claude Code version."""
    import gzip
    import re

    versions = set()
    for t in TRIALS:
        raw = gzip.open(STUDY / "runs" / "envelopes" / f"{t['trial']}.jsonl.gz", "rt").read(20000)
        versions.add(re.search(r'"claude_code_version":"([^"]*)"', raw).group(1))
    assert versions == {"2.1.319"}


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX paths in the ledger")
def test_ledger_chain_intact():
    """Every ledger link holds and every file matches its latest entry."""
    out = subprocess.run(
        [sys.executable, str(STUDY / "ledger.py"), "verify"], capture_output=True, text=True
    )
    assert out.returncode == 0, out.stdout + out.stderr
