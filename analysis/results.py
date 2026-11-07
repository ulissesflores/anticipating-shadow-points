"""Derive every number the two papers cite from committed data.

Inputs are all in the repository and never change:

* ``tests/iron-law-11/runs/published/2026-05-18T15-36-05Z-c1bceb85`` -- the
  May 2026 `claude -p` run (frozen evidence, hash-locked inputs).
* ``data/spike-2026-07-08/`` -- the redacted July 2026 re-measurement and the
  author/codebook labels.
* ``benchmark/runs/published/2026-05-18T00-27-43Z-b0a1bc7b`` -- a MOCK-mode run of
  the benchmark package: its RED/GREEN texts are fixtures the author wrote to
  exercise the adjudicator (``benchmark/PROTOCOL.md`` section 8), not model
  outputs. It validates the instrument; it says nothing about ASP's effect.

The derivation is deterministic: no network, no model calls, no randomness.
Output: ``output/results.json`` (canonical JSON, sorted keys).
"""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IL11 = ROOT / "tests" / "iron-law-11"
MAY_RUN = IL11 / "runs" / "published" / "2026-05-18T15-36-05Z-c1bceb85"
SPIKE = ROOT / "data" / "spike-2026-07-08"
BENCH_RUN = ROOT / "benchmark" / "runs" / "published" / "2026-05-18T00-27-43Z-b0a1bc7b"
EVALS = ROOT / "skills" / "anticipating-shadow-points" / "evals"
OUT = ROOT / "output" / "results.json"


def _load_analyze():
    """Import the locked May 2026 analysis script without copying it.

    Returns
    -------
    module
        ``tests/iron-law-11/scripts/analyze.py`` as a module, so the July data
        is scored with the exact detector and interval code used in May.
    """
    path = IL11 / "scripts" / "analyze.py"
    spec = importlib.util.spec_from_file_location("il11_analyze", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["il11_analyze"] = module  # dataclasses resolve types via sys.modules
    spec.loader.exec_module(module)
    return module


def wilson_95(k: int, n: int) -> tuple[float, float]:
    """Wilson score 95% interval for a binomial proportion.

    Parameters
    ----------
    k : int
        Successes.
    n : int
        Trials.

    Returns
    -------
    tuple of float
        ``(lower, upper)`` rounded to 4 decimals.
    """
    z = 1.959963984540054
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return round(centre - half, 4), round(centre + half, 4)


def _rate(k: int, n: int, analyze) -> dict:
    """Summarise a count as rate plus Wilson and Clopper-Pearson intervals.

    Parameters
    ----------
    k : int
        Count.
    n : int
        Denominator.
    analyze : module
        The locked analysis module (for its Clopper-Pearson implementation).

    Returns
    -------
    dict
        ``k``, ``n``, ``rate``, ``wilson95`` and ``clopper_pearson95``.
    """
    cp = analyze.clopper_pearson_95(k, n)
    return {
        "k": k,
        "n": n,
        "rate": round(k / n, 4),
        "wilson95": list(wilson_95(k, n)),
        "clopper_pearson95": [round(cp[0], 4), round(cp[1], 4)],
    }


def may_2026(analyze, phrases: list[str]) -> dict:
    """Recompute the May 2026 run with the locked phrase detector.

    Parameters
    ----------
    analyze : module
        The locked analysis module.
    phrases : list of str
        The locked refusal phrases.

    Returns
    -------
    dict
        Detector-based silent-refusal count, exit-code split and model.
    """
    trials = analyze.adjudicate_run(MAY_RUN, IL11)
    silent = sum(t.refused and t.exit_zero for t in trials)
    exit0 = sum(t.exit_zero for t in trials)
    summary = json.loads((MAY_RUN / "run-summary.json").read_text(encoding="utf-8"))
    return {
        "claude_code_version": "2.1.143",
        "model": summary["model"],
        "max_turns": summary["max_turns"],
        "n": len(trials),
        "exit0": exit0,
        "detector_silent_refusals": _rate(silent, len(trials), analyze),
    }


def july_2026(analyze, phrases: list[str]) -> dict:
    """Recompute the July 2026 re-measurement from the redacted extract.

    Parameters
    ----------
    analyze : module
        The locked analysis module.
    phrases : list of str
        The locked refusal phrases.

    Returns
    -------
    dict
        Exit/stop splits, answering-model mix and the three silent-refusal
        readings (locked detector, author label, codebook majority).
    """
    trials = [
        json.loads(line)
        for line in (SPIKE / "trials.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    with (SPIKE / "adjudication.tsv").open(encoding="utf-8") as fh:
        labels = {row["scenario_id"]: row for row in csv.DictReader(fh, delimiter="\t")}
    n = len(trials)

    def silent(pred) -> int:
        """Count exit-0 trials whose (trial, label) pair satisfies ``pred``."""
        return sum(1 for t in trials if t["exit_code"] == 0 and pred(t, labels[t["scenario_id"]]))

    detector = silent(lambda t, lab: analyze.matches_refusal(t["result_text"], phrases)[0])
    author = silent(lambda t, lab: lab["author_label"] == "DECLINE")
    codebook = silent(lambda t, lab: lab["codebook_majority"] == "DECLINE")
    core = silent(lambda t, lab: lab["class"] in {"safety_refusal", "destructive_refusal"})
    exit0 = [t for t in trials if t["exit_code"] == 0]
    model_mix = Counter(",".join(t["answering_models"]) for t in trials)
    safety_models = Counter(
        ",".join(t["answering_models"]) for t in trials if t["category"] == "safety"
    )
    return {
        "claude_code_version": sorted({t["claude_code_version"] for t in trials}),
        "session_model": sorted({t["session_model"] for t in trials}),
        "answering_models": dict(sorted(model_mix.items())),
        "safety_answering_models": dict(sorted(safety_models.items())),
        "permission_mode": sorted({t["permission_mode"] for t in trials}),
        "n": n,
        "exit0": len(exit0),
        "exit1": n - len(exit0),
        "exit0_stop_reasons": dict(sorted(Counter(t["stop_reason"] for t in exit0).items())),
        "stop_reasons": dict(sorted(Counter(t["stop_reason"] for t in trials).items())),
        "classes": dict(sorted(Counter(lab["class"] for lab in labels.values()).items())),
        "detector_silent_refusals": _rate(detector, n, analyze),
        "author_silent_refusals": _rate(author, n, analyze),
        "codebook_silent_refusals": _rate(codebook, n, analyze),
        "core_silent_refusals": _rate(core, n, analyze),
        "total_cost_usd": round(sum(t["total_cost_usd"] or 0 for t in trials), 2),
        "redacted_replies": sum(1 for t in trials if t["redactions"]),
    }


def adjudicator_fixture_check() -> dict:
    """Recompute the adjudicator check on the author-constructed fixtures.

    The published benchmark run is a mock run: every ``outputs/*/*.response.json``
    points at a fixture under ``benchmark/tests/fixtures/mock_runs/``. The
    numbers below therefore describe the matcher on text written to exercise
    it, and must never be quoted as an effect of ASP on a model.

    Returns
    -------
    dict
        Run mode, per-eval coverage of the RED/GREEN fixtures, the 5x5
        GREEN-fixture x expected-list matrix and its summary.
    """
    sys.path.insert(0, str(ROOT / "benchmark" / "src"))
    from asp_benchmark.adjudicator import adjudicate
    from asp_benchmark.eval_parser import parse_evals_dir

    specs = {s.eval_id: s for s in parse_evals_dir(EVALS)}
    ids = sorted(specs)
    committed = {}
    for cond in ("RED", "GREEN"):
        committed[cond] = {
            eid: json.loads(
                (BENCH_RUN / "adjudication" / eid / f"{cond}.json").read_text(encoding="utf-8")
            )["coverage"]
            for eid in ids
        }
    green = {
        eid: (BENCH_RUN / "outputs" / eid / "GREEN.text.txt").read_text(encoding="utf-8")
        for eid in ids
    }
    matrix = {
        i: {j: adjudicate(specs[j], green[i], "GREEN", "perm").coverage for j in ids} for i in ids
    }
    diag = [matrix[i][i] for i in ids]
    off = [matrix[i][j] for i in ids for j in ids if i != j]
    manifest = json.loads((BENCH_RUN / "manifest.json").read_text(encoding="utf-8"))
    return {
        "run_mode": manifest["mode"],
        "texts_are": "author-constructed fixtures (benchmark/tests/fixtures/mock_runs), "
        "not model outputs",
        "eval_ids": ids,
        "red_coverage": committed["RED"],
        "green_coverage": committed["GREEN"],
        "red_mean": round(sum(committed["RED"].values()) / len(ids), 4),
        "green_mean": round(sum(committed["GREEN"].values()) / len(ids), 4),
        "permutation_matrix": matrix,
        "permutation_diagonal_mean": round(sum(diag) / len(diag), 4),
        "permutation_offdiagonal_mean": round(sum(off) / len(off), 4),
        "permutation_offdiagonal_max": max(off),
    }


def compute() -> dict:
    """Assemble the full results document.

    Returns
    -------
    dict
        Everything ``output/results.json`` contains.
    """
    analyze = _load_analyze()
    phrases = analyze.load_refusal_phrases(IL11)
    return {
        "schema": 1,
        "iron_law_11": {
            "may_2026": may_2026(analyze, phrases),
            "july_2026": july_2026(analyze, phrases),
        },
        "adjudicator_fixture_check_2026_05": adjudicator_fixture_check(),
    }


def main() -> None:
    """Write ``output/results.json`` and print a one-line summary."""
    results = compute()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    j = results["iron_law_11"]["july_2026"]
    print(
        f"results -> {OUT.relative_to(ROOT)} | July author {j['author_silent_refusals']['k']}/50, "
        f"codebook {j['codebook_silent_refusals']['k']}/50, "
        f"detector {j['detector_silent_refusals']['k']}/50"
    )


if __name__ == "__main__":
    main()
