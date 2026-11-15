"""Unplanned checks on the second yardstick of study 2 (2026-11b).

Neither check is in ``ADDENDUM.md``. A blind reviewer of the manuscript asked for them after
the result of the second yardstick was known (``docs/paper/review/``, round 2), and they have no
decision rule. The three network-error trials are all ``RED-plain`` and count 0, which favours
the hypothesis; this script repeats the statistic and the permutation test of ``analyze.py``
without the three strata that hold them, without the three trials, and with each scored as full
coverage (the opposite bound). It also gives two 95% percentile intervals of the mean
difference, for both yardsticks: replicates resampled inside each cell, as in ``describe.py``,
and whole tasks resampled, which treats the twelve tasks as a sample.

Usage::

    python sensitivity2.py [--quiet]
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from analyze import MODELS, A, B, delta, permutation_p  # noqa: E402
from describe import bootstrap_interval  # noqa: E402

SEED = "asp-study2-2026-11b-yardstick2-sensitivity"
RESAMPLES = 10_000


def summary(cells: dict) -> dict:
    """Return the mean difference and its permutation p, pooled and per model.

    Parameters
    ----------
    cells : dict
        ``{"task|model": {condition: [coverage, ...]}}``.

    Returns
    -------
    dict
        ``{strata, delta_bar, p, by_model, p_by_model}``.
    """
    part = {m: {k: c for k, c in cells.items() if k.endswith(m)} for m in MODELS}
    return {
        "strata": len(cells),
        "delta_bar": round(delta(cells)[0], 4),
        "p": round(permutation_p(cells), 4),
        "by_model": {m: round(delta(part[m])[0], 4) for m in MODELS},
        "p_by_model": {m: round(permutation_p(part[m]), 4) for m in MODELS},
    }


def task_interval(cells: dict) -> list[float]:
    """Return a 95% percentile interval of the mean difference, resampling whole tasks.

    Parameters
    ----------
    cells : dict
        ``{"task|model": {condition: [coverage, ...]}}``.

    Returns
    -------
    list of float
        ``[low, high]``.
    """
    by_task: dict = {}
    for key, c in cells.items():
        by_task.setdefault(key.split("|")[0], []).append(
            statistics.fmean(c[A]) - statistics.fmean(c[B])
        )
    per_task = [statistics.fmean(v) for _, v in sorted(by_task.items())]
    rng = random.Random(SEED)
    draws = sorted(
        statistics.fmean(rng.choices(per_task, k=len(per_task))) for _ in range(RESAMPLES)
    )
    return [round(draws[int(0.025 * RESAMPLES)], 4), round(draws[int(0.975 * RESAMPLES) - 1], 4)]


def cells_of(rows: list, value, skip=lambda r, bad: False) -> dict:
    """Group one coverage value per trial into task-by-model cells.

    Parameters
    ----------
    rows : list of dict
        Trials, each with ``trial``, ``task``, ``model``, ``condition`` and ``is_error``.
    value : callable
        ``value(row) -> float``.
    skip : callable
        ``skip(row, strata_with_an_error) -> bool``.

    Returns
    -------
    dict
        ``{"task|model": {condition: [coverage, ...]}}``.
    """
    bad = {(r["task"], r["model"]) for r in rows if r["is_error"]}
    cells: dict = {}
    for r in sorted(rows, key=lambda r: r["trial"]):
        if skip(r, bad):
            continue
        cells.setdefault(f"{r['task']}|{r['model']}", {A: [], B: []})[r["condition"]].append(
            value(r)
        )
    return cells


def run() -> dict:
    """Compute the checks for every judge whose verdicts on the second yardstick are complete.

    Returns
    -------
    dict
        ``{"error_trials", "original": {...}, judge: {...}}``.
    """
    rows = json.loads((HERE.parent / "results.json").read_text())["trials"]
    out: dict = {"error_trials": sorted(r["trial"] for r in rows if r["is_error"])}
    first = cells_of(rows, lambda r: r["gemini"])
    out["original"] = {
        "judge": "gemini",
        "bootstrap_95": bootstrap_interval(first),
        "task_bootstrap_95": task_interval(first),
    }
    for name in ("gemini", "grok"):
        files = {r["trial"]: HERE / "judge" / name / f"{r['trial']}.json" for r in rows}
        if not all(f.exists() for f in files.values()):
            continue
        share = {}
        for trial, f in files.items():
            j = json.loads(f.read_text())
            share[trial] = round(len(j["covered"]) / j["n"], 4) if j["n"] else 0.0

        def scored(r, share=share):
            return 0.0 if r["is_error"] else share[r["trial"]]

        fixed = cells_of(rows, scored)
        out[name] = {
            "fixed_rule": summary(fixed),
            "without_strata": summary(
                cells_of(rows, scored, lambda r, bad: (r["task"], r["model"]) in bad)
            ),
            "without_trials": summary(cells_of(rows, scored, lambda r, bad: r["is_error"])),
            "errors_as_full_coverage": summary(
                cells_of(rows, lambda r, share=share: 1.0 if r["is_error"] else share[r["trial"]])
            ),
            "bootstrap_95": bootstrap_interval(fixed),
            "task_bootstrap_95": task_interval(fixed),
        }
    (HERE / "sensitivity2.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    out = run()
    if "--quiet" in sys.argv:
        g = out["gemini"]
        print(
            "study2 second yardstick, checks -> sensitivity2.json | errors as full coverage: "
            f"delta {g['errors_as_full_coverage']['delta_bar']:+.3f}, "
            f"p = {g['errors_as_full_coverage']['p']}"
        )
    else:
        print(json.dumps(out, indent=1))
