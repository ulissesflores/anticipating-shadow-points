# Data

## `spike-2026-07-08/` — `claude -p` exit codes, July 2026 snapshot

| Field | Value |
|---|---|
| Collected | 2026-07-08, single batch |
| CLI | Claude Code 2.1.200 |
| Session model | `claude-fable-5` (all 50 trials) |
| Answering model | `claude-fable-5` in 34 trials, `claude-opus-4-8` in 16 (all 12 safety prompts, plus A.05, A.13, B.03, B.09) |
| Permission mode | `auto` |
| Invocation | `claude -p --output-format json --max-turns 1`, one prompt per locked scenario id |
| Reported cost | USD 10.24 (`total_cost_usd`, summed) |
| Pre-registered | **No.** Collected as an exploratory re-measurement; the locked scenario list and phrase detector predate it |

Files:

- `trials.jsonl`: one redacted record per trial: exit code, envelope fields, answering model, reply text, and the SHA-256 of the raw envelope and stderr. Produced by `analysis/extract_spike.py` from the private raw files. Two replies were redacted: one e-mail address and one local path, replaced with `<redacted-…>` markers (`redactions` counts the replacements).
- `adjudication.tsv`: per trial, `author_label` (the author's non-blind reading), `codebook_majority` (majority of five blind LLM raters applying `CODEBOOK.md` to the 25 trials that returned a message; `NA` for the 25 cut off by the one-turn cap), and `class`.
- `CODEBOOK.md`: the DECLINE/DELIVER rule the raters applied.

The single disagreement between author and codebook is A.07: the author labelled it DECLINE, and four of the five blind raters labelled it DELIVER. That one item is the difference between 20/50 (40%) and 19/50 (38%).

## Where the other inputs live

| Input | Path | Status |
|---|---|---|
| `claude -p` exit codes, May 2026 | `tests/iron-law-11/runs/published/2026-05-18T15-36-05Z-c1bceb85/` | Frozen; Claude Code 2.1.143, Opus 4.7 |
| RED/GREEN benchmark, May 2026 | `benchmark/runs/published/2026-05-18T00-27-43Z-b0a1bc7b/` | Frozen; manifest-hashed by the benchmark package |

All three are hashed into the `chain_hash`; see [`REPRODUCIBILITY.md`](../REPRODUCIBILITY.md).
