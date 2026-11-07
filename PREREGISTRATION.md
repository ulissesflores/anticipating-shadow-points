# Pre-registration — two experiments

Protocol 1 is a third `claude -p` exit-code snapshot. Protocol 2 is the first real measurement of ASP's effect on plans.

# Protocol 1 — `claude -p` exit codes on graceful declines, third snapshot

> [!IMPORTANT]
> **Status: DRAFT. Not yet deposited. No data collected.**
> This document becomes a pre-registration only when (1) its SHA-256 is recorded in `output/hash-chain.md` through the `code` / `data` seal, and (2) the same bytes are deposited on Zenodo with a public timestamp, **both before the first trial runs**. Until then it is a plan. Amendments after deposit are appended as dated entries in the [Amendments](#amendments) section and never rewrite earlier text.

## Why a third snapshot

The two earlier runs are frozen evidence, not pre-registered studies (see the scope note in `paper/iron-law-11.md`). They leave four problems open, and this protocol is designed around them:

| Problem in the earlier runs | How this protocol addresses it |
|---|---|
| The model was not pinned; in July 2026 the session model (Fable 5) handed the safety prompts to Opus 4.8 | The model is pinned with `--model`, and the answering model of every trial is recorded and reported |
| `--max-turns 1` forces a choice between refusing in one turn (exit 0) and being cut off (exit 1) | Every prompt runs under two turn caps, 1 and 5 |
| July 2026 ran inside the author's own setup, with his global instructions loaded | A clean-room precondition, checked on a smoke trial before collection |
| The headline number depended on a non-blind, single-rater manual label | The primary outcome uses the locked, deterministic phrase detector; manual labels are secondary |

## Hypotheses

- **H1.** Under the pinned model and `--max-turns 1`, the share of the 50 prompts that end with exit code 0 **and** a reply the locked detector flags as a refusal is at least 5%.
- **H2.** Every exit-0 decline carries `stop_reason: end_turn` (no machine-readable refusal flag in the envelope).
- **H3.** Raising the cap from 1 to 5 turns changes the exit-0 decline count (two-sided; we do not predict the direction).

## Design

| Item | Value |
|---|---|
| Prompts | The 50 locked scenarios in `tests/iron-law-11/scenarios/` (13 impossible, 13 capability, 12 safety, 12 ambiguity), unchanged, hash-checked by `tests/iron-law-11/scripts/verify-prereg.sh` |
| Conditions | `--max-turns 1` and `--max-turns 5`; 100 trials in total |
| Order | Scenario order shuffled once with seed `asp-il11-v3`; the 1-turn block runs before the 5-turn block |
| Invocation | `claude -p --output-format json --model <pinned> --max-turns <cap> --no-session-persistence --strict-mcp-config --setting-sources project`, run from an empty folder, with the exit code captured immediately |
| Model | The current default Opus model at deposit time, written here as an exact id in the deposit amendment |
| Authentication | The operator's subscription login, no API key |
| Budget | Stop after 100 trials or USD 25 of reported `total_cost_usd`, whichever comes first; a budget stop is reported as such |

### Clean-room precondition (checked before trial 1)

One smoke trial with a neutral prompt must show, in its `system/init` event: no `memory_paths` entry pointing at a user folder, no plugins, no MCP servers. If it fails, collection does not start, and the failure is recorded as an amendment.

## Outcomes and analysis

- **Primary.** For each cap: `k / 50`, where `k` counts trials with exit code 0 whose `result` text matches the locked phrase list `tests/iron-law-11/refusal-phrases.txt`, using `matches_refusal` from the locked `analyze.py`. Reported with Wilson and Clopper-Pearson 95% intervals.
- **Secondary.**
  1. The same count under the author's manual label, applying `data/spike-2026-07-08/CODEBOOK.md` blind to exit code and `stop_reason` (labels written before the exit codes are joined).
  2. The `stop_reason` distribution of exit-0 trials (H2).
  3. The paired 1-turn versus 5-turn difference, using an exact McNemar test (H3).
  4. Per-category counts, and the answering model of every trial.
- **No other analyses are confirmatory.** Anything else is labelled exploratory.

## Decision rules

| Result (primary, 1-turn cap) | What the repository does |
|---|---|
| `k / 50 < 5%` | Iron Law 11 is downgraded in the skill from mandatory to advisory, and the paper reports the falsification |
| `5% <= k / 50 <= 25%` | Iron Law 11 stays; the paper reports the rate as a defensive recommendation |
| `k / 50 > 25%` | Iron Law 11 stays mandatory; the result is reported to Anthropic through the public issue tracker |
| Any exit-0 decline with a non-`end_turn` stop reason | H2 is falsified for that version; the paper's section 4 is rewritten accordingly |

## What is sealed and where

The data and the analysis follow the house pattern: raw envelopes kept outside git, a redacted `data/il11-v3-<date>/trials.jsonl` extract with the SHA-256 of each raw file, derivation in `analysis/results.py`, an assertion per published number in `tests/test_paper_numbers.py`, and a new `chain_hash`.

# Protocol 2 — ASP's effect on plans, first real-mode benchmark

## Why

Version 1.0 of the ASP paper reported a deterministic match of 80% (GREEN) versus 4% (RED). That run was a mock run over fixtures the author wrote; it measured nothing about ASP. The only real evidence is a non-blind author reading of plans whose transcripts were not kept. This protocol produces the first real, preserved measurement.

## Preconditions (before any dispatch)

1. **Blind expected lists.** Two or more engineers who have not read ASP's skill files each write, independently, the failure modes a senior engineer should surface for each of the five tasks in `skills/anticipating-shadow-points/evals/`, seeing only the INPUT statement. Their lists, and the merge rule below, are committed and hash-sealed before the first dispatch. Merge rule: an item enters the reference list if at least two reviewers name it (or, with exactly two reviewers, if either names it and the other agrees on reading it).
2. **No vocabulary leak.** The GREEN prompt is the skill as shipped; the reviewers never see it.
3. **Preserved output.** Every dispatch writes its full JSON envelope to the run directory, which the benchmark package hashes into its manifest.

## Design

| Item | Value |
|---|---|
| Tasks | E1–E5, unchanged INPUT statements |
| Conditions | RED (plan as a senior engineer, no skill) and GREEN (ASP loaded) |
| Replicates | 8 dispatches per task × condition (80 in total), order randomised with seed `asp-bench-v1` |
| Model | Pinned with `--model`, exact id recorded in the deposit amendment; same clean-room precondition as Protocol 1 |
| Scoring | The shipped deterministic matcher (`benchmark/src/asp_benchmark/adjudicator.py`), unchanged since commit of this document, against the blind reference lists |
| Budget | Stop at 80 dispatches or USD 60 reported cost, whichever comes first |

## Outcomes and analysis

- **Primary.** Per task, the difference in mean match (GREEN minus RED) over the 8 replicates; across tasks, a paired sign test on the five per-task differences, and a permutation test over the 80 dispatches (10 000 relabellings, seed fixed).
- **Secondary.** The same with the author's original lists (to measure how much author authorship inflated the earlier observation); per-layer match counts; plan length as a covariate.
- **Negative control.** Each GREEN plan scored against the other tasks' blind lists, as in the mock check.

## Decision rules

| Result | What the repository does |
|---|---|
| GREEN − RED ≤ 0 on 3 or more tasks | The paper states that ASP showed no measurable benefit under this protocol |
| GREEN − RED > 0 on all 5 tasks and permutation p < 0.05 | The paper reports a measured benefit, scoped to this model, these tasks and these lists |
| Anything in between | Reported as inconclusive, with the per-task table |

## Amendments

*None yet.*
