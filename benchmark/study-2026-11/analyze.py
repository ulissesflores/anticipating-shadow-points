"""Merge the reference lists and analyse the trials, as fixed in ``PROTOCOL.md``.

Usage::

    python analyze.py merge     # lists/<reviewer>/<task>.md -> lists/merged.json
    python analyze.py results   # runs/ + lists/merged.json -> results.json
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from pathlib import Path

from score import coverage, merge, numbered_items

HERE = Path(__file__).resolve().parent
REVIEWERS = ["gemini", "gptoss", "grok"]
SEED = "asp-bench-2026-11"
RELABELLINGS = 10_000
PRIMARY = ("GREEN", "RED-risk")
SECONDARY = [("GREEN", "RED-plain"), ("RED-risk", "RED-plain")]


def task_ids() -> list[str]:
    """Return the task ids in ``tasks.json`` order.

    Returns
    -------
    list of str
        ``T1``...``T6``.
    """
    return [t["id"] for t in json.loads((HERE / "tasks.json").read_text())["tasks"]]


def do_merge() -> dict:
    """Merge the three reviewers' lists per task and write ``lists/merged.json``.

    Returns
    -------
    dict
        Per task: the reference items, their count, each reviewer's count and the agreement.
    """
    out = {}
    for tid in task_ids():
        lists = {
            r: numbered_items((HERE / "lists" / r / f"{tid}.md").read_text(encoding="utf-8"))
            for r in REVIEWERS
        }
        reference, agreement = merge(lists)
        out[tid] = {
            "reference": reference,
            "n_reference": len(reference),
            "n_by_reviewer": {r: len(v) for r, v in lists.items()},
            "agreement": agreement,
        }
    (HERE / "lists" / "merged.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


def delta(scores: dict, a: str, b: str) -> tuple[float, dict]:
    """Return the mean over tasks of the per-task difference in mean coverage (a minus b).

    Parameters
    ----------
    scores : dict
        ``{task: {condition: [coverage, ...]}}``.
    a, b : str
        Conditions.

    Returns
    -------
    tuple
        ``(delta_bar, per_task_difference)``.
    """
    per = {
        t: statistics.fmean(c[a]) - statistics.fmean(c[b])
        for t, c in scores.items()
        if c[a] and c[b]
    }
    return statistics.fmean(per.values()), per


def permutation_p(scores: dict, a: str, b: str) -> float:
    """One-sided permutation p for delta(a, b) > 0, labels shuffled within each task.

    Parameters
    ----------
    scores : dict
        ``{task: {condition: [coverage, ...]}}``.
    a, b : str
        Conditions.

    Returns
    -------
    float
        Share of relabellings with a statistic at least as large as the observed one.
    """
    observed, _ = delta(scores, a, b)
    rng = random.Random(SEED)
    hits = 0
    for _ in range(RELABELLINGS):
        shuffled = {}
        for t, c in scores.items():
            pool = c[a] + c[b]
            rng.shuffle(pool)
            shuffled[t] = {a: pool[: len(c[a])], b: pool[len(c[a]) :]}
        if delta(shuffled, a, b)[0] >= observed - 1e-12:
            hits += 1
    return (hits + 1) / (RELABELLINGS + 1)


def decision(per_task: dict, p: float, complete: int) -> str:
    """Apply the primary decision rule of ``PROTOCOL.md``.

    Parameters
    ----------
    per_task : dict
        Per-task GREEN minus RED-risk difference.
    p : float
        Permutation p.
    complete : int
        Tasks with every replicate in both conditions.

    Returns
    -------
    str
        One of ``incomplete``, ``no measurable benefit``, ``measured benefit``, ``inconclusive``.
    """
    if complete < 5:
        return "incomplete"
    positive = sum(d > 0 for d in per_task.values())
    if len(per_task) - positive >= 3:
        return "no measurable benefit"
    if p < 0.05 and positive >= 5:
        return "measured benefit"
    return "inconclusive"


def summarise(scores: dict, replicates: int) -> dict:
    """Apply the primary and secondary analyses to one scorer's coverages.

    Parameters
    ----------
    scores : dict
        ``{task: {condition: [coverage, ...]}}``.
    replicates : int
        Replicates per task and condition.

    Returns
    -------
    dict
        Per-task means, the primary test with its decision, and the secondary tests.
    """
    full = {
        t: c
        for t, c in scores.items()
        if len(c[PRIMARY[0]]) == replicates and len(c[PRIMARY[1]]) == replicates
    }
    d, per = delta(full, *PRIMARY) if full else (0.0, {})
    p = permutation_p(full, *PRIMARY) if full else 1.0
    return {
        "overall": {
            c: round(statistics.fmean(v for cells in scores.values() for v in cells[c]), 4)
            for c in ("GREEN", "RED-risk", "RED-plain")
        },
        "means": {
            t: {k: round(statistics.fmean(v), 4) if v else None for k, v in c.items()}
            for t, c in scores.items()
        },
        "primary": {
            "comparison": "GREEN - RED-risk",
            "delta_bar": round(d, 4),
            "per_task": {k: round(v, 4) for k, v in per.items()},
            "p": round(p, 4),
            "complete_tasks": len(full),
            "decision": decision(per, p, len(full)),
        },
        "secondary": {
            f"{a} - {b}": {
                "delta_bar": round(delta(full, a, b)[0], 4),
                "p": round(permutation_p(full, a, b), 4),
            }
            for a, b in SECONDARY
        }
        if full
        else {},
    }


def do_results(replicates: int) -> dict:
    """Score every trial with each scorer and write ``results.json``.

    The judge ``gemini`` is primary; ``grok`` (second judge) and ``matcher`` (lexical) are
    secondary. A trial that ended with an error counts as coverage 0 for every scorer.

    Parameters
    ----------
    replicates : int
        Replicates per task and condition fixed under Deviations.

    Returns
    -------
    dict
        Per-trial scores and one summary per scorer.
    """
    merged = json.loads((HERE / "lists" / "merged.json").read_text())
    trials = [json.loads(ln) for ln in (HERE / "runs" / "trials.jsonl").read_text().splitlines()]
    scorers = ["gemini", "grok", "matcher"]
    scores = {
        s: {t: {c: [] for c in ("GREEN", "RED-risk", "RED-plain")} for t in task_ids()}
        for s in scorers
    }
    rows = []
    for tr in sorted(trials, key=lambda r: r["trial"]):
        answer = (HERE / "runs" / "answers" / f"{tr['trial']}.md").read_text(encoding="utf-8")
        ref = [i["item"] for i in merged[tr["task"]]["reference"]]
        lexical = coverage(ref, answer)
        row = {k: tr[k] for k in ("trial", "task", "condition", "rep")}
        row.update(rows_in_table=lexical["rows"], words=lexical["words"], is_error=tr["is_error"])
        for s in scorers:
            if s == "matcher":
                cov = lexical["coverage"]
            else:
                f = HERE / "judge" / s / f"{tr['trial']}.json"
                if not f.exists():
                    continue
                v = json.loads(f.read_text())
                cov = round(len(v["covered"]) / v["n"], 4)
                row[f"{s}_redactions"] = v["redactions"]
            cov = 0.0 if tr["is_error"] else cov
            row[s] = cov
            scores[s][tr["task"]][tr["condition"]].append(cov)
        rows.append(row)
    result = {"trials": rows, "primary_scorer": "gemini"}
    result.update({s: summarise(scores[s], replicates) for s in scorers})
    (HERE / "results.json").write_text(json.dumps(result, indent=1) + "\n")
    return result


if __name__ == "__main__":
    if sys.argv[1:] == ["merge"]:
        print(
            json.dumps(
                {
                    t: {k: v for k, v in m.items() if k != "reference"}
                    for t, m in do_merge().items()
                },
                indent=1,
            )
        )
    elif sys.argv[1:2] == ["results"]:
        r = do_results(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
        o = r["gemini"]["overall"]
        print(
            "study -> benchmark/study-2026-11/results.json | coverage ASP "
            f"{o['GREEN']:.1%}, list-what-could-go-wrong {o['RED-risk']:.1%}, plain "
            f"{o['RED-plain']:.1%} | primary: {r['gemini']['primary']['decision']}"
        )
    else:
        sys.exit(__doc__)
