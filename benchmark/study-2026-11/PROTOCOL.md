# Does ASP find more risks than a plain request? Study protocol, 2026-11

> [!IMPORTANT]
> **Status: fixed before data.** This file, the reference lists and the code that scores them were committed, pushed to the public repository and timestamped (`ledger.jsonl`, the head hash in OpenTimestamps and a Software Heritage snapshot) **before the first counted trial**. Changes after that are added as dated entries under [Deviations](#deviations), and earlier text is never rewritten. This study replaces Protocol 2 of [`PREREGISTRATION.md`](../../PREREGISTRATION.md), which was never deposited. Why it was replaced is explained in that file.

## Question

Claude Code is given a change request on a real repository. It is asked for a plan that ends in a table of at most ten risks. Does the ASP plugin's protocol (`/asp --standard`, stopped after the validated plan) cover more of the risks that independent reviewers named than plain Claude Code does when it is asked for the same table?

## What is fixed

| Item | Value |
|---|---|
| Tasks | Six change requests on six public repositories, each pinned to one commit, in [`tasks.json`](tasks.json). The repositories cover Python, Django, Flask, TypeScript and Docker. The tasks cover data lifecycle, a scheduled job, authentication, shared-library behaviour, deploy and a schema migration. |
| Conditions | `RED-plain`: the request plus "Plan this change." `RED-risk`: the request plus "Before planning, list the ways this change could go wrong." `GREEN`: `/anticipating-shadow-points:asp --standard` with the request, stopped after Phase 6. The exact prompts are the `CONDITIONS` and `CONTRACT` constants in [`run.py`](run.py). |
| Output contract | The same in all conditions: no questions, no file edits, English, and a final table with columns `#`, `Risk`, `Why it bites here`, `Mitigation` (at most 10 rows), followed by a line that starts with `Riskiest:`. Every condition has the same space for risks, so a longer answer cannot score higher by volume. |
| Model and harness | `claude -p` with `--model claude-opus-5-5`, `--permission-mode plan`, `--max-turns 60` and `--output-format stream-json`, on the operator's subscription login. |
| Configuration | One isolated configuration folder for all conditions. The ASP plugin is enabled only in `GREEN`, through `--settings`, and so are the plugins synced from the account (all five are turned off). Built-in plugins stay on in every condition. Every trial starts from a fresh clone of the pinned commit, in a folder outside the operator's home, so that no user `CLAUDE.md` is loaded. Every `CLAUDE*` and `ANTHROPIC*` environment variable inherited from the calling session is removed, so effort level and subagent model are Claude Code's defaults. |
| Plugin bytes | Before trial 1, `run.py check` must show that the installed plugin equals the repository's: one SHA-256 over `skills/anticipating-shadow-points/` and `commands/`, recorded under Deviations with the commit. |
| Order | All task × condition × replicate cells, shuffled once with seed `asp-bench-2026-11`. `python run.py plan` prints the order. Two trials run at a time. |
| Replicates | 5 per task and condition (90 trials). The operator's weekly usage resets about 15 hours after the protocol was written. If fewer than 9 hours remain when collection starts, the count is 3 (54 trials). The count used is recorded under Deviations before trial 1. |

## Changed before collection, 2026-11-09 (no trial had run)

Commit `fc448ba` fixed the lexical matcher (`score.py`, `TAU = 0.30`) as the planned primary scorer, before any reference list existed. When the three blind lists arrived, the matcher was first run on them, to merge them. It could not see that two independent reviewers named the same problem. The pairwise share of one reviewer's items that the matcher found in another reviewer's list:

| Task | Lowest pair | Highest pair |
|---|---|---|
| T1 | 8% | 45% |
| T2 | 8% | 13% |
| T3 | 10% | 36% |
| T4 | 0% | 20% |
| T5 | 18% | 46% |
| T6 | 0% | 33% |

On T4, all three lists name the same five problems in different words:
- retrying a non-idempotent POST duplicates writes;
- the request body stream is cloned or consumed between attempts;
- timeouts are governed separately from network errors;
- existing `shouldRetry` hooks change meaning;
- `Idempotency-Key` and nonce headers.

The matcher found 0% to 20% agreement there. It would miss coverage in the plans in the same way, so a result built on it would describe the scorer, not ASP. Before any trial, therefore:

1. **The primary scorer is a blind judge from another vendor**, Gemini 3.8 Flash (high), through Google Antigravity (`judge.py`).
   - It sees the request, the reference items and only the rows of the answer's table, after a fixed redaction of words that would reveal the condition (`REDACT` in `judge.py`; the count per trial is reported).
   - It answers yes or no for each reference item.
   - Claude is never the judge, because of the self-enhancement bias the skill's methodology cites.
   - Grok is a second judge, and the two judges' agreement is reported.
2. **The lists are merged by the same judge**, which groups items naming the same problem. The reference list keeps the groups named by at least two reviewers, worded as the first reviewer in alphabetical order wrote them. The fallback to the union below 5 items stays.
3. **The lexical matcher stays as a secondary scorer** and its result is reported next to the judge's. Its code and `TAU` are unchanged.
4. **The list parser was fixed.** Grok glued a sentence of narration to its first item, which dropped that item. No list was regenerated.

In the first merge run, the judge tried to run a shell command on T6, the headless mode refused, and no answer came back after eight attempts. One sentence was then added to both judge prompts, for every task: "Answer directly from the text above; do not run commands or use tools." All six merges were rerun with the new prompt. The first run's prompts and answers, which covered T1 to T5, are kept in `judge/merge-attempt1/` and are not used.

The judge's merge outputs (`judge/merge/`) are sealed with the lists before trial 1. Trial scoring runs after collection with the prompt, model and reference lists fixed here.

## Reference lists, written blind

Three models from vendors other than Anthropic each received the same prompt ([`prompts/reference-list.txt`](prompts/reference-list.txt)). Each read a fresh copy of the repository and the change request, and never saw ASP's files or this protocol. Each answered with 6 to 12 concrete ways the change could go wrong.

| Reviewer | Route |
|---|---|
| `grok` | Grok CLI 1.0.77, default model |
| `gptoss` | GPT-OSS 120B (medium), through Google Antigravity |
| `gemini` | Gemini 3.8 Flash (high), through Google Antigravity |

The house routes to GPT-6 Astra and Gemini 4 Argon had no credit or quota left on 2026-11-09.

> [!WARNING]
> **Models stand in for the engineers the earlier draft required. This is a weakening.** The merge rule and the agreement figures below are the only check that the lists are not arbitrary. Human reviewers can be added later as a dated amendment.

**Merge, as first fixed (replaced before collection by the judge's grouping; see above).** Matching uses `score.py`, with no model involved.
- An item enters the reference list when an item from another reviewer matches it in either direction. An item that matches one already kept is not added twice.
- If a merged list has fewer than 5 items, the union of the three lists is used instead.
- The pairwise agreement (the share of each reviewer's items that another reviewer matched) is reported for every task.

## Scoring

The rows of each answer's table are matched against the task's reference list by `score.py`:
- the matcher reuses the shipped matcher's tokenizer;
- an expected item counts as covered when one row contains at least 30% of the item's distinct content tokens, and at least 3 of them.

`TAU = 0.30` was fixed with `python score.py calibrate`, before any list existed. It is the lowest value, on a 0.05 grid, at which no author-written fixture of the earlier mock benchmark matches another task's expected list. At that value each fixture matches 5 to 8 of its own task's 10 items.

Coverage of a trial = covered items / items in the reference list. **Primary coverage uses the judge's verdicts** (see the section above), and the matcher's coverage is secondary.

## Analysis

- **Primary.** `GREEN` against `RED-risk`.
  - Statistic: Δ̄ = (1/6) Σ_t (mean coverage GREEN_t − mean coverage RED-risk_t).
  - Test: one-sided (GREEN > RED-risk), by permutation stratified by task. Condition labels are shuffled only within each task's 10 trials, 10 000 relabellings, seed `asp-bench-2026-11`.
- **Secondary, confirmatory in direction only.**
  - `GREEN` against `RED-plain`.
  - `RED-risk` against `RED-plain`: does asking for risks, by itself, help?
- **Descriptive.**
  - per-task means;
  - rows per answer, words per answer, turns, tokens and seconds per condition;
  - the riskiest point per trial;
  - trials with an error, or with project files changed.
- **Secondary judge (run after collection, labelled secondary).** A model from another vendor sees each reference item and one answer's table rows, without the condition. It answers yes or no for each item. Agreement with the matcher is reported. It never replaces the primary.
- **No other analysis is confirmatory.**

## Decision rule (primary)

| Result | What the repository says |
|---|---|
| Fewer than 5 tasks complete with every replicate in both conditions (usage stop) | Incomplete: the complete tasks are reported descriptively and no row below applies |
| GREEN − RED-risk ≤ 0 on 3 or more of the 6 tasks | ASP showed no measurable benefit over a plain request for the same risk table, under this protocol |
| Permutation p < 0.05 **and** GREEN − RED-risk > 0 on at least 5 of 6 tasks | A measured benefit, scoped to this model, these tasks and these lists |
| Anything else | Inconclusive, with the per-task table |

Whatever the result, it replaces "Not yet measured" in the README and its four translations, and it is reported in the ASP preprint.

## Stopping and errors

- A trial that ends with a usage-limit error stops collection. Trials already run are kept and the stop is recorded.
- A trial that ends with any other error is kept and counted as coverage 0. It is not rerun.
- A trial that changes a project file is reported. It is kept, because plan mode should make that impossible.

## Pipeline check before data

On 2026-11-09, before this protocol was pushed, `run.py` was smoke-tested with one trial per condition. The task was a dark-mode setting in `microblog`, which is not a study task. Those trials are not data, are not kept in the repository, and no study task was run before the push.

## Reserved, exploratory only

If the 90 trials finish and usage remains, a pilot outside software follows: three decision cases, `GREEN` against `RED-risk`, 2 replicates each. It has no decision rule and is labelled exploratory. The plugin does not claim this use.

## Timestamps and integrity

`ledger.jsonl` chains one entry per artifact:
- this protocol, the tasks, the prompt and the code;
- each reference list and the merged lists;
- each trial's answer and compressed envelope;
- the analysis.

Each entry carries the hash of the previous entry, and `python ledger.py verify` recomputes every link and every file hash. The head hash before trial 1 is stamped with OpenTimestamps, and the pushed commit is saved to Software Heritage. Envelopes are kept compressed, with machine paths replaced by markers.

## Deviations

- **2026-11-09, before trial 1: fixed values.**
  - **Replicates:** 5 (90 trials). Collection starts about 13 hours before the usage reset.
  - **Plugin:** installed from commit `fc448ba`. `run.py check` gives the same hash for the repository and the installed copy (`70ac673cb976b6d7e0b72d8237fd24b2e3c85367e769b9cbae13b55b242e123b`).
  - **Reinstall:** the plugin had to be uninstalled and installed again, because Claude Code does not refresh an installed plugin whose version number is unchanged.
- **2026-11-09, 10:20 to 11:28 GMT-3: collection.**
  - All 90 trials ran: 30 per condition, every one ended with `success`, and none changed a project file.
  - The ASP plugin was loaded in all 30 `GREEN` trials and in none of the others.
  - In one trial, `t026` (T3, `GREEN`), Claude Code also used `claude-haiku-5-5` (an internal subagent at its default model), and the run produced 3 `result` events. The last one is the answer, as `run.py` specifies.
- **2026-11-09, after collection: redaction and judging.**
  - Machine paths were redacted from the envelopes and the answers before publication. The temporary folder and the user name are replaced by markers. In 10 answers, the path to Claude Code's plan file was replaced the same way.
  - None of these paths was inside a table row, so the judges' input is unchanged. The SHA-256 values in `runs/trials.jsonl` are those of the published files.
  - `judge.py` gained parallel calls for trial judging. The prompts and models did not change.

