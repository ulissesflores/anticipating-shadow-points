# Pre-registration — two experiments

Protocol 1 is a third `claude -p` exit-code snapshot. Protocol 2 is the first real measurement of ASP's effect on plans.

# Protocol 1 — `claude -p` exit codes on graceful declines, third snapshot

> [!IMPORTANT]
> **Status: DRAFT. Not yet deposited. No data collected.**
> This document becomes a pre-registration only when (1) its SHA-256 is recorded in `output/hash-chain.md` through the `code` / `data` seal, and (2) the same bytes are deposited on Zenodo with a public timestamp, **both before the first trial runs**. Until then it is a plan. Amendments after deposit are appended as dated entries in the [Amendments](#amendments) section and never rewrite earlier text.

## Why a third snapshot

The two earlier runs are frozen evidence, not pre-registered studies (see the scope note in `paper/graceful-refusals.md`). They leave four problems open, and this protocol is designed around them:

| Problem in the earlier runs | How this protocol addresses it |
|---|---|
| The model was not pinned; in July 2026 the session model (Fable 5) handed the safety prompts to Opus 4.8 | The model is pinned with `--model`, and the answering model of every trial is recorded and reported |
| `--max-turns 1` forces a choice between refusing in one turn (exit 0) and being cut off (exit 1) | Every prompt runs under two turn caps, 1 and 5 |
| July 2026 ran inside the author's own setup, with his global instructions loaded | A clean-room precondition, checked on a smoke trial before collection |
| The headline number depended on a non-blind, single-rater manual label | The primary outcome is a blind two-rater codebook label; the locked phrase detector is kept as a secondary, comparability measure |

## Hypotheses

- **H1.** Under the pinned model and `--max-turns 1`, the share of the 50 prompts that end with exit code 0 **and** a reply the blind two-rater codebook labels a decline (the primary `k` below) is at least 5%.
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

- **Primary.** For each cap: `k / 50`, where `k` counts trials with exit code 0 labelled DECLINE under `data/spike-2026-07-08/CODEBOOK.md` by two raters who see only the reply text (blind to exit code, `stop_reason` and cap), with disagreements resolved by a third. Reported with Wilson and Clopper-Pearson 95% intervals. The locked phrase list is not primary because it matches generic phrases anywhere in a reply ("this would require", "could you clarify"), which a successful multi-turn reply under the 5-turn cap can contain, and because it misses non-English declines.
- **Secondary.**
  1. The locked phrase detector (`tests/iron-law-11/refusal-phrases.txt`, `matches_refusal` from the locked `analyze.py`), under the 1-turn cap only, for comparability with the May and July snapshots.
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
| Any exit-0 decline with a non-`end_turn` stop reason | H2 is falsified for that version; `paper/graceful-refusals.md` §4 is rewritten accordingly |

## What is sealed and where

The data and the analysis follow the house pattern: raw envelopes kept outside git, a redacted `data/il11-v3-<date>/trials.jsonl` extract with the SHA-256 of each raw file, derivation in `analysis/results.py`, an assertion per published number in `tests/test_paper_numbers.py`, and a new `chain_hash`.

# Protocol 2 — ASP's effect on plans, first real-mode benchmark

## Why

Version 1.0 of the ASP paper reported a deterministic match of 80% (GREEN) versus 4% (RED). That run was a mock run over fixtures the author wrote; it measured nothing about ASP. The only real evidence is a non-blind author reading of plans whose transcripts were not kept. This protocol produces the first real, preserved measurement.

## Preconditions (before any dispatch)

1. **Blind expected lists.** Two or more engineers who have not read ASP's skill files each write, independently, the failure modes a senior engineer should surface for each of the five tasks in `skills/anticipating-shadow-points/evals/`, seeing the INPUT statement and the same task workspace the agent gets (for E5, the fixture memory folder below), but never ASP's skill files. Their lists, and the merge rule below, are committed and hash-sealed before the first dispatch. Merge rule: an item enters the reference list if at least two reviewers name it (or, with exactly two reviewers, if either names it and the other agrees on reading it).
2. **No vocabulary leak.** The GREEN condition loads the skill as shipped (`skills/anticipating-shadow-points/SKILL.md` and its companion files) as the system prompt; the reviewers never see it.
3. **Runner and matcher ready.** `benchmark/src/asp_benchmark/runner.py` today sends a single-turn template, runs one replicate per task in fixed order and has no clean-room flags. Before deposit it gains: loading the shipped skill for GREEN, `--replicates 8`, a seeded order (`asp-bench-v1`), the clean-room flags of Protocol 1, and the analysis below; and the matcher's layer 3 replaces window Jaccard, which cannot reach the 0.30 threshold for expected points with ten or fewer distinct tokens in most windows, by token recall of the expected point within the window (|E ∩ W| / |E|) at a threshold fixed before the blind lists arrive, as the lowest value at which no author-written GREEN fixture matches another task's expected list, with at least three shared distinct tokens; coverage is reported per layer. These changes are committed and sealed before deposit.
4. **Preserved output.** Every dispatch writes its full JSON envelope to the run directory, which the benchmark package hashes into its manifest.

## Design

| Item | Value |
|---|---|
| Tasks | E1–E5, INPUT statements as committed. E5 tests whether the agent consults project memory (its points 1 and 8 come from it), so its INPUT is left unchanged and its workspace instead ships a fixture memory folder at `.agent/memory/` with the relevant project history, which an agent finds only by looking; RED and GREEN get the same folder, and Phase 1 of the skill will be extended to read `.agent/memory/*.md` in the working directory when `recall.py` is absent. Neither the fixture nor that extension exists yet; both are written, committed and sealed before deposit |
| Conditions | RED (plan as a senior engineer, no skill) and GREEN (ASP loaded) |
| Replicates | 8 dispatches per task × condition (80 in total), order randomised with seed `asp-bench-v1` |
| Model | Pinned with `--model`, exact id recorded in the deposit amendment; same clean-room precondition as Protocol 1 |
| Scoring | The shipped deterministic matcher (`benchmark/src/asp_benchmark/adjudicator.py`) with the layer-3 change of precondition 3, frozen and sealed at deposit and unchanged afterwards, against the blind reference lists |
| Budget | Stop at 80 dispatches or USD 60 reported cost, whichever comes first |

## Outcomes and analysis

- **Primary.** Per task, the difference in mean match (GREEN minus RED) over the 8 replicates. Across tasks, the test statistic is the mean of the five per-task differences, Δ̄ = (1/5) Σ_t (mean GREEN_t − mean RED_t), tested one-sided (GREEN > RED) by a permutation test stratified by task: RED/GREEN labels are permuted only within each task's 16 dispatches, 10 000 Monte Carlo relabellings, seed `asp-bench-v1`. The count of tasks with a positive difference is reported descriptively; no sign test is used, since with five tasks it adds nothing to the all-five rule below.
- **Budget stop.** If the USD 60 cap stops collection early, tasks with fewer than 8 replicates in either condition are reported but excluded from the decision rule, and the result is labelled incomplete.
- **Secondary.** The same with the author's original lists (to measure how much author authorship inflated the earlier observation); per-layer match counts; plan length as a covariate.
- **Negative control.** Each GREEN plan scored against the other tasks' blind lists, as in the mock check.

## Decision rules

| Result | What the repository does |
|---|---|
| Fewer than 5 tasks reach 8 replicates per condition (budget stop) | Labelled incomplete; the completed tasks are reported descriptively and no row below applies |
| GREEN − RED ≤ 0 on 3 or more tasks | The paper states that ASP showed no measurable benefit under this protocol |
| GREEN − RED > 0 on all 5 tasks and permutation p < 0.05 | The paper reports a measured benefit, scoped to this model, these tasks and these lists |
| Anything in between | Reported as inconclusive, with the per-task table |

## Amendments

*None yet.*
