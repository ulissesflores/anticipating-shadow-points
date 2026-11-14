# Roadmap

Stated honestly: what the next versions add, and what they still will not prove.

## v2.0.0 (this branch)

- Replication layer: `run_all.py`, SHA-256 provenance, every paper number asserted by a test.
- July 2026 `claude -p` re-measurement published as a redacted extract, with the corrected model attribution (Fable 5, safety prompts answered by Opus 4.8).
- Both papers revised against the derived numbers, reviewed blind by models of other families, and built in the house format (PDF and DOCX in `docs/paper/`, with version, DOI and replication notes in a Technical Note after the references).
- Demo recordings and figures as code; translations regenerated from the revised English.
- Runner no longer sets a permission mode (shipped in 1.0.4).

## Done in v2.0.0: the first real measurement of ASP

The 2026-11 study ([`benchmark/study-2026-11/`](benchmark/study-2026-11/)) ran 90 pre-registered trials on six pinned public repositories. ASP's full protocol covered fewer of the blind reviewers' risks than plain Claude Code asked to list the ways a change could go wrong: no measurable benefit. That one sentence beat a plain "plan this change" by 10 to 13 points (secondary, pre-registered).

## Done after v2.0.0: the one sentence, confirmed

The 2026-11b study ([`benchmark/study-2026-11b/`](benchmark/study-2026-11b/)) made the one-sentence pre-mortem its primary question: 240 pre-registered trials on twelve new pinned repositories, with Claude Opus 5.5 and Sonnet 5.5.
- **Result:** asking "Before planning, list the ways this change could go wrong." raised risk coverage from 46% to 58% (p = 0.0001 overall and within each model). The second judge agrees.
- **Relevance:** the listed risks were not less relevant.
- **Limits:** two Claude models, model-written reference lists, and three network-error trials that the report handles with a sensitivity check that was not planned.

## Next

1. **A human engineer on a sample of the reference lists.** Both studies scored against lists written by models of other vendors. This is the stated weakness that remains.
   The two studies together are the source of the series' third paper.
2. **ASP v2.1, rebuilt on what was measured.**
   - The one-sentence pre-mortem, now confirmed, becomes the cheap default.
   - The full protocol becomes an option that has to earn its cost.
   - The same study design re-measures it.
3. **A third `claude -p` snapshot** (Protocol 1 of [`PREREGISTRATION.md`](PREREGISTRATION.md)): pinned model, two turn caps, clean-room precondition.

## Open, and not claimed until done

| Item | Why it matters | Blocker |
|---|---|---|
| Human reviewers next to the model-written reference lists | The 2026-11 lists were written by three models of other vendors, a stated weakening | One or more outside engineers |
| MAST ablation with a blind placebo prompt | Would test what part of the protocol helps; after the 2026-11 result, first test whether any part beats the one sentence, which the 2026-11b study confirmed | A study design with the sentence as the baseline |
| Human second rater on the July 2026 labels | The 40% rests on one non-blind rater; an LLM panel agreed but shares lineage with the model under test | Needs one outside human rater |
| ASP for decisions outside code (legal, accounting, strategy) | The pre-mortem and the independent check are domain-neutral; the shipped checklist is not | A domain-specific checklist and its own blind lists; not run in 2026-11, since the protocol did not beat the baseline in code |
