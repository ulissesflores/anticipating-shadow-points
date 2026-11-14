# Study 2 (2026-11b), addendum: a second yardstick, written with different words

> [!IMPORTANT]
> **Exploratory and post hoc.** This addendum was written on 2026-11-14, after the pre-registered analysis had run and its result was known. Nothing here changes that analysis or its decision. This file, the prompt and the code were chained in the ledger and committed before the first reviewer call. The result is reported whichever way it falls.

## Why

Two outside reviewers of the paper draft raised the same objection independently. The reference lists of the study were written under a prompt that asks for "the concrete ways this change could go wrong" ([`../prompts/reference-list.txt`](../prompts/reference-list.txt)). The condition under test adds the sentence "Before planning, list the ways this change could go wrong." The plain condition never sees those words. Part of the measured gain could therefore come from the tested answers sharing the wording that produced the yardstick, and not from naming more of the risks of the change.

## What is fixed here

| Item | Value |
|---|---|
| Reviewer prompt | [`reference-list-2.txt`](reference-list-2.txt). It is the original prompt with one sentence replaced. "List the concrete ways this change could go wrong in this codebase if it were implemented without care: the problems a careful senior engineer would want addressed before starting." becomes "List the main risks of this change in this codebase: the risks a careful senior engineer would want addressed before starting." The words "the main risks of this change" are the words of the output contract, which **both** conditions receive. The words "go wrong" do not appear. |
| Reviewers | The same three routes: `grok` (Grok CLI), `gptoss` (GPT-OSS 120B medium through Google Antigravity), `gemini` (Gemini 3.8 Flash high through Google Antigravity). Each reads a fresh clone of the pinned commit. The exact commands are in [`yardstick2.py`](yardstick2.py). |
| Merge | Unchanged: the Gemini judge groups the items with the prompt of `../judge.py`, and a risk enters the list when at least two reviewers name it, worded as the first reviewer in alphabetical order wrote it. |
| Trials | The same 240 answers in `../runs/`. No trial is run again. |
| Scoring | Unchanged: `../judge.py`'s prompt, redaction and JSON reader, with the Gemini judge first and the Grok judge second. Verdicts go to `judge/` in this folder, so the sealed verdicts in `../judge/` are not touched. |
| Analysis | The primary statistic and permutation test of `../analyze.py`, on these verdicts, pooled and per model. Error trials count 0, as in the protocol. Output: `results2.json`. |
| If a judge reaches its usage quota | Collection waits for the quota. No judge is substituted. |

## How it will be read

- **The difference stays positive, with p < 0.05 pooled:** the gain does not depend on a yardstick elicited with the tested sentence's words. The paper reports both sizes side by side.
- **The difference is not distinguishable from zero:** the paper states that the confirmed effect may be specific to yardsticks elicited with the same words, and the READMEs are corrected to say so.
- Either way this is one exploratory check with model-written lists. It does not replace a yardstick written by people or taken from real defects.
