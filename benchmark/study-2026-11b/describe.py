"""Describe study 2 (2026-11b) for the paper: tables that the fixed analysis does not print.

Nothing here is confirmatory. The decision of the study comes from ``analyze.py`` alone. This
script re-reads the sealed trials and verdicts and writes ``descriptives.json`` with:

* coverage per task and model (the 24 strata) and per task, by the primary judge;
* a percentile interval for the primary difference, from a bootstrap that resamples replicates
  inside each task x model x condition cell (not planned in ``PROTOCOL.md``);
* cost per condition and model: seconds, turns, output tokens, table rows and words;
* item-level agreement between the two judges, with Cohen's kappa;
* coverage of each reference risk per condition (exploratory): which risks the sentence adds.

Usage::

    python describe.py [--quiet]
"""

from __future__ import annotations

import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SEED = "asp-study2-2026-11b-describe"
RESAMPLES = 10_000
A, B = "RED-risk", "RED-plain"
MODELS = ["claude-opus-5-5", "claude-sonnet-5-5"]


def load() -> tuple[list[dict], dict[str, dict]]:
    """Return the scored trials of ``results.json`` joined with their run records.

    Returns
    -------
    tuple
        ``(trials, runs)``: the scored trials and the ``trials.jsonl`` records by trial id.
    """
    trials = json.loads((HERE / "results.json").read_text())["trials"]
    runs = {}
    for line in (HERE / "runs" / "trials.jsonl").read_text().splitlines():
        rec = json.loads(line)
        runs[rec["trial"]] = rec
    return trials, runs


def cells(trials: list[dict], key: str = "gemini") -> dict:
    """Group a score by stratum and condition.

    Parameters
    ----------
    trials : list of dict
        Scored trials.
    key : str
        Score to read.

    Returns
    -------
    dict
        ``{(task, model): {condition: [value, ...]}}``.
    """
    out: dict = defaultdict(lambda: {A: [], B: []})
    for t in trials:
        out[(t["task"], t["model"])][t["condition"]].append(t[key])
    return out


def cells_in_analysis_order(trials: list[dict], key: str = "gemini") -> dict:
    """Group a score by stratum in the order ``analyze.py`` builds it, so shuffles repeat.

    Parameters
    ----------
    trials : list of dict
        Scored trials, in the order of ``results.json``.
    key : str
        Score to read.

    Returns
    -------
    dict
        ``{"task|model": {condition: [value, ...]}}`` in first-seen order.
    """
    out: dict = {}
    for t in trials:
        out.setdefault(f"{t['task']}|{t['model']}", {A: [], B: []})[t["condition"]].append(t[key])
    return out


def delta_bar(scores: dict) -> float:
    """Return the mean over strata of mean(A) minus mean(B).

    Parameters
    ----------
    scores : dict
        ``{stratum: {condition: [value, ...]}}``.

    Returns
    -------
    float
        The primary statistic of ``PROTOCOL.md``.
    """
    return statistics.fmean(
        statistics.fmean(c[A]) - statistics.fmean(c[B]) for c in scores.values()
    )


def bootstrap_interval(scores: dict) -> list[float]:
    """Return a 95% percentile interval for ``delta_bar``, resampling replicates inside each cell.

    Parameters
    ----------
    scores : dict
        ``{stratum: {condition: [value, ...]}}``.

    Returns
    -------
    list of float
        ``[low, high]``.
    """
    rng = random.Random(SEED)
    keys = sorted(scores)
    draws = []
    for _ in range(RESAMPLES):
        draws.append(
            statistics.fmean(
                statistics.fmean(rng.choices(scores[k][A], k=len(scores[k][A])))
                - statistics.fmean(rng.choices(scores[k][B], k=len(scores[k][B])))
                for k in keys
            )
        )
    draws.sort()
    return [round(draws[int(0.025 * RESAMPLES)], 4), round(draws[int(0.975 * RESAMPLES) - 1], 4)]


def null_distribution(scores: dict) -> dict:
    """Return the permutation null of ``delta_bar`` as a histogram, with the observed value.

    The shuffles repeat those of ``analyze.py`` (same seed and order), so the count of shuffles
    at or above the observed value is the one behind the published p.

    Parameters
    ----------
    scores : dict
        ``{stratum: {condition: [value, ...]}}``, in the insertion order of ``analyze.py``.

    Returns
    -------
    dict
        Observed value, largest shuffled value, hits, and counts per bin of half a point.
    """
    from analyze import RELABELLINGS
    from analyze import SEED as ANALYSIS_SEED

    observed = delta_bar(scores)
    rng = random.Random(ANALYSIS_SEED)
    width = 0.005
    counts: dict = defaultdict(int)
    largest, hits = -1.0, 0
    for _ in range(RELABELLINGS):
        shuffled = {}
        for k, c in scores.items():
            pool = c[A] + c[B]
            rng.shuffle(pool)
            shuffled[k] = {A: pool[: len(c[A])], B: pool[len(c[A]) :]}
        d = delta_bar(shuffled)
        largest = max(largest, d)
        hits += d >= observed - 1e-12
        counts[round(d // width * width, 3)] += 1
    return {
        "observed": round(observed, 4),
        "largest_shuffled": round(largest, 4),
        "hits": hits,
        "relabellings": RELABELLINGS,
        "bin_width": width,
        "bins": {f"{k:.3f}": counts[k] for k in sorted(counts)},
    }


def wording_origin() -> dict:
    """Return how many reference risks carry each reviewer's wording.

    Returns
    -------
    dict
        ``{reviewer: count}`` over the 100 reference risks.
    """
    merged = json.loads((HERE / "lists" / "merged.json").read_text())
    out: dict = defaultdict(int)
    for v in merged.values():
        for r in v["reference"]:
            out[r["from"]] += 1
    return {k: out.get(k, 0) for k in ("gemini", "gptoss", "grok")}


def relevance_where_a_table_exists(trials: list[dict]) -> dict:
    """Return mean relevance per condition over the trials that produced a table.

    A trial without a table has no rows to judge; the fixed rule scores it 0.

    Parameters
    ----------
    trials : list of dict
        Scored trials.

    Returns
    -------
    dict
        ``{condition: {"trials": n, "relevance": mean}}``.
    """
    out = {}
    for cond in (B, A):
        xs = [t["relevance"] for t in trials if t["condition"] == cond and not t["is_error"]]
        out[cond] = {"trials": len(xs), "relevance": round(statistics.fmean(xs), 4)}
    return out


def full_tables_only(trials: list[dict]) -> dict:
    """Repeat the primary statistic on the trials whose table has the full ten rows.

    Coverage is a recall measure, so a longer table has more chances to cover a reference risk.
    Holding the number of rows at the cap removes that difference between conditions.

    Parameters
    ----------
    trials : list of dict
        Scored trials.

    Returns
    -------
    dict
        Trials kept per condition, strata with both conditions present, and the mean difference.
    """
    kept = [t for t in trials if t["rows_in_table"] == 10]
    scores = {k: c for k, c in cells(kept).items() if c[A] and c[B]}
    return {
        "trials": {c: sum(t["condition"] == c for t in kept) for c in (B, A)},
        "strata": len(scores),
        "coverage": {
            c: round(statistics.fmean(t["gemini"] for t in kept if t["condition"] == c), 4)
            for c in (B, A)
        },
        "delta_bar": round(delta_bar(scores), 4),
    }


def costs(trials: list[dict], runs: dict) -> dict:
    """Return mean cost per condition and model over the trials that did not end in an error.

    Parameters
    ----------
    trials : list of dict
        Scored trials.
    runs : dict
        Run records by trial id.

    Returns
    -------
    dict
        ``{condition: {model or "all": {measure: mean}}}``.
    """
    out: dict = {}
    for cond in (B, A):
        out[cond] = {}
        for model in [*MODELS, "all"]:
            sel = [
                t
                for t in trials
                if t["condition"] == cond and not t["is_error"] and model in (t["model"], "all")
            ]
            out[cond][model] = {
                "trials": len(sel),
                "seconds": round(statistics.fmean(runs[t["trial"]]["seconds"] for t in sel), 1),
                "turns": round(statistics.fmean(runs[t["trial"]]["num_turns"] for t in sel), 2),
                "output_tokens": round(
                    statistics.fmean(runs[t["trial"]]["output_tokens"] for t in sel)
                ),
                "rows": round(statistics.fmean(t["rows_in_table"] for t in sel), 2),
                "words": round(statistics.fmean(t["words"] for t in sel)),
            }
    return out


def verdicts(judge: str, trials: list[dict]) -> dict:
    """Return each judge decision as ``{(trial, item): covered}``.

    Parameters
    ----------
    judge : str
        ``gemini`` or ``grok``.
    trials : list of dict
        Scored trials. A trial that ended in an error has a verdict with nothing covered.

    Returns
    -------
    dict
        One boolean per reference risk of each trial.
    """
    out = {}
    for t in trials:
        v = json.loads((HERE / "judge" / judge / f"{t['trial']}.json").read_text())
        covered = set(v["covered"])
        for i in range(1, v["n"] + 1):
            out[(t["trial"], i)] = i in covered
    return out


def agreement(trials: list[dict]) -> dict:
    """Return item-level agreement between the two judges and Cohen's kappa.

    Parameters
    ----------
    trials : list of dict
        Scored trials. Pass only the trials with a table to leave out the decisions that both
        judges made on an empty answer.

    Returns
    -------
    dict
        Items compared, share of agreement, each judge's share of "covered", and kappa.
    """
    g, k = verdicts("gemini", trials), verdicts("grok", trials)
    keys = sorted(set(g) & set(k))
    n = len(keys)
    po = sum(g[x] == k[x] for x in keys) / n
    pg, pk = sum(g[x] for x in keys) / n, sum(k[x] for x in keys) / n
    pe = pg * pk + (1 - pg) * (1 - pk)
    return {
        "items": n,
        "agreement": round(po, 4),
        "covered_gemini": round(pg, 4),
        "covered_grok": round(pk, 4),
        "kappa": round((po - pe) / (1 - pe), 4),
    }


def by_item(trials: list[dict]) -> dict:
    """Return, per reference risk, the share of trials per condition that cover it (exploratory).

    Parameters
    ----------
    trials : list of dict
        Scored trials. Error trials count as not covering any risk, as in the fixed analysis.

    Returns
    -------
    dict
        Per-item rates and a summary: items that gain, lose or tie, and items no plain trial covers.
    """
    g = verdicts("gemini", trials)
    sizes = {
        task: v["n_reference"]
        for task, v in json.loads((HERE / "lists" / "merged.json").read_text()).items()
    }
    hits: dict = defaultdict(lambda: {A: 0, B: 0})
    runs_per: dict = defaultdict(lambda: {A: 0, B: 0})
    for t in trials:
        for i in range(1, sizes[t["task"]] + 1):
            runs_per[(t["task"], i)][t["condition"]] += 1
            hits[(t["task"], i)][t["condition"]] += bool(g.get((t["trial"], i), False))
    items = {
        f"{task}#{i}": {
            B: round(hits[(task, i)][B] / runs_per[(task, i)][B], 3),
            A: round(hits[(task, i)][A] / runs_per[(task, i)][A], 3),
        }
        for (task, i) in sorted(hits)
    }
    diffs = [v[A] - v[B] for v in items.values()]
    return {
        "items": items,
        "summary": {
            "reference_risks": len(items),
            "gain": sum(d > 0 for d in diffs),
            "tie": sum(d == 0 for d in diffs),
            "loss": sum(d < 0 for d in diffs),
            "gain_10_points_or_more": sum(d >= 0.1 for d in diffs),
            "loss_10_points_or_more": sum(d <= -0.1 for d in diffs),
            "never_covered_plain": sum(v[B] == 0 for v in items.values()),
            "never_covered_risk": sum(v[A] == 0 for v in items.values()),
            "never_covered_either": sum(v[A] == 0 and v[B] == 0 for v in items.values()),
            "covered_in_most_plain": sum(v[B] > 0.5 for v in items.values()),
            "covered_in_most_risk": sum(v[A] > 0.5 for v in items.values()),
        },
    }


def main() -> None:
    """Write ``descriptives.json`` and print one line (or the file with no ``--quiet``)."""
    trials, runs = load()
    scores = cells(trials)
    strata = {
        f"{task}|{model}": {
            B: round(statistics.fmean(c[B]), 4),
            A: round(statistics.fmean(c[A]), 4),
            "delta": round(statistics.fmean(c[A]) - statistics.fmean(c[B]), 4),
        }
        for (task, model), c in sorted(scores.items())
    }
    tasks = sorted({t["task"] for t in trials})
    per_task = {}
    for task in tasks:
        row = {}
        for model in MODELS:
            row[model] = strata[f"{task}|{model}"]
        row["delta"] = round(statistics.fmean(row[m]["delta"] for m in MODELS), 4)
        per_task[task] = row
    out = {
        "note": "Descriptive and exploratory. The confirmatory analysis is results.json.",
        "delta_bar": round(delta_bar(scores), 4),
        "bootstrap_95": bootstrap_interval(scores),
        "bootstrap_95_by_model": {
            m: bootstrap_interval({k: v for k, v in scores.items() if k[1] == m}) for m in MODELS
        },
        "per_task": per_task,
        "reference_risks_per_task": {
            task: v["n_reference"]
            for task, v in json.loads((HERE / "lists" / "merged.json").read_text()).items()
        },
        "costs": costs(trials, runs),
        "judges": agreement(trials),
        "judges_where_a_table_exists": agreement([t for t in trials if not t["is_error"]]),
        "relevance_where_a_table_exists": relevance_where_a_table_exists(trials),
        "wording_origin": wording_origin(),
        "full_tables_only": full_tables_only(trials),
        "null": null_distribution(cells_in_analysis_order(trials)),
        "by_item": by_item(trials),
    }
    (HERE / "descriptives.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    if "--quiet" in sys.argv:
        print(
            f"study 2 descriptives: delta {out['delta_bar']} "
            f"[{out['bootstrap_95'][0]}, {out['bootstrap_95'][1]}], kappa {out['judges']['kappa']}"
        )
    else:
        print(json.dumps({k: v for k, v in out.items() if k not in ("by_item", "null")}, indent=1))
        print(json.dumps(out["by_item"]["summary"], indent=1))


if __name__ == "__main__":
    main()
