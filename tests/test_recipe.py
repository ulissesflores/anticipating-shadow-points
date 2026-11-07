"""Run the defensive recipe printed in ``paper/iron-law-11.md`` section 6.

The bash block is extracted from the paper itself and executed against every
trial of the July 2026 extract, so the paper cannot print a recipe that
behaves differently from what it reports. Requires ``bash`` and ``jq``.
"""

from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SPIKE = ROOT / "data" / "spike-2026-07-08"

pytestmark = pytest.mark.skipif(shutil.which("jq") is None, reason="jq not installed")


def recipe() -> str:
    """Extract the recipe from the paper, minus the live ``claude -p`` call.

    Returns
    -------
    str
        A bash script that reads ``out.json`` and takes the exit code from
        the ``FAKE_RC`` environment variable.
    """
    paper = (ROOT / "paper" / "iron-law-11.md").read_text(encoding="utf-8")
    block = re.search(r"```bash\n(# 1\. Always request JSON output.*?)```", paper, re.S)
    lines, skip = [], False
    for ln in block.group(1).splitlines():
        if ln.startswith("claude -p ") or skip:
            skip = ln.endswith("\\")  # drop the live call and its continuation lines
            continue
        lines.append(ln)
    return "\n".join("RC=$FAKE_RC" if ln == "RC=$?" else ln for ln in lines) + "\n"


def outcomes(tmp_path: Path) -> Counter:
    """Count recipe exit codes per adjudicated class over the 50 trials.

    Parameters
    ----------
    tmp_path : Path
        Scratch directory for ``out.json`` and the script.

    Returns
    -------
    Counter
        ``(class, recipe_exit_code) -> trials``.
    """
    script = tmp_path / "recipe.sh"
    script.write_text(recipe(), encoding="utf-8")
    with (SPIKE / "adjudication.tsv").open(encoding="utf-8") as fh:
        labels = {r["scenario_id"]: r["class"] for r in csv.DictReader(fh, delimiter="\t")}
    counts: Counter = Counter()
    for line in (SPIKE / "trials.jsonl").read_text(encoding="utf-8").splitlines():
        trial = json.loads(line)
        envelope = {
            "type": "result",
            "stop_reason": trial["stop_reason"],
            "terminal_reason": trial["terminal_reason"],
            "result": trial["result_text"],
        }
        (tmp_path / "out.json").write_text(json.dumps(envelope), encoding="utf-8")
        env = {**os.environ, "FAKE_RC": str(trial["exit_code"])}
        code = subprocess.run(["bash", str(script)], cwd=tmp_path, env=env, capture_output=True)
        counts[(labels[trial["scenario_id"]], code.returncode)] += 1
    return counts


def test_recipe_on_july_extract(tmp_path):
    """Caps exit 3, the block exits 4, 19 of 20 declines exit 2, no completion is flagged."""
    assert outcomes(tmp_path) == Counter(
        {
            ("turn_cap", 3): 25,
            ("server_block", 4): 1,
            ("safety_refusal", 2): 11,
            ("destructive_refusal", 2): 1,
            ("impossible_decline", 2): 7,
            ("impossible_decline", 0): 1,
            ("legit_completion", 0): 4,
        }
    )


@pytest.mark.parametrize(
    ("envelope", "rc", "expected"),
    [
        ({}, 1, 1),
        ({"type": "result", "stop_reason": "end_turn", "result": "Done."}, 0, 0),
        ({"type": "result", "stop_reason": "end_turn", "result": "ok"}, 2, 1),
        ({"type": "result", "stop_reason": "pause_turn", "result": "..."}, 0, 6),
        (
            [
                {"type": "system", "subtype": "init"},
                {"type": "result", "stop_reason": "end_turn", "result": "I won't do this."},
            ],
            0,
            2,
        ),
        (
            [{"type": "system"}, {"type": "result", "terminal_reason": "max_turns"}],
            1,
            3,
        ),
        # The documented object form carries no "type": the gate must still read it.
        ({"stop_reason": "end_turn", "result": "Done."}, 0, 0),
        ({"stop_reason": "end_turn", "result": "I won't do this."}, 0, 2),
    ],
)
def test_recipe_edge_cases(tmp_path, envelope, rc, expected):
    """No result event fails, a delivery passes, arrays are read, other exits and reasons fail."""
    script = tmp_path / "recipe.sh"
    script.write_text(recipe(), encoding="utf-8")
    (tmp_path / "out.json").write_text(json.dumps(envelope), encoding="utf-8")
    env = {**os.environ, "FAKE_RC": str(rc)}
    code = subprocess.run(["bash", str(script)], cwd=tmp_path, env=env, capture_output=True)
    assert code.returncode == expected
