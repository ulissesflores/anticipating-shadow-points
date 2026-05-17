# /goal Invocability Probe — Phase 9 pre-flight

> Iron Law mandate (from `skill/SKILL.md` Phase 9): before relying on `/goal` as the execution kernel, verify empirically whether `/goal` is invocable from within a skill context.

## Probe date

2026-05-16

## Method

Analytical reasoning + Anthropic docs review (Claude Code 2.1.139 release notes):

1. `/goal` is a **slash command** parsed by the Claude Code CLI harness, not the model.
2. Slash commands are recognized when the **user types** them into their terminal session.
3. Text emitted by the assistant (the model) is rendered as output, **not parsed back as commands**.
4. Therefore: a skill context that emits the literal string `/goal "..."` does NOT cause the harness to invoke `/goal` — it just shows that string to the user.

## v5 update (2026-05-17)

**REVISED**: The original FAIL verdict applies only to **direct emission within the SAME session**. Subsequent empirical testing (see `tests/claude-p-goal-runner-probe.md`) confirmed that `/goal` CAN be invoked from skill context via the `claude -p` subprocess pattern:

```bash
echo '/goal "..."' | claude -p --permission-mode bypassPermissions --output-format json
```

This spawns a child Claude Code session that DOES parse and execute `/goal`. The skill can therefore use `/goal` as the primary Phase 9 execution kernel by spawning subprocesses, not by emitting text in its own session.

The original FAIL still stands for "emit `/goal` and have current session execute it" — that path remains impossible. But the subprocess path is fully functional.

**v5 implication**: Native in-session kernel (v4 design) becomes the FALLBACK; `claude -p /goal` subprocess becomes the PRIMARY Phase 9 execution mode. See `claude-p-goal-runner.md` for spawn pattern.

---

## Original verdict (still valid for same-session invocation)

**FAIL** — `/goal` cannot be invoked from within skill context as if it were a tool call.

## Implication for ASP design

Phase 9 (Execution via `/goal`) must be reframed as a **two-step** pattern:

### Old (incorrect) Phase 9 model

> The skill calls `/goal "<completion-condition>"` and the harness runs autonomously.

### New (correct) Phase 9 model

1. Phase 8 emits the Goal Spec to the user as part of the acceptance contract.
2. The user, after acknowledging the contract, can **manually type** `/goal "<the completion condition>"` into their terminal to enter autonomous mode.
3. Alternatively, the skill proceeds in **`--no-goal` fallback mode**, executing tasks via the `executing-plans` skill within the same conversation.

## Default behavior change

Until Anthropic adds a tool-callable form of `/goal` (e.g., an API or programmatic invocation), the **default mode of ASP becomes `--no-goal`**. The Goal Spec is still emitted, but it serves as a *script the user can run* rather than a *kernel the skill invokes*.

## What this preserves

- The plan's separation of planner (Phases 0-7) from executor (Phase 9): still intact, because the user mediates the handoff.
- The contract / acceptance-test discipline: unchanged, still enforced per task.
- Cost tracking: lost (no native turn/time/token counter from `/goal`); skill must self-report.
- Built-in evaluator: lost; ASP falls back to its Phase 5-style validator pattern at periodic checkpoints during execution.

## What changes in user-facing docs

- README.md and `SKILL.md`: rewrite Phase 9 to describe the two-step pattern.
- `goal-spec.md` template: add a note "Output of this template is shown to the user as a command they may type to enter autonomous mode."
- Flag matrix: `--no-goal` becomes the default (current default `--standard` implicitly includes `--no-goal` until /goal is callable).

## Re-probe trigger

If Anthropic releases a programmatic `/goal` invocation (tool-callable, API-exposable, or hook-driven), re-run this probe and update the design.

## Conclusion

ASP ships in `--no-goal` mode by default. The Goal Spec is emitted as **guidance for the user**, not an autonomous kernel. The rest of the protocol (research, pre-mortem, validator, contract, sign-off, memory write-back) is unaffected.
