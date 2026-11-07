"""The derivation is deterministic and matches the committed output."""

from __future__ import annotations

import json
from pathlib import Path

import results as results_module

ROOT = Path(__file__).resolve().parent.parent


def test_two_runs_identical():
    """Two derivations in one process produce identical documents."""
    assert results_module.compute() == results_module.compute()


def test_committed_output_matches(results):
    """``output/results.json`` equals a fresh derivation (no stale commit)."""
    committed = json.loads((ROOT / "output" / "results.json").read_text(encoding="utf-8"))
    assert committed == json.loads(json.dumps(results))


def test_extract_carries_no_personal_identifiers():
    """The published July extract holds no e-mail address or local scratch path."""
    text = (ROOT / "data" / "spike-2026-07-08" / "trials.jsonl").read_text(encoding="utf-8")
    assert "@gmail.com" not in text
    assert "/private/tmp/" not in text
