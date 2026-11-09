"""Analyse study 2 (2026-11b) as fixed in ``PROTOCOL.md``.

Primary: RED-risk minus RED-plain coverage, by the blind Gemini judge, pooled over the 24
task x model strata, one-sided permutation test with labels shuffled within each stratum.
Secondary: the same per model, the Grok judge, the lexical matcher, and relevance (the share of
an answer's table rows the judge calls a concrete, plausible risk of this change).

Usage::

    python analyze.py results 5
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path

from score import coverage

HERE = Path(__file__).resolve().parent
SEED = "asp-study2-2026-11b"
RELABELLINGS = 10_000
A, B = "RED-risk", "RED-plain"
MODELS = ["claude-opus-5-5", "claude-sonnet-5-5"]
PLANNED_STRATA = 12 * len(MODELS)  # 12 tasks x 2 models, fixed before data


def delta(scores: dict) -> tuple[float, dict]:
    """Return the mean over strata of the per-stratum difference in mean coverage (A minus B).

    Parameters
    ----------
    scores : dict
        ``{stratum: {condition: [value, ...]}}``.

    Returns
    -------
    tuple
        ``(delta_bar, per_stratum)``.
    """
    per = {
        k: statistics.fmean(c[A]) - statistics.fmean(c[B])
        for k, c in scores.items()
        if c[A] and c[B]
    }
    return (statistics.fmean(per.values()) if per else 0.0), per


def permutation_p(scores: dict) -> float:
    """One-sided permutation p for delta > 0, labels shuffled within each stratum.

    Parameters
    ----------
    scores : dict
        ``{stratum: {condition: [value, ...]}}``.

    Returns
    -------
    float
        ``(hits + 1) / (relabellings + 1)``.
    """
    observed, _ = delta(scores)
    rng = random.Random(SEED)
    hits = 0
    for _ in range(RELABELLINGS):
        shuffled = {}
        for k, c in scores.items():
            pool = c[A] + c[B]
            rng.shuffle(pool)
            shuffled[k] = {A: pool[: len(c[A])], B: pool[len(c[A]) :]}
        hits += delta(shuffled)[0] >= observed - 1e-12
    return (hits + 1) / (RELABELLINGS + 1)


def decision(p: float, p_by_model: dict, complete: int) -> str:
    """Apply the decision rule of ``PROTOCOL.md``.

    Parameters
    ----------
    p : float
        Pooled permutation p.
    p_by_model : dict
        Model to its own permutation p (strata of that model only).
    complete : int
        Strata with every replicate in both conditions.

    Returns
    -------
    str
        ``incomplete``, ``confirmed``, ``confirmed in one model only: <model>`` or
        ``not confirmed``.
    """
    if complete < PLANNED_STRATA * 0.75:
        return "incomplete"
    if p >= 0.05:
        return "not confirmed"
    passing = [m for m, q in p_by_model.items() if q < 0.05]
    if len(passing) == len(MODELS):
        return "confirmed"
    if len(passing) == 1:
        return f"confirmed in one model only: {passing[0]}"
    return "not confirmed"


def summarise(values: dict, replicates: int) -> dict:
    """Run the primary analysis on one scorer's per-trial values.

    Parameters
    ----------
    values : dict
        ``{(task, model): {condition: [value, ...]}}``.
    replicates : int
        Planned replicates per cell.

    Returns
    -------
    dict
        Overall means, pooled and per-model deltas, p, and the decision.
    """
    full = {
        f"{t}|{m}": c
        for (t, m), c in values.items()
        if len(c[A]) == replicates and len(c[B]) == replicates
    }
    d, per = delta(full)
    p = permutation_p(full) if full else 1.0
    by_model, p_by_model = {}, {}
    for m in MODELS:
        part = {k: c for k, c in full.items() if k.endswith(m)}
        by_model[m] = round(delta(part)[0], 4)
        p_by_model[m] = round(permutation_p(part), 4) if part else 1.0
    overall = {
        c: round(statistics.fmean(v for cell in values.values() for v in cell[c]), 4)
        for c in (A, B)
    }
    return {
        "overall": overall,
        "delta_bar": round(d, 4),
        "p": round(p, 4),
        "by_model": by_model,
        "p_by_model": p_by_model,
        "positive_strata": sum(x > 0 for x in per.values()),
        "complete_strata": len(full),
        "decision": decision(p, p_by_model, len(full)),
    }


def do_results(replicates: int) -> dict:
    """Score every trial with each scorer and write ``results.json``.

    Parameters
    ----------
    replicates : int
        Replicates per task, model and condition.

    Returns
    -------
    dict
        Per-trial rows and one summary per scorer.
    """
    merged = json.loads((HERE / "lists" / "merged.json").read_text())
    trials = [json.loads(x) for x in (HERE / "runs" / "trials.jsonl").read_text().splitlines()]
    scorers = ["gemini", "grok", "matcher", "relevance"]
    values = {s: {} for s in scorers}
    rows = []
    for tr in sorted(trials, key=lambda r: r["trial"]):
        answer = (HERE / "runs" / "answers" / f"{tr['trial']}.md").read_text(encoding="utf-8")
        ref = [i["item"] for i in merged[tr["task"]]["reference"]]
        lexical = coverage(ref, answer)
        row = {k: tr[k] for k in ("trial", "task", "model", "condition", "rep")}
        row.update(rows_in_table=lexical["rows"], words=lexical["words"], is_error=tr["is_error"])
        for s in scorers:
            if s == "matcher":
                v = lexical["coverage"]
            else:
                f = HERE / "judge" / s / f"{tr['trial']}.json"
                if not f.exists():
                    continue
                j = json.loads(f.read_text())
                v = round(len(j["covered"]) / j["n"], 4) if j["n"] else 0.0
            v = 0.0 if tr["is_error"] else v
            row[s] = v
            cell = values[s].setdefault((tr["task"], tr["model"]), {A: [], B: []})
            cell[tr["condition"]].append(v)
        rows.append(row)
    result = {"trials": rows, "primary_scorer": "gemini"}
    result.update({s: summarise(values[s], replicates) for s in scorers if values[s]})
    (HERE / "results.json").write_text(json.dumps(result, indent=1) + "\n")
    return result


if __name__ == "__main__":
    if sys.argv[1:2] == ["results"]:
        r = do_results(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
        g = r["gemini"]
        print(
            f"study2 -> results.json | plain {g['overall'][B]:.1%}, list-what-could-go-wrong "
            f"{g['overall'][A]:.1%} | delta {g['delta_bar']:+.3f}, p = {g['p']} | {g['decision']}"
        )
    else:
        sys.exit(__doc__)
