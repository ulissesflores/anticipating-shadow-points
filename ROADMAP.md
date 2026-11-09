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

## Next

1. **A confirmatory study of the one-sentence pre-mortem**, with it as the primary question:
   - 12 to 15 pinned tasks and a second model;
   - a precision measure (are the listed risks real?) next to coverage;
   - a human engineer on a sample of the reference lists.

   It reuses the 2026-11 infrastructure and is pre-registered and timestamped before trial 1. It is the source of the series' third paper.
2. **ASP v2.1, rebuilt on what was measured.**
   - The one-sentence pre-mortem becomes the cheap default.
   - The full protocol becomes an option that has to earn its cost.
   - The same study design re-measures it.
3. **A third `claude -p` snapshot** (Protocol 1 of [`PREREGISTRATION.md`](PREREGISTRATION.md)): pinned model, two turn caps, clean-room precondition.

## Open, and not claimed until done

| Item | Why it matters | Blocker |
|---|---|---|
| Human reviewers next to the model-written reference lists | The 2026-11 lists were written by three models of other vendors, a stated weakening | One or more outside engineers |
| MAST ablation with a blind placebo prompt | Would test what part of the protocol helps; after the 2026-11 result, first test whether any part beats the one sentence | The confirmatory study first |
| Human second rater on the July 2026 labels | The 40% rests on one non-blind rater; an LLM panel agreed but shares lineage with the model under test | Needs one outside human rater |
| ASP for decisions outside code (legal, accounting, strategy) | The pre-mortem and the independent check are domain-neutral; the shipped checklist is not | A domain-specific checklist and its own blind lists; not run in 2026-11, since the protocol did not beat the baseline in code |
