---
description: "ASP (Ant-Shadow-Point) — full lifecycle: research, pre-mortem, validated plan, contractual micro-TODO, /goal-driven execution, deliverables sign-off"
allowed-tools: [Skill, Agent, TaskCreate, TaskUpdate, TaskList, Bash, Read, Grep, Glob, Write, Edit, AskUserQuestion]
---

# /asp — Ant-Shadow-Point Protocol

Invoke the `anticipating-shadow-points` skill on this task:

$ARGUMENTS

## Depth flags

- `--quick` — skip independent validator, skip `/goal` (manual execution).
- `--standard` (default) — pre-mortem + MAST 14-mode + 1 validator round + `/goal`.
- `--paranoid` — + `advisor()` + 2 validators + 3 rounds + strict `/goal` evaluator.
- `--no-goal` — anything above but skip `/goal` kernel (fallback to `executing-plans` skill).

## Invocation rules

1. Load the `anticipating-shadow-points` skill via the `Skill` tool, not `Read`.
2. Follow the 13-phase protocol in order. Skip a phase only if explicitly permitted by the skill (e.g., Phase 0b zero questions OK).
3. Iron Laws are non-negotiable. See `SKILL.md`.
4. The non-violation contract must be acknowledged by the user before Phase 9 execution.
