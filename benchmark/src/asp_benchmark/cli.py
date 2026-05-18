"""Command-line entry point.

Usage:

  asp-benchmark run --mode mock --evals <dir> [--out <runs-root>]
  asp-benchmark run --mode real --model claude-opus-4-7 --evals <dir>
  asp-benchmark verify <run-id> [--runs <runs-root>]
  asp-benchmark list   [--runs <runs-root>]

The `run` command always produces a complete, verifiable run directory.
The `verify` command checks the hash chain. The `list` command summarises
prior runs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import env_fingerprint
from .adjudicator import adjudicate
from .eval_parser import parse_evals_dir
from .manifest import (
    RunLayout,
    build_manifest,
    make_run_id,
    utcnow,
    verify_manifest,
    write_adjudication,
    write_code_inventory,
    write_env,
    write_inputs,
    write_outputs,
)
from .report import render_report
from .runner import (
    Candidate,
    build_prompt,
    dispatch_mock,
    dispatch_real,
)


# Path math: __file__ is .../ASP/benchmark/src/asp_benchmark/cli.py
#   parents[0] = src/asp_benchmark
#   parents[1] = src
#   parents[2] = benchmark/
#   parents[3] = ASP/
_HERE = Path(__file__).resolve()
_BENCHMARK_DIR = _HERE.parents[2]
_ASP_ROOT = _HERE.parents[3]

DEFAULT_RUNS_ROOT = _BENCHMARK_DIR / "runs"
DEFAULT_CODE_ROOT = _HERE.parent
DEFAULT_EVALS_ROOT = (
    _ASP_ROOT / "skills" / "anticipating-shadow-points" / "evals"
)
DEFAULT_FIXTURES_ROOT = _BENCHMARK_DIR / "tests" / "fixtures" / "mock_runs"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="asp-benchmark",
        description="Reproducible benchmark with cryptographic provenance for ASP.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run the benchmark")
    run_p.add_argument(
        "--mode",
        choices=["mock", "real"],
        required=True,
        help="`mock` reads canned outputs from fixtures (deterministic, CI-safe). "
             "`real` calls claude -p (costs inference; non-deterministic transcripts).",
    )
    run_p.add_argument("--evals", type=Path, default=DEFAULT_EVALS_ROOT,
                       help="Directory containing eval markdown files.")
    run_p.add_argument("--out", type=Path, default=DEFAULT_RUNS_ROOT,
                       help="Root directory for run outputs.")
    run_p.add_argument("--model", default="claude-opus-4-7",
                       help="Model identifier (real mode only).")
    run_p.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES_ROOT,
                       help="Mock fixtures root (mock mode only).")
    run_p.add_argument("--max-turns", type=int, default=1)

    verify_p = sub.add_parser("verify", help="Verify a previous run's hash chain")
    verify_p.add_argument("run_id", type=str)
    verify_p.add_argument("--runs", type=Path, default=DEFAULT_RUNS_ROOT)

    list_p = sub.add_parser("list", help="List previous runs")
    list_p.add_argument("--runs", type=Path, default=DEFAULT_RUNS_ROOT)

    args = parser.parse_args(argv)

    if args.cmd == "run":
        return _cmd_run(args)
    elif args.cmd == "verify":
        return _cmd_verify(args)
    elif args.cmd == "list":
        return _cmd_list(args)
    return 2


def _cmd_run(args: argparse.Namespace) -> int:
    started_at = utcnow()
    env = env_fingerprint.capture()
    run_id = make_run_id(env, started_at)
    layout = RunLayout.for_run(args.out, run_id)
    layout.ensure()

    specs = parse_evals_dir(args.evals)
    if not specs:
        print(f"no evals found under {args.evals}", file=sys.stderr)
        return 1
    print(f"loaded {len(specs)} evals from {args.evals}")
    print(f"run_id: {run_id}")

    candidates: list[Candidate] = []
    prompts_text: dict[tuple[str, str], str] = {}

    for spec in specs:
        for condition in ("RED", "GREEN"):
            prompts_text[(spec.eval_id, condition)] = build_prompt(spec, condition)
            if args.mode == "mock":
                cand = dispatch_mock(
                    spec, condition, fixtures_root=args.fixtures
                )
            else:
                cand = dispatch_real(
                    spec, condition,
                    model=args.model,
                    max_turns=args.max_turns,
                )
            candidates.append(cand)
            print(
                f"  {spec.eval_id}/{condition}: "
                f"text_sha256={cand.text_sha256[:12]}... "
                f"refusal={cand.refusal_detected} "
                f"terminal={cand.terminal_reason}"
            )

    # Adjudicate every candidate against its eval spec.
    coverages = []
    by_eval = {s.eval_id: s for s in specs}
    for cand in candidates:
        spec = by_eval[cand.eval_id]
        cov = adjudicate(
            spec,
            candidate_text=cand.text,
            candidate_label=cand.condition,
            candidate_text_sha256=cand.text_sha256,
        )
        coverages.append(cov)

    # Persist everything.
    write_env(layout, env)
    write_code_inventory(layout, DEFAULT_CODE_ROOT)
    write_inputs(layout, candidates, prompts_text)
    write_outputs(layout, candidates)
    write_adjudication(layout, coverages)

    finished_at = utcnow()
    manifest = build_manifest(
        layout,
        started_at=started_at,
        finished_at=finished_at,
        mode=args.mode,
        model=args.model,
        eval_count=len(specs),
        candidate_count=len(candidates),
    )

    report_md = render_report(
        run_dir=layout.run_dir,
        started_at=started_at,
        finished_at=finished_at,
        mode=args.mode,
        model=args.model,
        env=env,
        specs=specs,
        coverages=coverages,
        manifest_hash=manifest["manifest_hash"],
    )
    (layout.run_dir / "report.md").write_text(report_md, encoding="utf-8")

    print(f"\nrun complete: {layout.run_dir}")
    print(f"manifest_hash: {manifest['manifest_hash']}")
    print(f"to verify: asp-benchmark verify {run_id}")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    run_dir = args.runs / args.run_id
    if not run_dir.exists():
        print(f"no such run: {run_dir}", file=sys.stderr)
        return 1
    issues = verify_manifest(run_dir)
    if not issues:
        print(f"OK: {run_dir} hash chain intact")
        return 0
    print(f"TAMPER or DRIFT detected in {run_dir}:")
    for issue in issues:
        print(f"  - {issue}")
    return 1


def _cmd_list(args: argparse.Namespace) -> int:
    if not args.runs.exists():
        print(f"no runs at {args.runs}")
        return 0
    for run_dir in sorted(args.runs.iterdir()):
        if not run_dir.is_dir():
            continue
        manifest_path = run_dir / "manifest.json"
        if manifest_path.exists():
            import json
            m = json.loads(manifest_path.read_text(encoding="utf-8"))
            print(
                f"{run_dir.name}\t"
                f"mode={m.get('mode')}\t"
                f"model={m.get('model')}\t"
                f"hash={m.get('manifest_hash', '?')[:16]}..."
            )
        else:
            print(f"{run_dir.name}\t(no manifest)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
