---
name: anticipating-shadow-points
description: Use when starting any non-trivial task (feature, refactor, migration, deploy, schema change, debug, investigation, architecture decision) that needs deep upfront research, pre-mortem failure-mode anticipation, validated macro plan, contractual micro-TODO, autonomous execution via /goal, and deliverables sign-off. Brand ASP / Ant-Shadow-Point. Invoke via /asp or /ASP.
---

# Anticipating Shadow Points (ASP)

## Overview

**ASP IS Plan-Validate-Execute discipline applied to agentic work, with explicit pre-mortem detection of hidden failure modes ("Ant-Shadow-Points") before any line of code is written.**

Core principle: **No implementation without shadow-point pass first.** Every non-trivial task gets researched, pre-mortemed, planned, validated by an independent agent, contracted into a micro-TODO, executed via `/goal` with built-in evaluator, signed-off per-deliverable, and closed with memory write-back.

**REQUIRED BACKGROUND:** Read `methodology.md` (Klein pre-mortem, Berkeley MAST 14-mode, Plan-Validate-Execute, Reflexion critic-refine, /goal integration). Read `mast-checklist.md` before Phase 2.

## When to Use

```
Is the task...
├── trivial single-edit, doc fix, rename? -> SKIP ASP, just do it
├── purely informational (read/explain)? -> SKIP ASP
├── feature / refactor / migration / deploy / schema-change? -> USE ASP
├── debug requiring root-cause investigation? -> USE ASP
├── architecture decision? -> USE ASP
└── anything you'd later wish you had planned? -> USE ASP
```

Symptoms that demand ASP: data migration, RLS/permissions change, multi-file refactor, deploy with external dependencies, time/timezone logic, concurrency, cost-sensitive operations, cross-team contracts, security boundary.

## The 13 Phases

| # | Phase | Output |
|---|---|---|
| 0a | Pre-research Q&A (≤3 questions: scope/constraints) | Intake block |
| 1 | Parallel research (codebase + web + .agent/ recall) | "Consulted lessons before acting:" block |
| 0b | Post-research Q&A (≤3 questions: tradeoffs that emerged) | Refined intake; skip if nothing ambiguous |
| 2 | Shadow-Point Detection (Klein pre-mortem + MAST 14-mode) | Categorized shadow-point list + mitigations |
| 3 | Project Charter (`templates/project-charter.md`) | Filled charter |
| 4 | Macro Plan + Deliverables Register | Macro plan + numbered deliverables D01..Dn |
| 5 | Independent validator (separate-prompt subagent) | APPROVE / REVISE |
| 6 | Internal loop cap=3 + optional `advisor()` | Final-revision plan |
| 7 | User approves charter + macro plan + deliverables | Go/No-Go |
| 8 | Micro-TODO contract (`TaskCreate`) + Goal Spec | N tasks with PRE/ACT/POST/ACC/FAL/DEPENDS/DELIVERABLE-ID + completion condition |
| 9 | Execution via `/goal` (worker + evaluator built-in) | Tasks completed with fresh evidence |
| 10 | Deliverables sign-off (per-deliverable acceptance) | All Deliverables `aceito` |
| 11 | Execution Report + memory write-back | Closure artifact + `memory_reflect`/`learn.py` |
| 12 | (Opt-in) Public release (`install.sh` + GitHub) | Only on explicit user approval |

## Five Primitives — How ASP Wires Them

| Primitive | Role | Phases |
|---|---|---|
| `Agent` subagents | Parallel research (Phase 1) + independent validator (Phase 5) | 1, 5 |
| `using-superpowers` skill | Continuous routing of relevant skills (brainstorming, systematic-debugging, verification-before-completion, writing-plans, executing-plans) | All |
| `advisor()` tool | High-signal review by stronger model; reads full transcript | 6 (--paranoid), 11 (before close) |
| `loop` skill | Recurring opt-in supervision post-acceptance (NOT internal iteration) | 9 (opt-in only) |
| **`/goal` native (Claude Code 2.1.139+)** | Autonomous multi-turn execution kernel with built-in evaluator | 9 |

> [!WARNING]
> **`loop` skill ≠ convergence loop.** `loop` schedules recurring runs ("execute X every 10min"). The validator-cap=3 in Phase 6 is normal control flow. The execution-until-done loop is **`/goal`** built-in. Three distinct concepts.

## Iron Laws (non-negotiable)

1. **NO IMPLEMENTATION WITHOUT SHADOW-POINT PASS FIRST.**
2. **NO PLAN APPROVAL WITHOUT INDEPENDENT VALIDATOR PASS** (validator prompt MUST be separate from planner transcript).
3. **NO MICRO-TODO WITHOUT MACRO PLAN + CHARTER + DELIVERABLES APPROVED BY USER.**
4. **NO STEP COMPLETION WITHOUT FRESH ACCEPTANCE-TEST EVIDENCE.**
5. **NO DELIVERABLE `aceito` WITHOUT EVIDENCE FILE/OUTPUT MATCHED.**
6. **NO PROJECT CLOSE WITHOUT EXECUTION REPORT + MEMORY WRITE-BACK.**
7. **NO LOOP WITHOUT CAP** (validator cap=3; `/goal` has its own hard stops).
8. **(v4) NO PHASE 9 EXECUTION WITHOUT EVALUATOR DISPATCH AT CHECKPOINTS** (unless `--quick` flag chosen).
9. **(v5) NO REENTRANT ASP INSIDE `claude -p /goal` CHILD** — child detects `ASP_IN_GOAL=1` env var and refuses re-entry.
10. **(v5) NO `claude -p /goal` SPAWN WITHOUT FILE-BASED CONTRACT** — child operates on `~/Developer/ASP/runtime/<session-id>/` scratch dir with Goal Spec + state.json + exec.json.
11. **(v5) NEVER TRUST `$?` FROM `claude -p` FOR SEMANTIC SUCCESS/FAILURE** — Claude returns exit 0 even when it gracefully refuses. Parse `is_error`, `terminal_reason`, `stop_reason` from JSON output.
12. **(v5) ALL `claude -p` INVOCATIONS MUST USE `--output-format json` OR `--output-format stream-json`** — text output is unparseable and breaks Iron Law 11.

## Pre-flight: `/goal` invocability check

On **first real run** of this skill, before relying on `/goal` in Phase 9, verify empirically that `/goal` is invocable from skill context. If verification fails, force `--no-goal` as default and document in `tests/goal-invocability-probe.md`. This is ASP applying its own shadow-point discipline to its own assumptions.

## Depth Flags

| Flag | Behavior | Relative cost |
|---|---|---|
| `--quick` | Skip validator + skip `/goal` (manual execution) | 1x |
| `--standard` (default) | Pre-mortem + MAST + 1 validator round + `/goal` | 3x |
| `--paranoid` | + `advisor()` + 2 validators + 3 rounds + strict `/goal` evaluator | 6x+ |
| `--no-goal` | Anything above, but skip `/goal` (fallback to `executing-plans` skill) | -1x |

## Phase 1 — Parallel research (three subagents in one message)

| Subagent | Tool | Focus |
|---|---|---|
| `Explore` | local codebase | existing files, patterns, reusable utilities |
| `general-purpose` | WebSearch + WebFetch | prior art, similar repos, papers, official docs |
| `general-purpose` | Bash -> `python3 .agent/tools/recall.py "<task>"` (only if `~/.agent/` exists) | prior agentic-stack lessons |

Output MUST include `Consulted lessons before acting:` block before Phase 2 starts.

## Phase 2 — Shadow-Point Detection

1. **Pre-mortem prompt**: "It is 30 days in the future. This task failed catastrophically. List 10+ concrete causes."
2. **MAST 14-mode checklist** (`mast-checklist.md`) — for each mode: does it apply here? how?
3. Categorize: spec / data / integration / concurrency / security / observability / op-ex / contract / time-tz / cost.
4. Mandatory mitigation per shadow-point OR explicit risk-acceptance.

## Phase 5 — Independent validator (mandatory pattern)

Spawn a subagent with a **fresh prompt** containing ONLY:
- The project charter
- The macro plan
- The deliverables register
- The shadow-point list and mitigations

The validator must NOT receive the planner's transcript or reasoning trail. Self-critique from the same context fails on high-self-consistency hallucinations (EMNLP 2025). The validator returns `APPROVE` or `REVISE` with specific issues.

## Phase 8 — Contract structure

Each TaskCreate emitted in Phase 8 has a `description` with these labeled blocks:

```
PRECONDITION: <invariant that must be true before>
ACTION: <exact command or literal edit>
POSTCONDITION: <what changed>
ACCEPTANCE-TEST: <command + expected output>
FALSIFICATION-TEST: <command that would prove failure>
DEPENDS-ON: <task subjects that must be completed>
DELIVERABLE-ID: <D01..Dn or - for internal step>
```

And the Goal Spec (`templates/goal-spec.md`):

```
GOAL: <one-line completion condition>
EVALUATOR CRITERIA:
  - All TaskList items completed with ACCEPTANCE-TEST evidence
  - All Deliverables marked `aceito`
  - All Iron Laws respected
HARD STOP CONDITIONS:
  - turn count > N
  - elapsed > hh:mm
  - cost > $X
  - 3 consecutive falsification-test failures with no progress
```

## Phase 9 — Execution kernel (v5)

> [!IMPORTANT]
> **`/goal` is invocable from skill context via `claude -p` subprocess** (empirically verified 2026-05-17 — see `tests/claude-p-goal-runner-probe.md`). The skill spawns a child Claude Code session, pipes `/goal "..."` as first input, captures structured JSON output, and reconciles state with the parent TaskList. This is the primary Phase 9 path. Native in-session kernel (`execution-kernel.md`) is the fallback for short tasks.

### Primary path: `claude -p /goal` subprocess

See `claude-p-goal-runner.md` for the full spawn pattern. High-level flow:

1. Phase 8 renders the Goal Spec to `~/Developer/ASP/runtime/<session-id>/goal-spec.md` and seeds `state.json`.
2. Parent emits a Bash spawn script that runs `claude -p --permission-mode bypassPermissions --output-format json --max-budget-usd $BUDGET --max-turns $MAX_TURNS` with `/goal "..."` piped via stdin, **in background** (`run_in_background: true`).
3. `Monitor` tool watches for child exit; parent stays idle until notified.
4. Post-exit, parent parses `exec.json` via `jq` — extracts `is_error`, `terminal_reason`, `total_cost_usd`, `num_turns`, `result`. **Never trusts `$?`** (Iron Law 11).
5. Parent reconciles task statuses and updates Deliverables Register based on the child's reported work.

**Phase 5 validator ≠ `/goal` evaluator**: Phase 5 validates the PLAN (before execution); the child's built-in `/goal` evaluator validates EXECUTION turn-by-turn. Complementary, not redundant.

### Fallback path: native in-session kernel

See `execution-kernel.md`. Use when:
- Task has <5 micro-steps (subprocess overhead not justified).
- User passed `--no-claude-p` flag explicitly.
- `claude` CLI is missing from `$PATH`.
- Inside a child session (`ASP_IN_GOAL=1`) — Iron Law 9 prevents recursion.

### Opt-in alternative: user-typed `/goal`

The user MAY also manually type `/goal "..."` in their interactive Claude Code terminal using the rendered Goal Spec. This is a third mode, complementary to the primary `claude -p` subprocess path. Useful when the user wants to drive autonomous mode interactively rather than via skill-triggered spawn.

### `--no-claude-p` flag

Forces the native in-session kernel even when `claude` is available. Useful in CI / batch contexts where subprocess spawn is undesired.

### `--no-kernel` flag

Skips both kernels and delegates to vanilla `executing-plans` skill. Manual step-by-step, no autonomous execution.

### Why this design

Empirical probe (2026-05-17 battery) confirmed `claude -p /goal` is the right primitive. The probe also surfaced **critical finding C**: Claude returns exit 0 even when it gracefully refuses the goal — Iron Laws 11 (parse JSON, never trust `$?`) and 12 (always use `--output-format json` or `stream-json`) are mandatory to use this kernel safely. See `tests/claude-p-goal-runner-probe.md` Section 3 for the empirical evidence.

## Red Flags / Rationalizations × Counter

| Thought | Reality |
|---|---|
| "This is simple enough to skip ASP" | If it touches data, integration, or shared state — it's not simple. Use ASP. |
| "I already know the failure modes" | Then write them down — that's the pre-mortem output. Skipping discovery vs skipping artifact are different. |
| "Validator is overkill — I'm confident" | Self-critique fails on the cases you're most confident about. Validator is for blind spots. |
| "The TODO is too granular" | The TODO IS the contract. Coarse TODOs = unverifiable promises. |
| "I'll write the report after we ship" | Memory write-back done now > done never. Phase 11 is mandatory. |
| "/goal feels like overhead" | `/goal` separates worker from evaluator officially (or the user mediates if /goal isn't tool-callable — see `tests/goal-invocability-probe.md`). |
| "Let me just start, I'll plan as I go" | Iron Law 1 violation. No implementation without shadow-point pass first. |
| "The optimization X applies, so we're fine" | Even when a known optimization removes one failure mode, the MAST 14-mode pass must still run for the rest. |
| "Single PR is simpler" | Single PR ≠ better PR. Phase 4 deliverables register forces per-deliverable acceptance, surfacing whether a split improves reviewability. |
| "Manual smoke test is enough" | Iron Law 4 + ACCEPTANCE/FALSIFICATION schema rejects manual-only verification — the contract requires automated, reproducible evidence. |

## Load-bearing observation (from GREEN baseline runs)

The component that most reliably elevates baseline competence to gold-standard rigor is the **MAST 14-mode forced-categorization pass**. Free-form pre-mortem alone tends to cluster on a few obvious categories; the MAST checklist forces coverage of less-intuitive categories (time/tz, observability, op-ex, contract drift). Without it, expected-shadow-point coverage stays around 50%; with it, coverage exceeds 95% in baseline evals.

## Cross-references

- `methodology.md` — full methodology + sources (Klein, MAST, Plan-and-Act, Anthropic Plan-Validate-Execute, Reflexion)
- `mast-checklist.md` — 14 failure modes with per-mode pre-mortem prompts
- `question-frames.md` — Pre/post-research Q&A frames (≤3 questions each)
- `templates/` — project-charter, macro-plan, deliverables-register, micro-todo, goal-spec, acceptance-contract, execution-report
- `evals/` — 5 structured evaluations with expected shadow-point lists

## Sources

- Klein pre-mortem (1998/2007) — prospective hindsight, +30% risk-identification lift.
- Berkeley MAST 14 failure modes — arxiv 2503.13657.
- Plan-and-Act — arxiv 2503.09572.
- Anthropic Plan-Validate-Execute — platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.
- Reflexion / critic-refine — EMNLP 2025 (self-critique limits).
- Claude Code `/goal` — release 2.1.139, 2026-05-12.
