"""Unit tests for deterministic adjudication.

Adjudication MUST be a pure function: same EvalSpec + same candidate text
⇒ same Coverage. These tests pin that invariant plus a handful of
behavioural contracts on each match layer.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from asp_benchmark.adjudicator import (
    JACCARD_THRESHOLD,
    adjudicate,
)
from asp_benchmark.eval_parser import EvalSpec, ShadowPoint


def _make_spec(tmp_path: Path, points: list[tuple[str, str]]) -> EvalSpec:
    """Build a minimal EvalSpec on disk so the synonyms sidecar lookup
    resolves to an empty dict (file absent ⇒ no synonyms)."""
    source = tmp_path / "fake-eval.md"
    source.write_text("# Eval 99 — fake\n", encoding="utf-8")
    return EvalSpec(
        eval_id="E99",
        title="fake",
        input_prompt="irrelevant for adjudication",
        expected=tuple(
            ShadowPoint(index=i + 1, name=name, description=desc)
            for i, (name, desc) in enumerate(points)
        ),
        acceptance_threshold=0.80,
        source_path=source,
    )


def test_exact_name_match_layer_one(tmp_path: Path):
    spec = _make_spec(tmp_path, [
        ("RLS policy update", "row-level security needs review"),
    ])
    cand = "We will ensure RLS policy update is performed before deploy."
    cov = adjudicate(spec, cand, candidate_label="RED", candidate_text_sha256="0" * 64)
    assert len(cov.matched) == 1
    assert cov.matched[0].matched_via == "exact_name"
    assert len(cov.unmatched) == 0
    assert cov.coverage == 1.0


def test_jaccard_paraphrase_match_layer_three(tmp_path: Path):
    spec = _make_spec(tmp_path, [
        ("Replica lag", "replication slot may fall behind during migration window"),
    ])
    # Paraphrase: doesn't contain "replica lag" verbatim, but tokens overlap.
    cand = (
        "Heads-up: during a long migration window the replication "
        "may fall behind on the read replicas; monitor the slot."
    )
    cov = adjudicate(spec, cand, candidate_label="GREEN", candidate_text_sha256="1" * 64)
    assert len(cov.matched) == 1
    assert cov.matched[0].matched_via == "jaccard"
    assert cov.matched[0].jaccard_score >= JACCARD_THRESHOLD


def test_no_match_layer_four(tmp_path: Path):
    spec = _make_spec(tmp_path, [
        ("Trigger interaction", "BEFORE INSERT/UPDATE triggers may fire unexpectedly"),
    ])
    # Entirely unrelated candidate text.
    cand = "I will use a recursive descent parser to handle the grammar."
    cov = adjudicate(spec, cand, candidate_label="RED", candidate_text_sha256="2" * 64)
    assert len(cov.matched) == 0
    assert len(cov.unmatched) == 1
    assert cov.unmatched[0].best_jaccard < JACCARD_THRESHOLD


def test_synonym_sidecar_match_layer_two(tmp_path: Path):
    """Layer 2 fires when expected name doesn't appear but a synonym does,
    even if the Jaccard window similarity is low."""
    spec = _make_spec(tmp_path, [
        ("RLS policy update", "row-level security needs review"),
    ])
    # Write the synonyms sidecar next to the eval source.
    sidecar = spec.source_path.with_suffix(".synonyms.json")
    sidecar.write_text(
        '{"synonyms": {"RLS policy update": ["row-level security check"]}}',
        encoding="utf-8",
    )
    cand = "ensure a row-level security check is in place before shipping"
    cov = adjudicate(spec, cand, candidate_label="GREEN", candidate_text_sha256="3" * 64)
    assert len(cov.matched) == 1
    assert cov.matched[0].matched_via == "synonym"


def test_adjudication_is_deterministic(tmp_path: Path):
    spec = _make_spec(tmp_path, [
        ("Replica lag", "replication slot may fall behind"),
        ("Trigger interaction", "BEFORE INSERT/UPDATE triggers may fire"),
        ("Lock contention", "ALTER TABLE blocks reads/writes"),
    ])
    cand = (
        "Plan: we will run the ALTER TABLE during low-traffic window. "
        "Note that BEFORE INSERT and UPDATE triggers may fire on the new "
        "column. Replication slot needs to be monitored for fall behind."
    )
    cov1 = adjudicate(spec, cand, candidate_label="RED", candidate_text_sha256="4" * 64)
    cov2 = adjudicate(spec, cand, candidate_label="RED", candidate_text_sha256="4" * 64)
    assert cov1.as_dict() == cov2.as_dict()


def test_coverage_is_matched_over_total(tmp_path: Path):
    spec = _make_spec(tmp_path, [
        ("Alpha", "first thing"),
        ("Beta", "second thing"),
        ("Gamma", "third thing"),
        ("Delta", "fourth thing"),
    ])
    cand = "Discuss alpha and beta only; the rest is out of scope."
    cov = adjudicate(spec, cand, candidate_label="RED", candidate_text_sha256="5" * 64)
    assert len(cov.matched) == 2
    assert len(cov.unmatched) == 2
    assert cov.coverage == 0.5
