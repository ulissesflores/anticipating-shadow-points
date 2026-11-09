"""Single entry point: results -> figures -> tests -> provenance -> verify.

``python run_all.py`` re-derives every published number from committed data,
regenerates the figures, runs both test suites (``tests/``, which asserts each
number the papers compute, and ``benchmark/tests/``), rebuilds the hash seal and
verifies it. It makes no network or
model calls. Exit code 0 means the whole chain held.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STEPS = [
    ("results", [sys.executable, "analysis/results.py"]),
    ("study results", [sys.executable, "benchmark/study-2026-11/analyze.py", "results", "5"]),
    ("figures", [sys.executable, "analysis/make_figures.py"]),
    ("tests", [sys.executable, "-m", "pytest", "-q", "tests"]),
    (
        "benchmark tests",
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-o",
            "addopts=",
            "-c",
            "benchmark/pyproject.toml",
            "benchmark/tests",
        ],
    ),
    ("provenance", [sys.executable, "make_provenance.py"]),
    ("verify", [sys.executable, "make_provenance.py", "--verify"]),
]


def main() -> int:
    """Run every step in order and stop at the first failure.

    Returns
    -------
    int
        0 on success, otherwise the failing step's exit code.
    """
    for name, cmd in STEPS:
        print(f"== {name}: {' '.join(cmd[1:])}", flush=True)
        env = {**os.environ, "PYTHONPATH": str(ROOT / "benchmark" / "src")}
        code = subprocess.call(cmd, cwd=ROOT, env=env)
        if code != 0:
            print(f"run_all FAILED at step '{name}' (exit {code})")
            return code
    print("run_all OK: results reproduced, tests passed, provenance verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
