# Roadmap

Stated honestly: what the next versions add, and what they still will not prove.

## v2.0.0 (this branch)

- Replication layer: `run_all.py`, SHA-256 provenance, every paper number asserted by a test.
- July 2026 `claude -p` re-measurement published as a redacted extract, with the corrected model attribution (Fable 5, safety prompts answered by Opus 4.8).
- Both papers revised against the derived numbers and rebuilt as PDFs.
- Demo recordings and figures as code; translations regenerated from the revised English.
- Runner no longer sets a permission mode (shipped in 1.0.4).

## Next: third `claude -p` snapshot

Run the protocol in [`PREREGISTRATION.md`](PREREGISTRATION.md) after it is deposited: pinned model, two turn caps, clean-room precondition, deterministic primary outcome.

## Open, and not claimed until done

| Item | Why it matters | Blocker |
|---|---|---|
| Blind re-authoring of the five benchmark expected lists by independent engineers | The 80% GREEN match is against lists the author wrote; only independent lists remove the within-task circularity | Needs two or more outside reviewers |
| MAST ablation with a blind placebo prompt | Tests whether the 14-mode enumeration, not prompt length or framing, drives the GREEN effect | Needs the blind lists above first |
| Human second rater on the July 2026 labels | The 40% rests on one non-blind rater; an LLM panel agreed but shares lineage with the model under test | Needs one outside human rater |
| Colab notebook | Zero-setup Track 1 verification in the browser | None; planned for v2.1 |
