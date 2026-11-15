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
- **2026-11-09, 16:19 GMT-3: collection paused by the operator, who had to shut the computer down.**
  - 38 of 240 trials are recorded, all successful.
  - Trials in flight at the pause were killed before they finished and left no record. They run again on resume.
  - Collection resumes with the same seeded order, skipping recorded trials, and nothing else changes.
  - The usage reset (about 22:40 GMT-3) may fall inside the pause. That does not change any condition.
  - Three answers (`t006`, `t022`, `t023`) named Claude Code's plan file by its absolute path. The path was replaced by markers, as in study 2026-11, outside any table row. From the resumed trials on, `run.py` applies the same markers to the answer before saving it.
- **2026-11-13, 09:40 GMT-3: collection resumed after a four-day pause.**
  - **Claude Code version:** the computer had updated to 2.1.325 during the pause. The 38 recorded trials ran on 2.1.319, so the resumed trials run on 2.1.319 too, installed in a separate folder and placed first on `PATH`, with the auto-updater off. `run.py` is unchanged.
  - **Scratch folder:** the repository mirrors were lost with the restart and were cloned again from the URLs in `tasks.json`. Each pinned commit was checked out once before collection.
  - **Order:** the 38 records match the seeded order on task, model, condition and replicate, and 202 trials remain.
  - Nothing in the prompts, models, tasks, scoring or analysis changed.
- **2026-11-13: collection finished, 240 of 240 trials recorded; three ended in a network error.**
  - **What happened:** during a short loss of internet access, trials `t097` (U09, Opus 5.5), `t099` (U07, Opus 5.5) and `t100` (U10, Sonnet 5.5) ended with "API Error: Can't reach the API server" after ten retries. They left no table. No usage limit was reached.
  - **How they count:** as fixed under "Stopping and errors", each counts as coverage 0 and relevance 0 and is not rerun.
  - **Why this matters:** all three are `RED-plain` trials, so the fixed rule moves the primary difference in the direction of the hypothesis. The report therefore also gives the same analysis without the three strata that hold these trials (21 of 24), labelled as a sensitivity check that was not planned. If the two disagree, the report says so and the weaker result is the one stated in the README.
  - All 240 trials ran on Claude Code 2.1.319 with no plugin enabled, and none changed a project file.
- **2026-11-14: scoring.**
  - **Judge pause:** the Gemini judge stopped at 225 of 240 coverage verdicts when its usage quota ran out. The remaining 15 were judged by the same model with the same command about three hours later, after the quota reset. No other judge was substituted.
  - **Order of sealing:** all trials were pushed before any verdict existed, and all 720 verdicts (Gemini coverage, Grok coverage, Gemini relevance) were chained in the ledger and committed before `analyze.py` ran.
  - **Sensitivity check, not planned:** `sensitivity.py` repeats the primary analysis without the three strata that hold a network-error trial, and without those three trials only. Its output is `sensitivity.json`.
- **2026-11-14: the exploratory `RED-klein` condition was not run.** As of this report it has no trials. It stays optional and exploratory, and it has no bearing on the confirmatory result.
- **2026-11-14: corrections to this file's wording, and a second yardstick.**
  - **Plugins:** the entry of 2026-11-13 says the trials ran "with no plugin enabled". As fixed under "What is fixed", ASP and the five plugins synced from the account were off, and the four plugins built into Claude Code stayed on in all 240 trials, in both conditions (the `plugins` field of `runs/trials.jsonl`).
  - **Redaction list:** the words replaced before judging are those of study 2026-11, written to hide the ASP protocol. No word of that list distinguishes the two conditions of this study. The list changed 12 words in 10 of the 240 tables.
  - **Parallelism:** collection ran with `--workers 3`, as fixed above; `run.py`'s default is 2.
  - **Second yardstick, exploratory and post hoc:** two outside reviewers of the paper draft noted that the reference lists were elicited with the words of the tested sentence ("ways this change could go wrong"). [`yardstick2/ADDENDUM.md`](yardstick2/ADDENDUM.md) fixes a second set of reference lists elicited with the words of the output contract, sealed before its collection. It does not change the analysis above.
- **2026-11-15: a second addendum, exploratory and post hoc, sealed before its first call.**
  - **What it adds:** [`addendum2/ADDENDUM-2.md`](addendum2/ADDENDUM-2.md) fixes two additions. The three network-error trials are run once more, into a separate folder, and reported in a separate row. A third judge (GPT-6 Astra) scores the 240 sealed answers against the second yardstick.
  - **What it does not change:** the rule under "Stopping and errors" still governs the confirmatory analysis and the planned analysis of the second yardstick. In both, the three trials count 0 and are not rerun. The Grok judge on the second yardstick is still owed and is not substituted.
- **2026-11-15, about 11:45 GMT-3: addendum 2 collected in part; the Gemini judge reached its usage quota.**
  - **Reruns:** `t097`, `t099` and `t100` each ran once, on Claude Code 2.1.319, and ended in success with a table of 8, 9 and 10 rows. Their plugins, session model and models used are those of every sealed trial of the same model, and none changed a project file.
  - **Third judge:** GPT-6 Astra returned a complete verdict for all 240 sealed answers and for the three reruns against the second yardstick (243 of 243).
  - **Gemini judge on the reruns:** 4 of the 9 verdicts exist (`t100` on both yardsticks and for relevance, `t097` on the original lists). The quota then ran out, with a reset announced for about 2026-11-21, 00:30 GMT-3. The remaining 5 verdicts wait for it. No judge is substituted, and the rows of `results3.json` that need them are not computed until then.
- **2026-11-15, about 14:40 GMT-3: third addendum, a deviation from the second.** Fixed in [`addendum3/ADDENDUM-3.md`](addendum3/ADDENDUM-3.md) and sealed before any of its calls, except one neutral connection test.
  - **What changes:** the author decided, as a single exception, not to wait for the quota of the judge's command-line channel. The three reruns are scored by the same model, `google/gemini-3.8-flash`, through OpenRouter (a paid API; provider Google AI Studio, reasoning effort high), all 9 verdicts through that channel.
  - **Channel check:** 30 sealed trials, drawn with seed 20261115, are scored through the same channel on the second yardstick and compared with their sealed verdicts.
  - **What it does not change:** the original channel still completes its 9 verdicts when its quota returns, as addendum 2 fixes, and both rows are reported. The 4 verdicts it already gave are not opened. The rows under the fixed rule stay as they are.
- **2026-11-15, about 15:20 GMT-3: addendum 3 collected.** All 9 verdicts on the three reruns and all 30 verdicts of the channel check came back complete through the paid API (39 of 39), for a measured cost of about 3.9 US dollars.
  - **Channel check:** on the 30 sampled trials (281 items) the two channels agree on 98.2% of the items (Cohen's kappa 0.96); 25 of the 30 verdicts are identical; mean coverage is 56.4% through the command line and 56.0% through the API.
  - **Rows with the reruns, API channel:** original lists 47.1% -> 57.5%, 10.5 points, p = 0.0001; second yardstick 56.9% -> 62.5%, 5.6 points, p = 0.0003 (Opus 5.5: 4.9 points, p = 0.0094; Sonnet 5.5: 6.4 points, p = 0.0017). The stopping rule is not triggered.
  - **Still owed:** the 5 remaining verdicts of the command-line channel, when its quota returns, and the Grok judge on the second yardstick.
