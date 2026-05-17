# Acceptance Contract — Non-Violation Commitment

> ASP Phase 8 emission. This text is shown verbatim to the user; user must explicitly acknowledge before Phase 9 begins.

---

## Contract text

> I hereby commit to executing the {{N}} micro-steps listed in the TaskList in the order specified by their DEPENDS-ON dependencies, **without skipping, merging, or reordering** any step without explicit user approval.
>
> Each task will only be marked `completed` after its **ACCEPTANCE-TEST** passes with fresh evidence captured and persisted (in `tests/` or commit body or task metadata).
>
> Each **Deliverable** (D01..D{{n}}) listed in `deliverables-register.md` will only be `aceito` after its required evidence is validated against the acceptance criterion.
>
> If a task fails its **FALSIFICATION-TEST**, I will stop immediately and re-enter the ASP protocol from the appropriate phase (typically Phase 2 shadow-point re-detection or Phase 4 macro-plan revision).
>
> If `/goal` is active (Phase 9), its built-in evaluator may interrupt at any turn if EVALUATOR CRITERIA fail. I will respect that interruption.
>
> If any **Iron Law** is on the verge of violation, I will halt and surface the conflict, not rationalize past it.
>
> I will NOT make unsanctioned destructive operations (force-push, branch deletion, schema drop, prod deploy) — these always require explicit user approval, even within autonomous execution.

---

## User acknowledgement

- [ ] User explicitly acknowledged this contract on YYYY-MM-DD HH:MM
- [ ] User selected execution mode: manual-supervised / autonomous-via-/goal / autonomous-with-bypassPermissions
- [ ] User selected depth: --quick / --standard / --paranoid
- [ ] User explicitly opted in or out of Phase 12 public release

---

## Re-entry protocol (if FALSIFICATION fires)

1. Halt current task at fail point.
2. Mark task `in_progress` -> revert if partial side effects.
3. Document failure in `tests/falsification-<task-id>.md`.
4. Re-enter ASP at:
   - Phase 2 if shadow-point was missed.
   - Phase 4 if plan was incorrect.
   - Phase 8 if step decomposition was wrong.
5. Update Deliverables Register status to `rejeitado` for affected D-IDs.
6. Resume only after user re-approves revised artifact.
