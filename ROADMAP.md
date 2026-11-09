# Roadmap

Stated honestly: what the next versions add, and what they still will not prove.

## v2.0.0 (this branch)

- Replication layer: `run_all.py`, SHA-256 provenance, every paper number asserted by a test.
- July 2026 `claude -p` re-measurement published as a redacted extract, with the corrected model attribution (Fable 5, safety prompts answered by Opus 4.8).
- Both papers revised against the derived numbers, reviewed blind by models of other families, and built in the house format (PDF and DOCX in `docs/paper/`, with version, DOI and replication notes in a Technical Note after the references).
- Demo recordings and figures as code; translations regenerated from the revised English.
- Runner no longer sets a permission mode (shipped in 1.0.4).

## Next: two experiments, drafted and not yet deposited

Both are specified in [`PREREGISTRATION.md`](PREREGISTRATION.md) and run only after the document is deposited with a public timestamp:

1. A third `claude -p` snapshot: pinned model, two turn caps, clean-room precondition, deterministic primary outcome.
2. The first real ASP benchmark: real-mode RED/GREEN runs with preserved, hash-sealed transcripts, scored by the shipped matcher against expected lists written blind by independent engineers.

The second experiment is the source of the series' third paper: the scientific paper on ASP, reporting the benchmark's result under the decision rule fixed in advance. Until it runs, the whitepaper stays what it is, an experience report, and claims no measured effect.

## Open, and not claimed until done

| Item | Why it matters | Blocker |
|---|---|---|
| Blind re-authoring of the five benchmark expected lists by independent engineers | No preserved model output yet measures ASP; and lists written by the author would make any measurement circular | Needs two or more outside reviewers |
| MAST ablation with a blind placebo prompt | Tests whether the 14-mode enumeration, not prompt length or framing, drives the GREEN effect | Needs the blind lists above first |
| Human second rater on the July 2026 labels | The 40% rests on one non-blind rater; an LLM panel agreed but shares lineage with the model under test | Needs one outside human rater |
| ASP for decisions outside code (legal, accounting, strategy) | The pre-mortem and the independent check are domain-neutral; the shipped checklist is not | A domain-specific checklist and its own blind lists; an exploratory pilot is reserved in the 2026-11 study |
