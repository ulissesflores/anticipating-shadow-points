"""Unplanned sensitivity check for study 2 (2026-11b): the three network-error trials.

Trials ``t097``, ``t099`` and ``t100`` ended in a network error and count as 0 under the fixed
rule. All three are ``RED-plain``, so that rule favours the hypothesis. This script repeats the
primary analysis of ``analyze.py`` (same statistic, same permutation test, same seed) two ways:
without the three strata that hold those trials, and without the three trials only. It was
written after the errors were seen and has no decision rule of its own.

Usage::

    python sensitivity.py [--quiet]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from analyze import MODELS, A, B, delta, permutation_p

HERE = Path(__file__).resolve().parent


def run() -> dict:
    """Recompute delta and p for each judge scorer under both exclusions.

    Returns
    -------
    dict
        ``{scorer: {exclusion: {delta_bar, p, by_model, p_by_model, strata}}}``.
    """
    rows = json.loads((HERE / "results.json").read_text())["trials"]
    bad = {(r["task"], r["model"]) for r in rows if r["is_error"]}
    out = {"error_trials": sorted(r["trial"] for r in rows if r["is_error"])}
    for scorer in ("gemini", "grok", "relevance"):
        out[scorer] = {}
        for name in ("without_strata", "without_trials"):
            cells: dict = {}
            for r in rows:
                key = (r["task"], r["model"])
                if (name == "without_strata" and key in bad) or (
                    name == "without_trials" and r["is_error"]
                ):
                    continue
                cells.setdefault(f"{key[0]}|{key[1]}", {A: [], B: []})[r["condition"]].append(
                    r[scorer]
                )
            part = {m: {k: c for k, c in cells.items() if k.endswith(m)} for m in MODELS}
            out[scorer][name] = {
                "strata": len(cells),
                "delta_bar": round(delta(cells)[0], 4),
                "p": round(permutation_p(cells), 4),
                "by_model": {m: round(delta(part[m])[0], 4) for m in MODELS},
                "p_by_model": {m: round(permutation_p(part[m]), 4) for m in MODELS},
            }
    (HERE / "sensitivity.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    out = run()
    if "--quiet" in sys.argv:
        g = out["gemini"]["without_strata"]
        print(
            f"study2 sensitivity -> sensitivity.json | without the {len(out['error_trials'])} "
            f"network-error strata: delta {g['delta_bar']:+.3f}, p = {g['p']}"
        )
    else:
        print(json.dumps(out, indent=1))
