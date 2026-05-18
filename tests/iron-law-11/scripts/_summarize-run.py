#!/usr/bin/env python3
"""Aggregate per-trial wall_clock.json records into a run-summary.json.

Internal helper called by run-protocol.sh once all trials complete.
Does not perform adjudication or statistics — that is analyze.py's job.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 5:
        print("usage: _summarize-run.py <run_dir> <mode> <model> <max_turns>",
              file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    mode, model, max_turns = sys.argv[2], sys.argv[3], int(sys.argv[4])

    trials_dir = run_dir / "trials"
    trial_records = []
    for tdir in sorted(trials_dir.iterdir()):
        if not tdir.is_dir():
            continue
        sid = tdir.name
        wc = json.loads((tdir / "wall_clock.json").read_text(encoding="utf-8"))
        trial_records.append({
            "scenario_id": sid,
            "exit_code": wc["exit_code"],
            "terminal_reason": wc["terminal_reason"],
            "is_error": wc["is_error"],
            "elapsed_seconds": wc["elapsed_seconds"],
            "result_bytes": wc["result_bytes"],
        })

    total_seconds = sum(r["elapsed_seconds"] for r in trial_records)
    summary = {
        "run_id": run_dir.name,
        "mode": mode,
        "model": model,
        "max_turns": max_turns,
        "trial_count": len(trial_records),
        "total_elapsed_seconds": total_seconds,
        "trials": trial_records,
    }
    out = run_dir / "run-summary.json"
    out.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {out} ({len(trial_records)} trials, "
          f"{total_seconds}s total wall-clock)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
