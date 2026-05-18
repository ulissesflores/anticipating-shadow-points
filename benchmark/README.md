# ASP Benchmark

A reproducible benchmark with cryptographic provenance for **Anticipating
Shadow Points (ASP)**. Read [`PROTOCOL.md`](./PROTOCOL.md) for the
scientific specification; this file is the operational quick-start.

## Why this exists

The companion preprint reports a RED → GREEN coverage lift of ≈47% →
≈100% on five engineering evaluations. That measurement was hand-adjudicated
by the author and is preliminary. This benchmark replaces hand-adjudication
with a deterministic algorithm, hashes every byte of input/output/code/env,
and produces a run directory that anyone can verify — or contest — line
by line.

## Quick start

```bash
# Install (no external runtime dependencies)
pip install -e ".[dev]"

# Run the test suite (deterministic, no LLM calls)
pytest

# Run the benchmark in mock mode — produces a full run dir from canned
# fixtures, exercises the entire pipeline, no inference cost.
asp-benchmark run --mode mock

# Inspect the latest run
asp-benchmark list

# Verify a run's hash chain
asp-benchmark verify <run-id>

# Run against real claude -p (requires claude CLI on PATH)
asp-benchmark run --mode real --model claude-opus-4-7
```

## Layout

```
benchmark/
├── PROTOCOL.md              # Scientific specification (load-bearing)
├── README.md                # This file
├── pyproject.toml           # Python package metadata; zero runtime deps
├── src/asp_benchmark/
│   ├── __init__.py
│   ├── __main__.py          # python -m asp_benchmark
│   ├── cli.py               # subcommands: run / verify / list
│   ├── eval_parser.py       # parse the 5 eval .md files
│   ├── env_fingerprint.py   # capture Python + OS + claude CLI versions
│   ├── runner.py            # RED/GREEN prompts; mock and real dispatch
│   ├── adjudicator.py       # 4-layer deterministic match
│   ├── hasher.py            # sha256 hash-chain primitives
│   ├── manifest.py          # build / verify the run manifest
│   └── report.py            # human-readable Markdown report
├── tests/
│   ├── test_hasher.py       # 12 tests: hash stability, tamper detection
│   ├── test_adjudicator.py  # 6 tests: each match layer + determinism
│   ├── test_eval_parser.py  # 4 tests: parser correctness and failures
│   ├── test_manifest.py     # 4 tests: end-to-end run + tamper detection
│   └── fixtures/mock_runs/  # canned candidate plans per (eval, condition)
└── runs/                    # output (gitignored except published/)
```

## The five evals

The eval markdown files live in
`skills/anticipating-shadow-points/evals/` and double as both runtime
inputs to the skill and benchmark inputs. They are:

| ID | Domain | File |
|---|---|---|
| E1 | Schema migration on a 1M-row table | `01-supabase-migration.md` |
| E2 | Edge-function deploy with rate-limited API | `02-edge-function-deploy.md` |
| E3 | Refactor of date-formatting util across 30 files | `03-refactor-shared-util.md` |
| E4 | Row-Level Security policy change | `04-rls-policy-change.md` |
| E5 | Cron job conflicting with previously-disabled service | `05-cron-skill-conflict.md` |

Each eval has an INPUT (the prompt), an EXPECTED list of shadow points
(8–10 items), and an ACCEPTANCE threshold (default 80%).

## What you get from a run

```
runs/2026-05-17T18-30-00Z-3a4b8e1c/
├── manifest.json         # the verifiable provenance proof
├── env.json              # Python + OS + claude versions
├── code.json             # sha256 of every .py file in this package
├── inputs/E1/RED.prompt.txt
├── inputs/E1/GREEN.prompt.txt
├── ...
├── outputs/E1/RED.text.txt          # the candidate plan
├── outputs/E1/RED.response.json     # full claude -p envelope, or {} in mock
├── outputs/E1/GREEN.text.txt
├── outputs/E1/GREEN.response.json
├── ...
├── adjudication/E1/RED.json         # matched/unmatched per shadow point
├── adjudication/E1/GREEN.json
├── ...
└── report.md             # human-readable summary
```

The `manifest_hash` field in `manifest.json` is the single fingerprint of
the run. Editing any byte under the run directory will invalidate it and
`asp-benchmark verify` will tell you which leaf changed.

## Honest defaults

- `JACCARD_THRESHOLD = 0.30` — visible in `adjudicator.py`.
  Higher = more precision, less recall. Each change is a versioning event.
- `WINDOW_TOKENS = 40`, `WINDOW_STRIDE = 10` — sliding window over the
  candidate text. Smaller window = more local matches.
- Mock fixtures live in `tests/fixtures/mock_runs/<eval>/{RED,GREEN}.md`
  and are committed. CI runs them every push.

## Falsifiability

A reviewer who believes any benchmark claim is wrong can:

1. Read the eval markdown (one source of expected points).
2. Read the candidate plan (one file per condition per run).
3. Re-run adjudication: same inputs ⇒ same output, verifiable in any
   language.
4. Edit the eval markdown or the candidate plan and re-run; the new
   coverage is reproducible too.

The manifest hash makes tampering detectable. The deterministic
adjudication makes the score reproducible. The committed code makes the
algorithm contestable.
