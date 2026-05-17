# ASP Methodology — Foundations

This document is the deep reference behind `SKILL.md`. Read it once; SKILL.md cross-references it for justifications.

## 1. Klein's Pre-Mortem (1998 / 2007)

**Technique**: Prospective hindsight. Instead of asking "what could go wrong?", ask "Imagine it is N days from now and this task failed catastrophically. List the concrete causes."

**Why it works**: Forces the brain to commit to a failure narrative. Subjects identify ~30% more risks than naive forward-looking risk analysis. The retrospective framing bypasses optimism bias.

**ASP application** — Phase 2 fixed prompt:

> "Estamos 30 dias no futuro. A tarefa falhou catastroficamente. Liste 10+ causas concretas. Cada causa deve ser específica o suficiente para ter um nome (não 'algo deu errado')."

Output must produce ≥10 concrete causes, each with a name and a one-line description.

## 2. Berkeley MAST — 14 Multi-Agent System Failure Modes

**Source**: arxiv 2503.13657.

The 14 modes are organized into 3 families:

### Family A — Specification (5 modes)
1. **Spec ambiguity** — task description allows multiple interpretations.
2. **Goal misalignment** — agent goal drifts from user goal.
3. **Implicit assumptions** — agent assumes context not in prompt.
4. **Hidden constraints** — real-world constraints not surfaced.
5. **Success-criteria gap** — agent declares done before user's definition met.

### Family B — Inter-agent coordination (6 modes)
6. **Information loss** — handoff between agents drops critical context.
7. **Premature termination** — agent stops before subtask complete.
8. **Wrong delegation** — agent assigns task to subagent ill-suited.
9. **Validator collusion** — validator shares biases with worker.
10. **Infinite loop** — re-validation cycle never converges.
11. **Conflicting outputs** — two agents produce incompatible artifacts.

### Family C — Verification (3 modes)
12. **No acceptance test** — work declared done without test passing.
13. **Falsification gap** — no test would prove the work failed.
14. **Evidence loss** — accept-test evidence not durable / not captured.

**ASP application** — Phase 2 step 2: for each of the 14 modes, ask "Does this mode apply to my task? Specifically how?"

`mast-checklist.md` has a per-mode pre-mortem prompt.

## 3. Plan-and-Act separation (arxiv 2503.09572)

**Principle**: The agent that plans ≠ the agent that executes. Different cognitive modes, different prompts, different reasoning chains.

**ASP application**:
- Planner phases: 0a, 1, 0b, 2, 3, 4 (one agent, planning mode).
- Validator phase: 5 (separate agent, validating mode).
- Worker phases: 8 micro-step execution.
- Evaluator phase: 9 (separate agent or `/goal` built-in).

## 4. Anthropic Plan-Validate-Execute (official guidance)

**Source**: platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.

**Principle**: "Create verifiable intermediate outputs." Each phase emits an artifact that the next phase consumes. Failures are localized — you know exactly which artifact caused the rejection.

**ASP application** — every phase emits a named artifact:

| Phase | Artifact |
|---|---|
| 0a | `intake.md` (in scratchpad) |
| 1 | `research-summary.md` + `Consulted lessons before acting:` block |
| 2 | `shadow-points.md` (categorized list) |
| 3 | filled `project-charter.md` |
| 4 | filled `macro-plan.md` + `deliverables-register.md` |
| 5 | `validator-verdict.md` |
| 8 | TaskList entries + filled `goal-spec.md` + filled `acceptance-contract.md` |
| 9 | TaskList entries marked completed with evidence paths |
| 10 | deliverables-register with all rows `aceito` |
| 11 | filled `execution-report.md` |

## 5. Reflexion + critic-refine, but with prompt separation

**Source**: Reflexion paper + EMNLP 2025 work on self-critique limits.

**Finding**: When the critic is the same context as the worker, the critic fails on high-self-consistency hallucinations — the cases the worker is most confident about and most wrong. Prompt separation (validator subagent gets a fresh context with only the artifacts) breaks this collusion.

**ASP application** — Phase 5 validator MUST be a separate prompt with only the planner's artifacts (not the transcript or reasoning trail).

## 6. `/goal` integration (Anthropic Claude Code 2.1.139, 2026-05-12)

**Mechanism**: `/goal "<completion-condition>"` lets the agent work autonomously across turns. A built-in evaluator agent reviews after each turn and decides if the completion condition is satisfied. Tracks turn count, elapsed time, and token spend natively.

**Why ASP uses it**:
- Replaces hand-rolled validator-loop in execution phase.
- Officially separates worker from evaluator (matches Plan-and-Act principle).
- Provides cost/time tracking we'd otherwise build manually.
- Documented hard-stop conditions prevent infinite loops (MAST mode 10).

**ASP application** — Phase 9 entry point:

```
/goal "<EVALUATOR CRITERIA from goal-spec.md>"
```

If `/goal` is not invocable from skill context (pre-flight probe documented in `tests/goal-invocability-probe.md`), force `--no-goal` and fallback to `executing-plans` skill.

## 7. TDD-for-skills (writing-skills meta-skill)

**Source**: `~/.claude/skills/writing-skills/SKILL.md`.

**Principle**: Every skill is documentation that must pass a RED test (agent violates without skill) and a GREEN test (agent complies with skill). Refactor closes loopholes.

**ASP application** — building ASP itself requires:
- 3 baseline scenarios (RED) documented in `tests/baseline-pressure-tests.md`.
- 3 re-runs with the skill loaded (GREEN) showing compliance.
- 1 REFACTOR cycle plugging new rationalizations into SKILL.md.
- 5 evals in `evals/` with expected shadow-point coverage ≥80%.

## 8. The "Ant-Shadow-Point" coinage

This is the user's terminology, not academic. It maps onto Klein's "prospective hindsight" + MAST's "failure mode" but emphasizes the *easily missed* nature of these points — like ants in shadows, they're there but invisible until pointed at.

ASP's value proposition: making the shadows scannable via structured pre-mortem + MAST checklist, before they become bugs.
