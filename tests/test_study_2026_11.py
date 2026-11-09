"""Every number the README and the preprint quote from the 2026-11 study, as an assertion.

The numbers are read from ``benchmark/study-2026-11/results.json``, which ``run_all.py`` derives
again from the committed judge verdicts, and from the verdict files themselves.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "benchmark" / "study-2026-11"
RESULTS = json.loads((STUDY / "results.json").read_text(encoding="utf-8"))


def _verdicts(folder: str) -> dict[str, dict]:
    """Return the judge verdicts in ``judge/<folder>/`` keyed by trial id.

    Parameters
    ----------
    folder : str
        ``gemini``, ``grok`` or ``gemini-full``.

    Returns
    -------
    dict
        Trial id to verdict.
    """
    return {
        f.stem: json.loads(f.read_text(encoding="utf-8"))
        for f in sorted((STUDY / "judge" / folder).glob("t*.json"))
    }


def test_ninety_trials_all_clean():
    """90 trials, 30 per condition, all successful, no project file changed."""
    trials = [json.loads(x) for x in (STUDY / "runs" / "trials.jsonl").read_text().splitlines()]
    assert len(trials) == 90
    for cond in ("GREEN", "RED-risk", "RED-plain"):
        assert sum(t["condition"] == cond for t in trials) == 30
    assert all(t["subtype"] == "success" and not t["is_error"] for t in trials)
    assert sum(t["project_files_changed"] for t in trials) == 0
    assert [t["asp_loaded"] for t in trials] == [t["condition"] == "GREEN" for t in trials]
    seconds = {
        c: round(sum(t["seconds"] for t in trials if t["condition"] == c) / 30)
        for c in ("RED-plain", "RED-risk", "GREEN")
    }
    assert seconds == {"RED-plain": 58, "RED-risk": 50, "GREEN": 175}


def test_primary_result():
    """Primary judge: ASP 48%, plain + one sentence 66%, plain 56%; no measurable benefit."""
    g = RESULTS["gemini"]
    assert g["overall"] == {"GREEN": 0.4811, "RED-risk": 0.6635, "RED-plain": 0.56}
    assert g["primary"]["delta_bar"] == -0.1825
    assert g["primary"]["p"] == 1.0
    assert all(d < 0 for d in g["primary"]["per_task"].values())
    assert g["primary"]["decision"] == "no measurable benefit"


def test_second_judge_agrees():
    """Grok: same direction on every task, same decision."""
    k = RESULTS["grok"]
    assert k["overall"] == {"GREEN": 0.5378, "RED-risk": 0.7022, "RED-plain": 0.5679}
    assert k["primary"]["delta_bar"] == -0.1644
    assert all(d < 0 for d in k["primary"]["per_task"].values())
    assert k["primary"]["decision"] == "no measurable benefit"


def test_one_sentence_effect():
    """Secondary, pre-registered: asking for the ways it could go wrong helps (+10 / +13 points)."""
    assert RESULTS["gemini"]["secondary"]["RED-risk - RED-plain"] == {
        "delta_bar": 0.1035,
        "p": 0.0014,
    }
    assert RESULTS["grok"]["secondary"]["RED-risk - RED-plain"] == {
        "delta_bar": 0.1343,
        "p": 0.0001,
    }


def test_lexical_matcher_was_blind():
    """The demoted lexical matcher covers almost nothing in any condition."""
    assert max(RESULTS["matcher"]["overall"].values()) < 0.03


def test_judges_agree_on_items():
    """The two judges agree on 91.9% of the 855 item decisions."""
    gem, grok = _verdicts("gemini"), _verdicts("grok")
    assert sorted(gem) == sorted(grok) and len(gem) == 90
    pairs = [
        (i in gem[t]["covered"], i in grok[t]["covered"])
        for t in gem
        for i in range(1, gem[t]["n"] + 1)
    ]
    assert len(pairs) == 855
    assert round(sum(a == b for a, b in pairs) / len(pairs), 3) == 0.919


def test_exploratory_full_text():
    """Exploratory: reading whole answers narrows the gap to -0.08, ASP behind on 5 of 6 tasks."""
    trials = {t["trial"]: t for t in RESULTS["trials"]}
    full = _verdicts("gemini-full")
    cover: dict[str, dict[str, list[float]]] = {}
    for tid, v in full.items():
        tr = trials[tid]
        cover.setdefault(tr["condition"], {}).setdefault(tr["task"], []).append(
            len(v["covered"]) / v["n"]
        )

    def mean(xs: list[float]) -> float:
        """Arithmetic mean."""
        return sum(xs) / len(xs)

    overall = {c: round(mean([x for xs in by.values() for x in xs]), 3) for c, by in cover.items()}
    assert overall == {"GREEN": 0.659, "RED-risk": 0.739}
    behind = sum(mean(cover["GREEN"][t]) < mean(cover["RED-risk"][t]) for t in cover["GREEN"])
    assert behind == 5


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX paths in the ledger")
def test_ledger_chain_intact():
    """Every ledger link holds and every file matches its latest entry."""
    out = subprocess.run(
        [sys.executable, str(STUDY / "ledger.py"), "verify"], capture_output=True, text=True
    )
    assert out.returncode == 0, out.stdout + out.stderr
