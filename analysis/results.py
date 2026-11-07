"""Derive every number the two papers cite from committed data.

Inputs are all in the repository and never change:

* ``tests/iron-law-11/runs/published/2026-05-18T15-36-05Z-c1bceb85`` -- the
  May 2026 `claude -p` run (frozen evidence, hash-locked inputs).
* ``data/spike-2026-07-08/`` -- the redacted July 2026 re-measurement and the
  author/codebook labels.
* ``benchmark/runs/published/2026-05-18T00-27-43Z-b0a1bc7b`` -- a MOCK-mode run of
  the benchmark package: its RED/GREEN texts are fixtures the author wrote to
  exercise the adjudicator (``benchmark/PROTOCOL.md`` section 8), not model
  outputs. It exercises the instrument; it says nothing about ASP's effect.

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
    # The lock file's confusion matrix: exit 0 read as "success", the detector as truth.
    true_success = sum(t.exit_zero and not t.refused for t in trials)
    false_alarm = [t for t in trials if not t.exit_zero and not t.refused]
    by_category = {
        cat: {
            "n": sum(t.category == cat for t in trials),
            "exit0": sum(t.category == cat and t.exit_zero for t in trials),
        }
        for cat in sorted({t.category for t in trials})
    }
    return {
        "claude_code_version": "2.1.143",
        "model": summary["model"],
        "max_turns": summary["max_turns"],
        "n": len(trials),
        "exit0": exit0,
        "detector_silent_refusals": _rate(silent, len(trials), analyze),
        "lock_file_confusion": {
            "true_success": true_success,
            "silent_refusal": silent,
            "false_alarm": len(false_alarm),
            "false_alarm_turn_cap": sum(t.terminal_reason == "max_turns" for t in false_alarm),
            "precision": round(true_success / exit0, 4),
            "recall": round(true_success / (true_success + len(false_alarm)), 4),
            "misclassification": round((silent + len(false_alarm)) / len(trials), 4),
        },
        "by_category": by_category,
    }


def _entropy(counts) -> float:
    """Shannon entropy in bits of a frequency table.

    Parameters
    ----------
    counts : iterable of int
        Frequencies (zeros allowed).

    Returns
    -------
    float
        Entropy in bits.
    """
    counts = [c for c in counts if c]
    total = sum(counts)
    return -sum(c / total * math.log2(c / total) for c in counts)


def outcome_information(trials: list[dict], labels: dict, label_key: str) -> dict:
    """How much of the task outcome each envelope channel carries.

    Each trial gets one of four outcomes: ``cut`` (stopped by the turn cap),
    ``blocked`` (server-side safety block), ``declined`` (exit 0 and labelled a
    decline) or ``done`` (exit 0 and labelled a delivery). The mutual information
    between that outcome and a channel, divided by the outcome entropy, is the
    share of the outcome a wrapper can recover by reading that channel alone.

    Parameters
    ----------
    trials : list of dict
        Records from ``trials.jsonl``.
    labels : dict
        Rows of ``adjudication.tsv`` keyed by scenario id.
    label_key : str
        ``"author_label"`` or ``"codebook_majority"``.

    Returns
    -------
    dict
        Outcome counts, the outcome entropy in bits, and for each channel
        (exit code; exit code plus ``stop_reason``) the mutual information in
        bits and as a share of the entropy; ``delivered`` repeats the measure
        for the binary question "was the task delivered?".
    """

    def outcome(t: dict) -> str:
        """Four-way task outcome of one trial."""
        cls = labels[t["scenario_id"]]["class"]
        if cls == "turn_cap":
            return "cut"
        if cls == "server_block":
            return "blocked"
        return "declined" if labels[t["scenario_id"]][label_key] == "DECLINE" else "done"

    outcomes = [outcome(t) for t in trials]

    def info(target: list, channel) -> dict:
        """Mutual information between a target labelling and one channel."""
        h = _entropy(Counter(target).values())
        groups: dict = {}
        for t, o in zip(trials, target, strict=True):
            groups.setdefault(channel(t), []).append(o)
        h_cond = sum(len(g) / len(trials) * _entropy(Counter(g).values()) for g in groups.values())
        return {"bits": round(h - h_cond, 4), "share": round((h - h_cond) / h, 4)}

    def exit_code(t: dict):
        """Return the process exit code."""
        return t["exit_code"]

    def exit_and_stop(t: dict):
        """Return the exit code paired with the envelope's ``stop_reason``."""
        return (t["exit_code"], t["stop_reason"])

    # The question a wrapper actually asks: was the task delivered?
    delivered = ["done" if o == "done" else "not_done" for o in outcomes]
    return {
        "outcomes": dict(sorted(Counter(outcomes).items())),
        "entropy_bits": round(_entropy(Counter(outcomes).values()), 4),
        "exit_code": info(outcomes, exit_code),
        "exit_code_and_stop_reason": info(outcomes, exit_and_stop),
        "residual_bits": round(
            _entropy(Counter(outcomes).values()) - info(outcomes, exit_and_stop)["bits"], 4
        ),
        "delivered": {
            "entropy_bits": round(_entropy(Counter(delivered).values()), 4),
            "exit_code": info(delivered, exit_code),
            "exit_code_and_stop_reason": info(delivered, exit_and_stop),
        },
    }


def _identical_raters() -> int:
    """Count the blind raters whose label vector equals R1's, R1 included.

    Returns
    -------
    int
        Number of raters among R1-R5 with the same labels as R1 on every trial.
    """
    with (SPIKE / "rater-matrix.tsv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    return sum(all(r[name] == r["R1"] for r in rows) for name in ("R1", "R2", "R3", "R4", "R5"))


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
        "exit1_by_category": {
            cat: f"{sum(t['category'] == cat and t['exit_code'] != 0 for t in trials)}"
            f"/{sum(t['category'] == cat for t in trials)}"
            for cat in sorted({t["category"] for t in trials})
        },
        "declines_given_exit0": {
            "author": f"{author}/{len(exit0)}",
            "codebook": f"{codebook}/{len(exit0)}",
            "core": f"{core}/{len(exit0)}",
        },
        "opus_48_exit0": {
            "trials": sum("claude-opus-4-8" in t["answering_models"] for t in exit0),
            "author_declines": sum(
                "claude-opus-4-8" in t["answering_models"]
                and labels[t["scenario_id"]]["author_label"] == "DECLINE"
                for t in exit0
            ),
        },
        "raters_identical_to_r1": _identical_raters(),
        "outcome_information": {
            "author": outcome_information(trials, labels, "author_label"),
            "codebook": outcome_information(trials, labels, "codebook_majority"),
        },
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
        Run mode, per-eval coverage of the RED/GREEN fixtures (committed and
        re-scored with the shipped matcher), matches per matcher layer, the 5x5
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
    texts = {
        cond: {
            eid: (BENCH_RUN / "outputs" / eid / f"{cond}.text.txt").read_text(encoding="utf-8")
            for eid in ids
        }
        for cond in ("RED", "GREEN")
    }
    green = texts["GREEN"]
    # Re-score both conditions with the shipped matcher, so the committed adjudication
    # files cannot drift from the code without the tests noticing.
    rescored = {
        cond: {eid: adjudicate(specs[eid], texts[cond][eid], cond, "check").coverage for eid in ids}
        for cond in ("RED", "GREEN")
    }
    e2_red = json.loads(
        (BENCH_RUN / "adjudication" / "E2" / "RED.json").read_text(encoding="utf-8")
    )
    rate_limit_jaccard = next(
        u["best_jaccard"] for u in e2_red["unmatched"] if u["name"] == "Rate-limit backoff"
    )
    layers = Counter(
        m["matched_via"]
        for cond in ("RED", "GREEN")
        for eid in ids
        for m in json.loads(
            (BENCH_RUN / "adjudication" / eid / f"{cond}.json").read_text(encoding="utf-8")
        )["matched"]
    )
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
        "rescored_coverage": rescored,
        "matches_by_layer": dict(sorted(layers.items())),
        "e2_red_rate_limit_best_jaccard": round(rate_limit_jaccard, 2),
        "red_mean": round(sum(rescored["RED"].values()) / len(ids), 4),
        "green_mean": round(sum(rescored["GREEN"].values()) / len(ids), 4),
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
