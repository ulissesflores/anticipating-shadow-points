# Study 2 (2026-11b): does one sentence make a coding agent find more risks? Confirmatory protocol

> [!IMPORTANT]
> **Status: fixed before data.** The tasks were committed first (`eb1a447`), before any reference list existed. This protocol, the reference lists, their merge and the code were then committed, pushed and timestamped (`ledger.jsonl`, OpenTimestamps on the head, Software Heritage snapshot) **before the first counted trial**. Anything changed afterwards is added as a dated entry under [Deviations](#deviations).

## Question

Study 2026-11 ([`../study-2026-11/`](../study-2026-11/)) found, as a pre-registered **secondary** comparison, that adding one sentence to a plain request raised coverage from 56% to 66% (p = 0.0014). The sentence was "Before planning, list the ways this change could go wrong." Coverage there meant the share of independent reviewers' risks named in the answer's final risk table, measured on Claude Opus 5.5 and six tasks. This study tests that effect as its **primary** question, on twelve new tasks and two models.

## What is fixed

| Item | Value |
|---|---|
| Tasks | Twelve change requests on twelve public repositories, each pinned to one commit, in [`tasks.json`](tasks.json). None was used in study 2026-11. They cover Go, PHP, C#, Java, TypeScript, JavaScript and Python. Their shapes are authentication, URL contracts, moderation, security-library defaults, shared-library behaviour, data export, identifier migration, cryptographic defaults, credential migration, multi-tenancy, booking concurrency and framework security defaults. |
| Conditions | `RED-plain`: the request plus "Plan this change." `RED-risk`: the request plus "Before planning, list the ways this change could go wrong." The prompts are the `CONDITIONS` and `CONTRACT` constants in [`run.py`](run.py), byte for byte the same as in study 2026-11. |
| Output contract | The same in both conditions: no questions, no file edits, English, and a final table with columns `#`, `Risk`, `Why it bites here`, `Mitigation` (at most 10 rows), followed by a line that starts with `Riskiest:`. |
| Models | `claude-opus-5-5` and `claude-sonnet-5-5`, both run on every task × condition cell. |
| Harness | `claude -p` with `--permission-mode plan`, `--max-turns 60` and `--output-format stream-json`, on the operator's subscription login. Every `CLAUDE*` and `ANTHROPIC*` variable is removed from the environment, so effort level and subagent model are Claude Code's defaults. |
| Configuration | One isolated configuration folder. Every plugin is turned off through `--settings`: ASP and the five synced from the account. Built-in plugins stay on. Each trial starts from a fresh clone of the pinned commit, outside the operator's home. |
| Order | All task × model × condition × replicate cells, shuffled once with seed `asp-study2-2026-11b`. `python run.py plan` prints the order. Three trials run at a time. |
| Replicates | 5 per cell, for 240 trials. The operator's weekly usage resets at about 22:40 GMT-3 on 2026-11-09. If fewer than 3 hours remain when collection starts, the count is 3, for 144 trials. The count used is recorded under Deviations before trial 1. |

## Reference lists, written blind

The method is the same as in study 2026-11.
- Three models of other vendors write the risks they expect. Each reads a fresh copy of the repository and the request, with the same prompt ([`prompts/reference-list.txt`](prompts/reference-list.txt)), and never sees ASP, the conditions or this protocol:
  - `grok`: Grok CLI;
  - `gptoss`: GPT-OSS 120B (medium) through Google Antigravity;
  - `gemini`: Gemini 3.8 Flash (high) through Google Antigravity.
- **Merge:**
  - The blind Gemini judge groups items that name the same problem (`judge.py merge`).
  - A risk enters the reference list when at least two reviewers name it, worded as the first reviewer in alphabetical order wrote it.
  - The fallback to the union when fewer than 5 risks remain stays.

> [!WARNING]
> Models stand in for independent engineers, a weakening also declared in study 2026-11.

## Scoring

- **Primary: coverage by the blind Gemini judge.**
  - The judge sees the request, the reference risks and only the rows of the answer's table, with condition-revealing words redacted.
  - It marks each reference risk as covered or not.
  - Coverage = covered risks / reference risks.
- **Secondary:**
  - the same scoring by a Grok judge, with agreement between the two judges reported;
  - the lexical matcher of study 2026-11, which is known to be blind to paraphrase;
  - **relevance**: the share of an answer's table rows that the Gemini judge calls a concrete, plausible risk of this specific change (`judge.py relevance`). This checks that a gain in coverage is not just more items listed. Relevance is judged from the request and the row alone, without the repository: it measures specificity and plausibility, not correctness.

All judge prompts include "Answer directly from the text above; do not run commands or use tools." The JSON reader skips braces in prose, and an unreadable reply is asked again, never edited.

## Analysis

- **Primary.** Δ̄ = the mean, over the 24 task × model strata, of mean coverage `RED-risk` minus mean coverage `RED-plain`.
  - Test: one-sided (`RED-risk` > `RED-plain`), by permutation within each stratum, 10 000 relabellings, seed `asp-study2-2026-11b`.
- **Reported with it:**
  - Δ̄ and its own permutation p for each model separately (its 12 strata);
  - the number of strata with a positive difference;
  - overall coverage per condition;
  - turns, tokens, seconds and table rows per condition.
- **Secondary:** the same analysis for the Grok judge, the matcher and relevance.
- **No other analysis is confirmatory.**

## Decision rule (primary)

| Result | What the repository says |
|---|---|
| Fewer than 18 of the 24 planned strata complete with every replicate in both conditions | Incomplete: reported descriptively, no claim |
| p ≥ 0.05 | Not confirmed: the study 2026-11 effect did not replicate under this protocol |
| Pooled p < 0.05 **and** the same permutation test within each model (its 12 strata) gives p < 0.05 for both models | Confirmed: asking for the ways a change could go wrong raises risk coverage, scoped to these two models, these tasks and model-written reference lists |
| Pooled p < 0.05 and exactly one model's own p < 0.05 | Confirmed in one model only, named |
| Pooled p < 0.05 and neither model's own p < 0.05 | Not confirmed |

Whatever the result, it is reported in the README, the ROADMAP and the third paper, together with relevance: a coverage gain with lower relevance is reported as such.

## Replication subset, not counted

Study 2026-11's six tasks, Opus 5.5 only, already measured this comparison. Those numbers are cited next to this study's result and are not pooled into it.

## Exploratory, only if usage remains

If the 240 trials finish and usage remains, a third condition runs on all 12 tasks with Opus 5.5 and 2 replicates. It is `RED-klein`: "Imagine it is a month from now and this change has failed. Before planning, list why it failed." This is Klein's pre-mortem framing. It has no decision rule and is labelled exploratory.

## Stopping and errors

- A usage-limit error stops collection, and the stop is recorded.
- Any other error counts as coverage 0 and relevance 0, and is not rerun.
- A changed project file is reported.

## Pipeline check before data

Before this protocol was pushed, one Sonnet 5.5 trial ran on a task outside the study (a dark-mode setting in `microblog`), to check the model flag. It ended in success in 3 turns and 24.5 s, changed no file and ran with no plugin enabled. It is not data and is not kept.

## Timestamps and integrity

`ledger.jsonl` chains:
- the protocol, tasks, prompts and code;
- each reference list, the judge's merge outputs and `lists/merged.json`;
- each trial's answer and redacted envelope;
- each verdict;
- the analysis.

`python ledger.py verify` checks every link and that each file matches its latest entry. The pre-trial head is stamped with OpenTimestamps, and the pushed commit is saved to Software Heritage.

## Deviations

- **2026-11-09, about 16:10 GMT-3, before trial 1: fixed values.**
  - **Replicates:** 5, for 240 trials. About 6.5 hours remain before the usage reset.
  - **Reference lists:** 6 to 10 risks per task after the judge's merge.
  - **Agreement:** the share of each reviewer's items also named by another runs from 8% (GPT-OSS on U02) to 100% (Grok on U10).
- **2026-11-09, 16:10 GMT-3: plumbing fix during the first minutes of collection.**
  - **The problem:** `run.py` cloned each trial into the scratch folder `work/<trial id>`, and folders `t001` to `t090` still held study 2026-11's clones. Those trials failed at `git clone`, before any `claude -p` call, and left no record.
  - **What ran anyway:** trials `t091` to `t096`, whose folders did not exist, ran normally and are kept. Their records are the first six lines of `runs/trials.jsonl`.
  - **The fix:** `run.py` now clones into `work-2026-11b/`, and collection resumed with the same seeded order, skipping trials already recorded.
  - Nothing in the prompts, models, tasks, scoring or analysis changed.

