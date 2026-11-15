# Addendum 2 to study 2 (2026-11b): a rerun of the three error trials, and a third judge

**Status: exploratory and post hoc.** Written on 2026-11-15, after the confirmatory result, the second yardstick and two rounds of outside review were known. Sealed in the ledger, committed and timestamped before any call described here was made. It changes no sealed file and no fixed number:

- the confirmatory analysis stays [`../results.json`](../results.json), with the three error trials counted 0 and not rerun, as [`../PROTOCOL.md`](../PROTOCOL.md) fixes;
- the planned analysis of the second yardstick stays [`../yardstick2/results2.json`](../yardstick2/results2.json), under [`../yardstick2/ADDENDUM.md`](../yardstick2/ADDENDUM.md);
- the Grok judge on the second yardstick, which that addendum plans, is still owed. It stopped at 11 of 240 verdicts when its usage quota ran out, and it runs when the quota returns. Nothing below substitutes it.

## Why

1. **The three error trials.** Trials `t097` (U09, Opus 5.5), `t099` (U07, Opus 5.5) and `t100` (U10, Sonnet 5.5) ended in a network error and count 0. All three are `RED-plain`, so the fixed rule moves the difference toward the hypothesis. The reports so far bound the effect of that rule from both sides: the trials left out, and the trials scored as full coverage. On the second yardstick the unfavourable bound leaves the pooled difference at 4.2 points (p = 0.0051) and the Opus 5.5 difference at 3.2 points, not significant (p = 0.099). A bound is an assumption. Running the three trials once more replaces the assumption with an observation, under the limits listed below.
2. **A second opinion on the second yardstick.** Only the Gemini judge has scored it in full. The planned second judge is waiting for its quota, with no date.

## Addition 1: the three trials, run once more

| Item | Fixed here |
|---|---|
| Trials | `t097`, `t099`, `t100`: the same task, model, condition and replicate as in the seeded order. |
| How | `run.py`'s own `run_trial`, called by [`addendum2.py`](addendum2.py): the same prompt, pinned commit, plan mode, turn cap, settings file and clean environment. Claude Code 2.1.319, the version of all 240 trials, with the same configuration folder. |
| Where | `rerun/` in this folder (`trials.jsonl`, `answers/`, `envelopes/`). `../runs/` is not touched. |
| Attempts | One per trial. A usage-limit error stops the rerun, which resumes after the reset. Any other error, or an answer with no table, counts 0 in the rerun rows and is reported. There is no third attempt. |
| Scoring | The Gemini judge, with the command, prompts, redaction and JSON reader of `../judge.py`: coverage against the original lists, coverage against the second yardstick, and relevance. Verdicts go to `rerun-judge/`. A reply that does not answer every item exactly once is asked again, at most three times, and never edited. |
| Analysis | The statistic and permutation test of `../analyze.py`, pooled and per model, with the value of each error trial replaced by the value of its rerun. One row per yardstick, in `results3.json`. |
| Reported | Whatever the result, as a separate row labelled as an unplanned rerun. It never replaces the rows under the fixed rule. |

**Limits, known before the rerun.** It runs two days after collection ended, by an operator who knows the result. The model behind an identifier can change without notice, and nothing observable settles that. `results3.json` records what can be observed: for each rerun, the model the session reports, the models it used, its plugins and whether it changed a project file, next to the values seen in the 237 sealed trials that ended normally. That is a consistency check and not proof that the model is the same.

## Addition 2: a third judge on the second yardstick

| Item | Fixed here |
|---|---|
| Judge | GPT-6 Astra, high reasoning effort, through the Codex CLI: `codex exec --skip-git-repo-check --ephemeral -s read-only -m gpt-6-astra -c model_reasoning_effort=high "<prompt>"`, from an empty folder, with a configuration folder that holds the login only. The model identifier is saved in every verdict. |
| What it scores | The 240 sealed answers against the second yardstick, and the three reruns against it. It does not score the original lists or relevance. |
| Prompt | Unchanged: the per-trial prompt and redaction of `../judge.py`. |
| Verdicts | `astra/yardstick2/astra/` and `rerun-judge/yardstick2/astra/`. A reply that does not answer every item exactly once is asked again, at most three times, and never edited. |
| Analysis | The statistic and permutation test of `../analyze.py`, pooled and per model, error trials counting 0; the same with the error trials as full coverage; the same with the reruns; item-level agreement with the Gemini judge (Cohen's kappa) on the trials that have a table. Output: `results3.json`. |
| If the judge reaches its usage quota | Collection waits for the quota. |
| Reported | Whatever the result, as an additional judge that was not planned. |

**Limits, known before the judge runs.** One of the three reviewers whose lists form the yardstick is GPT-OSS 120B, from the same vendor as this judge. Of the 111 risks of the second yardstick, the wording of each comes from the first reviewer in alphabetical order that named it ([`../yardstick2/results2.json`](../yardstick2/results2.json), `wording_origin`). The judge is also asked, after this addendum's data are in, to review the manuscript; the two tasks are separate calls with no shared context.

## Stopping rule

If the rerun or the third judge reverses the sign of the difference on the second yardstick, or leaves the pooled test at p ≥ 0.05, the manuscript and the README are not edited further until the author has seen the numbers.
