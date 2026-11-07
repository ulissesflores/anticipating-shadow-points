"""Single entry point: results -> figures -> tests -> provenance -> verify.

``python run_all.py`` re-derives every published number from committed data,
regenerates the figures, runs the test suite (which asserts each number the
papers cite), rebuilds the hash seal and verifies it. It makes no network or
model calls. Exit code 0 means the whole chain held.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STEPS = [
    ("results", [sys.executable, "analysis/results.py"]),
    ("figures", [sys.executable, "analysis/make_figures.py"]),
    ("tests", [sys.executable, "-m", "pytest", "-q", "tests"]),
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
        code = subprocess.call(cmd, cwd=ROOT)
        if code != 0:
            print(f"run_all FAILED at step '{name}' (exit {code})")
            return code
    print("run_all OK: results reproduced, tests passed, provenance verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
