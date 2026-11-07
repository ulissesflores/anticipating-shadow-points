"""Shared fixtures: compute the results once per test session."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))

import results as results_module  # noqa: E402


@pytest.fixture(scope="session")
def results() -> dict:
    """Return a fresh, in-memory derivation of ``output/results.json``.

    Returns
    -------
    dict
        The full results document.
    """
    return results_module.compute()
