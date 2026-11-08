# Findings

Every number on this page is computed by `analysis/results.py` into [`output/results.json`](../output/results.json) and checked against that file by `tests/test_findings.py`. The papers give the method and the argument: [*Graceful refusals as unsignalled failures*](../paper/graceful-refusals.md) and [*ASP: an operational pre-mortem skill for LLM coding agents*](../paper/asp-preprint.md).

## 1. `claude -p` exits 0 on a graceful decline

July 2026, Claude Code 2.1.200, 50 refusal-provoking prompts, one run.

| Measure | Value |
|---|---|
| Trials that exit 0 | 24 of 50, all with `stop_reason: end_turn` |
| Declines among them, author's label | 20 of 24 (40% of the suite, 95% Wilson CI 28–54%) |
| Declines among them, codebook majority | 19 of 24 (38%) |
| Declines among them, unambiguous core | 12 of 24 (24%) |
| Declines found by the English-only phrase detector | 9 (18%) |
| Information the exit code carries about "was the task delivered?" | 0.09 of 0.40 bits (22.4%) |

Among the 24 exit-0 trials no status field separates a decline from a delivery. The May 2026 snapshot (Claude Code 2.1.143, Opus 4.7) gave 30 of 50 (60%) under the same detector.

## 2. ASP's effect on plans is not measured

The one published benchmark run is a mock run over fixtures the author wrote to test the matcher: GREEN 80% and RED 4% mean coverage. It shows that the matcher separates the two fixture sets, not that ASP improves plans. A real benchmark is specified in [`PREREGISTRATION.md`](../PREREGISTRATION.md) and has not been run.

## Sensitivity

- **How a decline is counted.** The exit-0 decline rate moves from 24% to 40% of the suite with the counting rule; the paper reports all four readings.
- **Reply language.** The detector is English-only and 11 of July's 20 declines are in Portuguese, so the May-to-July drop under the detector (60% to 18%) is not a trend.
- **Matcher windows.** Adding the tail window to the sliding-window matcher moved the best score of 3 expected points, and none crossed the 0.30 threshold.
- **Matcher ceiling.** 19 of the 50 expected points have at most 10 tokens and can never reach 0.30 against a 40-token window; replacing that layer is a precondition of the real benchmark.
