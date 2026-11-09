---
description: "Plan a non-trivial task before coding: research, pre-mortem, independently checked plan, tasks with acceptance tests, execution and sign-off"
allowed-tools: [Skill, Agent, TaskCreate, TaskUpdate, TaskList, Bash, Read, Grep, Glob, Write, Edit, AskUserQuestion]
---

# /asp — Anticipating Shadow Points

Invoke the `anticipating-shadow-points` skill on this task:

$ARGUMENTS

## Depth flags

- `--quick` — skip independent validator, manual execution.
- `--standard` (default) — pre-mortem + MAST 14-mode + 1 validator round + execution in this session.
- `--paranoid` — + `advisor()` + 2 validators + 3 rounds + strict evaluator.
- `--goal` — opt-in, combines with the above: Phase 9 runs in a separate background `claude -p /goal` session.

## Invocation rules

1. Load the `anticipating-shadow-points` skill via the `Skill` tool, not `Read`.
2. Follow the 13-phase protocol in order. Skip a phase only if explicitly permitted by the skill (e.g., Phase 0b zero questions OK).
3. Iron Laws are non-negotiable. See `SKILL.md`.
4. The non-violation contract must be acknowledged by the user before Phase 9 execution, and, only with `--goal`, before the separate `claude -p` session is started the user is told it runs under their permissions and usage, with the budget and turn cap stated.
