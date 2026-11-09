---
name: anticipating-shadow-points
description: Use when starting a non-trivial engineering task (feature, refactor, migration, deploy, schema change, root-cause debugging, architecture decision) that should be planned before any code is written - research, a pre-mortem with the MAST failure-mode checklist, a plan checked by an independent subagent, a task list with acceptance tests, optional execution in a separate claude -p session, and per-deliverable sign-off. Invoke via /asp.
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
| 1 | Parallel research (codebase + web + the project's own lessons, if any) | "Consulted lessons before acting:" block |
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
| 11 | Execution Report + lessons write-back | Closure artifact + lessons recorded where the project keeps them |
| 12 | (Opt-in) Publish or release | Only on explicit user approval |

## Five Primitives — How ASP Wires Them

| Primitive | Role | Phases |
|---|---|---|
| `Agent` subagents | Parallel research (Phase 1) + independent validator (Phase 5) | 1, 5 |
| Process skills, if installed | Route to relevant skills the user already has (for example brainstorming, systematic debugging, verification before completion, writing and executing plans). ASP does not require any of them | All |
| `advisor()` tool, where available | High-signal review by a stronger model that reads the full transcript; skip it when the tool is absent | 6 (--paranoid), 11 (before close) |
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
10. **(v5) NO `claude -p /goal` SPAWN WITHOUT FILE-BASED CONTRACT** — child operates on the `<runtime root>/<session-id>/` scratch dir (see Runtime directory below) with Goal Spec + state.json + exec.json.
11. **(v5) NEVER TRUST `$?` FROM `claude -p` FOR SEMANTIC SUCCESS/FAILURE** — Claude returns exit 0 even when it gracefully refuses. Parse `is_error`, `terminal_reason`, `stop_reason` from JSON output.
12. **(v5) ALL `claude -p` INVOCATIONS MUST USE `--output-format json` OR `--output-format stream-json`** — text output is unparseable and breaks Iron Law 11.

## Runtime directory

Phase 9 keeps its scratch files (Goal Spec, `state.json`, `exec.json`, logs) under one runtime root:

- **Installed as a plugin:** `${CLAUDE_PLUGIN_DATA}/runtime`. Claude Code substitutes that path when it loads this skill. The folder belongs to the plugin, survives plugin updates, and is deleted when the plugin is uninstalled.
- **Copied by hand into `~/.claude/skills/`** (the line above then shows the literal `${CLAUDE_PLUGIN_DATA}`): use `${XDG_STATE_HOME:-$HOME/.local/state}/asp/runtime`.

ASP writes nothing else outside the user's project.

## What Phase 9 does on the user's machine (say it before spawning)

The primary Phase 9 path starts a **second, headless Claude Code session** (`claude -p`) that works on the plan without the user watching each step. Before the first spawn, tell the user in plain words, and spawn only after they agree at Phase 7:

- it runs with **their own Claude Code permission settings**; ASP passes no permission flag and never widens them, so an action they have not pre-allowed is denied, not prompted;
- it **uses their plan or API usage**, capped by `--max-budget-usd` and `--max-turns` (state the values);
- its scratch files go to the runtime root above.

If the user declines, use the in-session kernel (`--no-claude-p`) instead.

## Pre-flight: `/goal` invocability check

On **first real run** of this skill, before relying on `/goal` in Phase 9, verify empirically that `/goal` is invocable from skill context. If verification fails, force `--no-goal` as default, tell the user, and record it in the Execution Report. This is ASP applying its own shadow-point discipline to its own assumptions.

## Depth Flags

| Flag | Behavior | Relative cost |
|---|---|---|
| `--quick` | Skip validator + skip `/goal` (manual execution) | 1x |
| `--standard` (default) | Pre-mortem + MAST + 1 validator round + `/goal` | 3x |
| `--paranoid` | + `advisor()` + 2 validators + 3 rounds + strict `/goal` evaluator | 6x+ |
| `--no-goal` | Anything above, but skip `/goal` (fallback to `executing-plans` skill) | -1x |

## Phase 0a — Entry check (Iron Law 9)

Before asking any Phase 0a question, run this check with the Bash tool. If it prints `REFUSE`, stop: do not continue the skill, and tell the user why.

```bash
if [[ -n "${ASP_IN_GOAL:-}" ]]; then
  echo "REFUSE: ASP cannot re-enter itself inside a /goal child session."
  echo "Iron Law 9 violation prevented."
  exit 1
fi
```

## Phase 1 — Parallel research (three subagents in one message)

| Subagent | Tool | Focus |
|---|---|---|
| `Explore` | local codebase | existing files, patterns, reusable utilities |
| `general-purpose` | WebSearch + WebFetch | prior art, similar repos, papers, official docs |
| `general-purpose` | Read the project's lessons store if it has one (for example a lessons file that `CLAUDE.md` points to); skip when there is none | prior lessons |

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

The validator must NOT receive the planner's transcript or reasoning trail.
The justification is three converging primary findings: (a) Huang et al.
(2024, ICLR) show LLMs cannot reliably self-correct without external
feedback (arxiv 2310.01798); (b) Tyen et al. (2024) show LLMs cannot
*localize* their own reasoning errors but *can* correct them given the
location externally (arxiv 2311.08516); (c) Zheng et al. (2023, NeurIPS
D&B) document a *self-enhancement bias* where LLM judges over-favor outputs
from the same model family (arxiv 2306.05685). The validator returns
`APPROVE` or `REVISE` with specific issues.

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
> **`/goal` is invocable from skill context via `claude -p` subprocess** (empirically verified 2026-05-17 — see the [runner probe](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/claude-p-goal-runner-probe.md)). The skill spawns a child Claude Code session, pipes `/goal "..."` as first input, captures structured JSON output, and reconciles state with the parent TaskList. This is the primary Phase 9 path. Native in-session kernel (`execution-kernel.md`) is the fallback for short tasks.

### Primary path: `claude -p /goal` subprocess

See `claude-p-goal-runner.md` for the full spawn pattern. High-level flow:

1. Phase 8 renders the Goal Spec to `<runtime root>/<session-id>/goal-spec.md` and seeds `state.json`.
2. Parent emits a Bash spawn script that runs `claude -p --output-format json --max-budget-usd $BUDGET --max-turns $MAX_TURNS` with `/goal "..."` piped via stdin, **in background** (`run_in_background: true`). The script passes **no permission flag**: the child inherits the user's own Claude Code permission settings, and ASP never grants, widens or bypasses them. Actions the user has not pre-allowed are denied in `-p` mode; if the child stalls on a denial, report it to the user and let them decide how to proceed.
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

Empirical probe (2026-05-17 battery) confirmed `claude -p /goal` is the right primitive. The probe also surfaced **critical finding C**: Claude returns exit 0 even when it gracefully refuses the goal — Iron Laws 11 (parse JSON, never trust `$?`) and 12 (always use `--output-format json` or `stream-json`) are mandatory to use this kernel safely. See Section 3 of the [runner probe](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/claude-p-goal-runner-probe.md) for the empirical evidence.

## Red Flags / Rationalizations × Counter

| Thought | Reality |
|---|---|
| "This is simple enough to skip ASP" | If it touches data, integration, or shared state — it's not simple. Use ASP. |
| "I already know the failure modes" | Then write them down — that's the pre-mortem output. Skipping discovery vs skipping artifact are different. |
| "Validator is overkill — I'm confident" | Self-critique fails on the cases you're most confident about. Validator is for blind spots. |
| "The TODO is too granular" | The TODO IS the contract. Coarse TODOs = unverifiable promises. |
| "I'll write the report after we ship" | Memory write-back done now > done never. Phase 11 is mandatory. |
| "/goal feels like overhead" | `/goal` separates worker from evaluator officially (or the user mediates if /goal isn't tool-callable — see the [invocability probe](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/goal-invocability-probe.md)). |
| "Let me just start, I'll plan as I go" | Iron Law 1 violation. No implementation without shadow-point pass first. |
| "The optimization X applies, so we're fine" | Even when a known optimization removes one failure mode, the MAST 14-mode pass must still run for the rest. |
| "Single PR is simpler" | Single PR ≠ better PR. Phase 4 deliverables register forces per-deliverable acceptance, surfacing whether a split improves reviewability. |
| "Manual smoke test is enough" | Iron Law 4 + ACCEPTANCE/FALSIFICATION schema rejects manual-only verification — the contract requires automated, reproducible evidence. |

## Load-bearing hypothesis (from GREEN baseline runs)

The component that most raises plan quality above the unaided baseline
*appears* to be the **MAST 14-mode forced-categorization pass**.
Free-form pre-mortem alone tends to cluster on a few obvious categories;
the MAST checklist forces coverage of less-intuitive categories
(time/tz, observability, op-ex, contract drift). This is the author's
non-blind reading of the May 2026 subagent plans, whose transcripts were not
preserved; no measurement supports it yet. (The deterministic adjudicator's
published run is a mock run over author-written fixtures and says nothing
about this; see §5 of the [ASP report](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/paper/asp-preprint.md).) **This
attribution is a hypothesis. A real-mode RED-versus-GREEN benchmark is
specified in [`PREREGISTRATION.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/PREREGISTRATION.md) (Protocol 2), but that protocol does not
isolate the MAST checklist: a with-versus-without-MAST ablation has no
protocol yet.**

## Cross-references

- `methodology.md` — full methodology + sources (Klein, MAST, Plan-and-Act, Anthropic Plan-Validate-Execute, Reflexion)
- `mast-checklist.md` — 14 failure modes with per-mode pre-mortem prompts
- `question-frames.md` — Pre/post-research Q&A frames (≤3 questions each)
- `templates/` — project-charter, macro-plan, deliverables-register, micro-todo, goal-spec, acceptance-contract, execution-report
- `evals/` — 5 structured evaluations with expected shadow-point lists

## Sources (primary, verified)

- **Mitchell, Russo & Pennington (1989)** — *Back to the Future: Temporal
  Perspective in the Explanation of Events*, J. Behavioral Decision Making
  2(1), 25–38. Primary study of prospective hindsight; the ~30% figure is Klein's (2007) summary of it.
- **Klein (2007)** — *Performing a Project Premortem*, Harvard Business
  Review 85(9). Operational recipe building on Mitchell et al. 1989.
- **Cemri et al. (2025)** — *Why Do Multi-Agent LLM Systems Fail?* MAST
  14-mode taxonomy derived from 150 seed traces (κ=0.88), with a corpus of
  1,600+ annotated traces. NeurIPS 2025. arxiv 2503.13657.
- **Erdogan et al. (2025)** — *Plan-and-Act*. ICML 2025. arxiv 2503.09572.
- **Huang et al. (2024)** — *Large Language Models Cannot Self-Correct
  Reasoning Yet*. ICLR 2024. arxiv 2310.01798.
- **Tyen et al. (2024)** — *LLMs Cannot Find Reasoning Errors, but Can
  Correct Them Given the Error Location*. arxiv 2311.08516.
- **Zheng et al. (2023)** — *Judging LLM-as-a-Judge with MT-Bench and
  Chatbot Arena*. NeurIPS 2023 D&B. arxiv 2306.05685.
- **Shinn et al. (2023)** — *Reflexion: Language Agents with Verbal
  Reinforcement Learning*. NeurIPS 2023. arxiv 2303.11366.
- **Wang et al. (2026)** — *PreFlect: From Retrospective to Prospective
  Reflection in LLM Agents*. arxiv 2602.07187. Closest concurrent work.
- **Anthropic Agent Skills Best Practices** —
  platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.
- **Claude Code `/goal`** — release 2.1.139, 2026-05-12.

See the [ASP report](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/paper/asp-preprint.md) for the full APA references.
