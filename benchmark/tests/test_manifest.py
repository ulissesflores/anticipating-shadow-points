"""End-to-end test of run/verify with mock-mode fixtures.

Goes through the entire pipeline: parse evals, dispatch mock candidates,
adjudicate, build manifest, and re-verify. Then flips one byte under the
run directory and confirms verify catches the tamper.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from asp_benchmark import env_fingerprint
from asp_benchmark.adjudicator import adjudicate
from asp_benchmark.eval_parser import parse_eval
from asp_benchmark.manifest import (
    RunLayout,
    build_manifest,
    make_run_id,
    verify_manifest,
    write_adjudication,
    write_code_inventory,
    write_env,
    write_inputs,
    write_outputs,
)
from asp_benchmark.runner import build_prompt, dispatch_mock


_EVAL_FIXTURE = """\
# Eval 01 — Manifest test eval

## INPUT

Task: "Add an idempotent retry to a flaky downstream call."

## EXPECTED SHADOW POINTS (>=3 required; >=66% coverage required for eval pass)

1. **Idempotency key** — the downstream must accept idempotency keys or duplicates may post twice.
2. **Backoff strategy** — exponential backoff with jitter to avoid thundering herd.
3. **Dead-letter** — after N failed retries, route to a dead-letter sink and alert.

## ACCEPTANCE

The eval passes if >=66% of the expected shadow points are covered.
"""

_GREEN_FIXTURE = """\
Plan with ASP discipline:

1. Use an idempotency key on every retry so the downstream service does
   not double-apply the side effect.
2. Apply exponential backoff with jitter between retries to avoid a
   thundering herd when many callers fail at once.
3. After 5 retries, route the request to a dead-letter sink and emit a
   pager alert for human follow-up.
"""

_RED_FIXTURE = """\
Plan as a senior engineer:

I will add a try/except around the call and retry once on failure with a
fixed 100ms sleep. If it fails again I will log and move on. This should
handle most flake cases without overengineering.
"""


def _stage_fixtures(tmp_path: Path) -> tuple[Path, Path]:
    evals_dir = tmp_path / "evals"
    evals_dir.mkdir()
    (evals_dir / "01-retry.md").write_text(_EVAL_FIXTURE, encoding="utf-8")

    fixtures_dir = tmp_path / "mock_fixtures"
    (fixtures_dir / "E1").mkdir(parents=True)
    (fixtures_dir / "E1" / "RED.md").write_text(_RED_FIXTURE, encoding="utf-8")
    (fixtures_dir / "E1" / "GREEN.md").write_text(_GREEN_FIXTURE, encoding="utf-8")
    return evals_dir, fixtures_dir


def _do_run(tmp_path: Path) -> Path:
    evals_dir, fixtures_dir = _stage_fixtures(tmp_path)
    runs_root = tmp_path / "runs"
    code_root = Path(__file__).resolve().parents[1] / "src" / "asp_benchmark"

    started_at = datetime(2026, 5, 17, 12, 0, 0, tzinfo=timezone.utc)
    env = env_fingerprint.capture()
    run_id = make_run_id(env, started_at)
    layout = RunLayout.for_run(runs_root, run_id)
    layout.ensure()

    specs = [parse_eval(evals_dir / "01-retry.md")]
    prompts_text = {}
    candidates = []
    for spec in specs:
        for condition in ("RED", "GREEN"):
            prompts_text[(spec.eval_id, condition)] = build_prompt(spec, condition)
            candidates.append(dispatch_mock(spec, condition, fixtures_root=fixtures_dir))

    coverages = [
        adjudicate(
            specs[0],
            candidate_text=c.text,
            candidate_label=c.condition,
            candidate_text_sha256=c.text_sha256,
        )
        for c in candidates
    ]

    write_env(layout, env)
    write_code_inventory(layout, code_root)
    write_inputs(layout, candidates, prompts_text)
    write_outputs(layout, candidates)
    write_adjudication(layout, coverages)
    build_manifest(
        layout,
        started_at=started_at,
        finished_at=started_at,
        mode="mock",
        model="mock",
        eval_count=len(specs),
        candidate_count=len(candidates),
    )
    return layout.run_dir


def test_run_then_verify_intact(tmp_path: Path):
    run_dir = _do_run(tmp_path)
    assert verify_manifest(run_dir) == []


def test_tamper_with_output_is_detected(tmp_path: Path):
    run_dir = _do_run(tmp_path)
    # Pick one output file and flip a byte.
    out_path = run_dir / "outputs" / "E1" / "GREEN.text.txt"
    text = out_path.read_text(encoding="utf-8")
    out_path.write_text(text + "tamper", encoding="utf-8")
    issues = verify_manifest(run_dir)
    assert issues, "expected at least one discrepancy after tampering"
    assert any("outputs" in i for i in issues)


def test_tamper_with_adjudication_is_detected(tmp_path: Path):
    run_dir = _do_run(tmp_path)
    adj_path = run_dir / "adjudication" / "E1" / "RED.json"
    data = adj_path.read_bytes()
    adj_path.write_bytes(data + b"\n")  # single trailing-byte flip
    issues = verify_manifest(run_dir)
    assert issues
    assert any("adjudication" in i for i in issues)


def test_green_beats_red_on_synthetic_fixtures(tmp_path: Path):
    """Smoke story the fixtures must support: GREEN coverage strictly
    exceeds RED coverage, AND GREEN passes the acceptance threshold of
    the eval (>=66% on this fixture). We deliberately do NOT require
    GREEN == 1.0 — the Jaccard match layer has finite recall on real
    paraphrases (e.g. "exponential backoff with jitter" does not match
    "Backoff strategy" because "strategy" never appears), and gaming
    the fixture to hit 100% would conceal that property of the matcher.
    The test instead pins the directional claim that the benchmark
    advertises."""
    run_dir = _do_run(tmp_path)
    import json
    red = json.loads((run_dir / "adjudication" / "E1" / "RED.json").read_text())
    green = json.loads((run_dir / "adjudication" / "E1" / "GREEN.json").read_text())
    assert green["coverage"] > red["coverage"], (
        f"GREEN ({green['coverage']}) must beat RED ({red['coverage']})"
    )
    # The fixture eval declares >=66% acceptance.
    assert green["coverage"] >= 0.66
