# MAST 14-Mode Checklist — Per-Mode Pre-Mortem Prompts

Source: Berkeley arxiv 2503.13657 — "Multi-Agent System Failure Taxonomy".

For each task in Phase 2, ask the per-mode prompt. Record applicability and mitigation.

---

## Mode 1 — Specification ambiguity

**Description**: The task description allows multiple plausible interpretations.

**Pre-mortem prompt**: "Three different engineers read this task. Each interpreted it differently. Which three interpretations are possible, and which did we silently pick?"

**Symptoms**: 'I assumed X but the user meant Y'. PR-review back-and-forth on what was actually requested.

**Default mitigation**: Phase 0a question forcing scope clarification; explicit out-of-scope list in charter.

---

## Mode 2 — Goal misalignment

**Description**: Agent goal drifts from user goal during execution.

**Pre-mortem prompt**: "Mid-execution, the agent decided a tangent was more important. What tangent was tempting enough to derail focus?"

**Symptoms**: Refactoring during a bug fix. Adding features during a refactor.

**Default mitigation**: Iron Law in micro-TODO: no scope expansion without re-entering Phase 4. `/goal` evaluator catches drift turn-by-turn.

---

## Mode 3 — Implicit assumptions

**Description**: Agent assumes context that wasn't in the prompt (env vars, file existence, network access, permissions).

**Pre-mortem prompt**: "If we ran this on a fresh laptop with only the repo and no other state, which step would silently fail?"

**Symptoms**: ENOENT, ECONNREFUSED, missing env var, command-not-found.

**Default mitigation**: Every micro-step has a PRECONDITION block that names the assumed state.

---

## Mode 4 — Hidden constraints

**Description**: Real-world constraints (rate limits, compliance, business rules) not surfaced in the prompt.

**Pre-mortem prompt**: "What law, contract, or external rate-limit are we about to violate that nobody mentioned?"

**Symptoms**: Hitting API rate limits in production. Compliance team blocks deploy.

**Default mitigation**: Phase 1 research includes 'constraints' search. Phase 0a asks about deadlines, compliance, third-party limits.

---

## Mode 5 — Success-criteria gap

**Description**: Agent declares 'done' before user's actual definition of done is met.

**Pre-mortem prompt**: "We marked it done. The user opened it 24h later and said 'this isn't what I wanted'. What was the gap?"

**Symptoms**: Re-opened PRs. 'It works on my machine'.

**Default mitigation**: Phase 0a asks for measurable success criteria. Deliverables Register has 'Aceite (criterion)' column. Phase 10 sign-off per deliverable.

---

## Mode 6 — Information loss

**Description**: Critical context dropped during agent-to-agent handoff (e.g., planner to executor).

**Pre-mortem prompt**: "What did the planner know that the executor would need but won't get in the handoff?"

**Symptoms**: Executor re-asks questions. Executor makes different assumption than planner.

**Default mitigation**: Charter + Macro Plan + Deliverables Register are durable artifacts handed forward, not transcript context.

---

## Mode 7 — Premature termination

**Description**: Agent stops before subtask actually complete (often because output 'looked right').

**Pre-mortem prompt**: "Each micro-step has an ACCEPTANCE-TEST. Which step's test could pass while the work is actually broken?"

**Symptoms**: 'Compiles' = 'done'. 'Returns 200' = 'feature works'.

**Default mitigation**: ACCEPTANCE-TEST must check the postcondition, not just the action. FALSIFICATION-TEST documents what failure would look like.

---

## Mode 8 — Wrong delegation

**Description**: Task delegated to a subagent type ill-suited (Explore for synthesis, general-purpose for narrow lookup).

**Pre-mortem prompt**: "Which subagent dispatch could come back with garbage because we picked the wrong agent type?"

**Symptoms**: Explore agent returns 'I couldn't find anything' on a synthesis question. general-purpose burns 20 tool calls for a single grep.

**Default mitigation**: Phase 1 subagent matrix in SKILL.md is fixed — Explore for codebase, general-purpose for web + recall.

---

## Mode 9 — Validator collusion

**Description**: Validator shares biases or context with worker, so blind spots are shared.

**Pre-mortem prompt**: "Both planner and validator are the same model. What kind of mistake would they both confidently miss?"

**Symptoms**: 'I asked the validator and it agreed' on the exact case that turned out broken.

**Default mitigation**: **Iron Law 2** — validator gets fresh prompt with only the artifacts, NEVER the planner's transcript.

---

## Mode 10 — Infinite loop

**Description**: Re-validation or critic-refine cycle never converges.

**Pre-mortem prompt**: "The validator keeps saying REVISE. After how many rounds do we stop and ask the human?"

**Symptoms**: 4th round of 'almost there'. Agent spends an hour on a 10-min task.

**Default mitigation**: **Iron Law 7** — validator cap=3 rounds, then escalate to `advisor()` or human. `/goal` has hard-stop conditions.

---

## Mode 11 — Conflicting outputs

**Description**: Two agents produce incompatible artifacts (e.g., one says 'use library X', another writes code using library Y).

**Pre-mortem prompt**: "Our 3 parallel research subagents will return findings. Which pair could contradict each other and which decision rule resolves it?"

**Symptoms**: Mid-execution: 'wait, but the other agent said the opposite'.

**Default mitigation**: After Phase 1, planner synthesizes findings explicitly, flagging contradictions, before Phase 0b.

---

## Mode 12 — No acceptance test

**Description**: Work declared done without any test passing — only a vibe check.

**Pre-mortem prompt**: "If we look at the TODO right now, which task's ACCEPTANCE-TEST field is empty or vague?"

**Symptoms**: 'Acceptance: works correctly'. No command, no expected output.

**Default mitigation**: Phase 8 emission rejects any task with empty ACCEPTANCE-TEST. Each test names a command and an expected output.

---

## Mode 13 — Falsification gap

**Description**: No test would have proven the work failed — we only check for success signals.

**Pre-mortem prompt**: "If this work is broken, what would we see? Is that observable today?"

**Symptoms**: Silent failures. Bug surfaces weeks later.

**Default mitigation**: Each micro-step has a FALSIFICATION-TEST field naming what failure would look like.

---

## Mode 14 — Evidence loss

**Description**: Acceptance-test evidence not durable or not captured (was in scrollback, now gone).

**Pre-mortem prompt**: "The acceptance test passed in the moment. Six months later, someone asks 'how do we know?'. What can we show?"

**Symptoms**: 'I saw it work in a terminal but didn't save the output'.

**Default mitigation**: Phase 9 captures evidence in `tests/eval-*.md` or commit body. Phase 11 Execution Report includes evidence paths.

---

## Aggregate gate

Before exiting Phase 2, confirm:
- Every mode that *applies* has a documented mitigation OR explicit risk acceptance.
- No mode is left as 'not applicable' without one-line justification.
- Output is a categorized shadow-point list ready to feed into Phase 3 charter.
