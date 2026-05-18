# Iron Law 11 — Pre-registered protocol runner

This directory contains the executable scaffolding for the
pre-registered protocol described in `paper/iron-law-11.md`. The
protocol characterises `claude -p` exit-code semantics under graceful
agent refusal across N=50 deliberate refusal scenarios.

## What is committed BEFORE data collection (and locked)

| File | Purpose |
|---|---|
| `refusal-phrases.txt` | The locked list of refusal phrases used by `analyze.py` |
| `random_seed.txt` | The committed run-id seed |
| `scenarios/A.01.txt` … `D.12.txt` | 50 scenario prompts (13 + 13 + 12 + 12) |
| `preregistration.json` | SHA-256 of each scenario + the refusal-phrase list + the seed; the timestamped record of pre-registration |
| `scripts/run-protocol.sh` | The dispatch script (Iron Laws 9, 11, 12 honored) |
| `scripts/analyze.py` | The pre-committed analysis (confusion matrix + Clopper-Pearson 95% CI) |
| `scripts/verify-prereg.sh` | Hash-checks every locked file against `preregistration.json` |

Editing any of these files after the formal run has begun is a
pre-registration violation. `verify-prereg.sh` is run before and after
the formal data collection to detect it.

## Smoke test (already executed)

A 3-trial smoke test using non-formal scenarios under `smoke/scenarios/`
was run during scaffolding to verify the dispatch pipeline end-to-end.
The smoke run lives under `smoke/runs/<id>/` and is reported in
`paper/iron-law-11.md` §4.3.

**Important smoke-test outcome**: the safety-refusal scenario
(S.02) produced exit code 0 with `terminal_reason: completed`,
confirming the Iron Law 11 failure mode in a category (safety) distinct
from the original observation (explicit impossibility). This is
preliminary infrastructural validation only — the formal claim still
depends on the pre-registered N=50 run.

## Running the formal N=50 protocol

```bash
# 1. Verify the pre-registration is intact.
./scripts/verify-prereg.sh

# 2. Run the protocol. Expect ~5-15 minutes wall-clock; ~$3-5 inference.
./scripts/run-protocol.sh

# 3. Analyze the result. The analysis plan is pre-committed in
#    paper/iron-law-11.md §3.4 and implemented in scripts/analyze.py.
./scripts/analyze.py runs/<run-id>

# 4. Re-verify the pre-registration is still intact (no edits during run).
./scripts/verify-prereg.sh
```

The run produces a directory `runs/<timestamp>-<seed>/` with one
trial subdirectory per scenario, containing the exact prompt, the
exit code, the JSON envelope, and the textual result. `analyze.py`
produces `analysis-report.md` and `analysis.json` in the same
directory.

## Once the formal run completes

The empirical addendum is appended to `paper/iron-law-11.md` as a
new section that:

1. Reproduces the analysis-report.md content (confusion matrix +
   metrics + per-category breakdown).
2. Compares the observed misclassification rate against the
   falsification thresholds in §3.6.
3. Notes any deviations from the pre-registration with a one-line
   justification each (Appendix A of the paper).
4. Publishes the per-trial dataset (already in `runs/<id>/trials/`)
   as the supplementary material.

## Cost and time

A typical trial takes ~3-15 seconds wall-clock; the JSON envelope's
`total_cost_usd` field on our smoke runs averaged ~$0.09 per call
(Claude Opus 4.7, --max-turns 1). For N=50 this is approximately:

- **Wall-clock**: ~5-15 minutes
- **Inference cost**: ~$3-5 (against the user's Claude Code plan
  allowance, not a separate API bill)

These figures are estimates and will be reported exactly in the
addendum's per-trial dataset.

## Reentrancy guard

`run-protocol.sh` exports `ASP_IN_GOAL=1` to its child `claude -p`
processes. Any ASP-aware skill the child invokes is expected to
honor Iron Law 9 (no reentrant ASP) and refuse to load. This is
defense-in-depth: the formal scenarios do not invoke ASP, but a
recursive scenario would be a budget-explosion footgun.

## Layout

```
tests/iron-law-11/
├── README.md                       ← this file
├── refusal-phrases.txt             ← LOCKED phrase list
├── random_seed.txt                 ← LOCKED seed
├── preregistration.json            ← LOCKED hashes + analysis plan
├── scenarios/                      ← LOCKED 50 prompt files
│   ├── A.01.txt … A.13.txt
│   ├── B.01.txt … B.13.txt
│   ├── C.01.txt … C.12.txt
│   └── D.01.txt … D.12.txt
├── scripts/
│   ├── run-protocol.sh             ← dispatcher
│   ├── _summarize-run.py           ← internal helper
│   ├── analyze.py                  ← confusion matrix + stats
│   └── verify-prereg.sh            ← integrity checker
├── smoke/                          ← infrastructure validation (NOT formal)
│   ├── scenarios/
│   │   └── S.01.txt … S.03.txt
│   └── runs/<id>/                  ← one example smoke run committed
└── runs/                           ← formal runs land here (gitignored except .gitkeep)
```
