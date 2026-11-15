# Addendum 3 to study 2 (2026-11b): the rerun scored by the same judge model through a paid API

**Status: exploratory and post hoc, and a deviation from [`../addendum2/ADDENDUM-2.md`](../addendum2/ADDENDUM-2.md).** Written on 2026-11-15, sealed in the ledger, committed and timestamped before any call described here was made, except one neutral test call ("Reply with the single word OK.") that checked the connection. It changes no sealed file and no fixed number.

## Why

Addendum 2 fixed that the three reruns are scored by the Gemini judge with the command of `../judge.py`, and that collection waits when a usage quota runs out. That command is the Antigravity CLI of a subscription (`agy --model gemini-3.8-flash-high`). Its quota ran out after 4 of the 9 verdicts, and the service reports a reset about 2026-11-21 00:30 (GMT-3). The author decided on 2026-11-15, as a single exception, not to wait: the same model is called through OpenRouter, a paid API, and the original channel is still run when its quota returns.

The channel is not the same thing as the command addendum 2 fixed. The CLI wraps a prompt in its own agent instructions; the API receives the prompt alone. This addendum therefore keeps the two apart and measures the difference instead of assuming it away.

## What is fixed here

| Item | Fixed here |
|---|---|
| Model and channel | `google/gemini-3.8-flash` through `https://openrouter.ai/api/v1/chat/completions`, provider restricted to Google AI Studio with fallbacks off, `reasoning.effort` = `high`. One user message that holds the prompt; no system message; no other parameter. The full API reply (model, provider, token counts, generation id) is saved with every verdict. |
| Prompt | Unchanged: the prompts and redaction of `../judge.py`, built by the same functions. |
| What is scored | All three reruns, on the original lists, on the second yardstick and for relevance: 9 verdicts, all through this channel. The 4 verdicts the CLI already gave are not used here and not opened. |
| Channel check | 30 of the 237 sealed trials that have a table, drawn with `random.Random(20261115).sample` from the trial ids in order, scored through this channel against the second yardstick. Their CLI verdicts are the sealed ones in `../yardstick2/judge/gemini/`. Reported: item-level agreement and Cohen's kappa, each channel's share of items marked covered, and the mean coverage per trial under each channel. |
| Verdict rules | As in addendum 2: a reply that does not answer every item exactly once is asked again, at most three times, and never edited. An HTTP or API error is not a reply; it is retried up to five times and then stops the run. |
| Where | `openrouter/` in this folder. Nothing is written to `../addendum2/rerun-judge/*/gemini/`, which stays reserved for the CLI. |
| Analysis | The statistic and permutation test of `../analyze.py`, pooled and per model, with the value of each error trial replaced by the value of its rerun under this channel, for each yardstick; relevance the same way. Output: `results4.json`. |
| The original channel | When the CLI quota returns, `addendum2.py judge-rerun` completes its 9 verdicts as addendum 2 fixes, and both rows are reported side by side. |
| Reported | Whatever the result, as an unplanned rerun scored through a second channel, with the channel check next to it. It never replaces the rows under the fixed rule. |

## Limits, known before the calls

- How the CLI maps its `-high` suffix to a reasoning setting is not documented, so `reasoning.effort` = `high` is the nearest declared setting and not a proven equivalent.
- The sample of 30 measures agreement between channels; it cannot show the channels are identical.
- The stopping rule of addendum 2 applies to these rows as well: a reversed sign or a pooled p ≥ 0.05 on the second yardstick stops any edit of the manuscript until the author has seen the numbers.
- The API key is the author's. It is read from the environment and written nowhere.
