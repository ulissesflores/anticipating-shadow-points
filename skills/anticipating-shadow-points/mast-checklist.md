# MAST 14-Mode Checklist — Per-Mode Pre-Mortem Prompts

> **Primary source**: Cemri, M., Pan, M. Z., Yang, S., Agrawal, L. A., Chopra, B.,
> Tiwari, R., Keutzer, K., Parameswaran, A., Klein, D., Ramchandran, K., Zaharia,
> M., Gonzalez, J. E., & Stoica, I. (2025). *Why do multi-agent LLM systems fail?*
> arXiv:2503.13657. https://arxiv.org/abs/2503.13657
>
> Cemri et al. analyzed 150 traces with κ=0.88 inter-annotator agreement and
> released MAST-Data (1,600+ annotated traces) clustering 14 failure modes into
> 3 categories. **The 14 mode names below are verbatim from the paper.**
>
> ASP operationalizes the canonical taxonomy as a runtime pre-mortem checklist.
> Pre-mortem prompts, symptoms, and mitigations are the ASP author's
> operationalization for in-context use, not from the paper.

For each task in Phase 2, ask the per-mode prompt. Record applicability and
mitigation. Modes are organized by Cemri et al.'s three failure categories
(FC1 / FC2 / FC3).

---

## FC1 — Specification and System Design Failures

### FM-1.1 — Disobey task specification

**Cemri et al. (2025) definition**: *Failure to adhere to the specified
constraints or requirements of a given task.*

**Pre-mortem prompt**: "Three different engineers read this task. Each
interpreted it differently. Which constraints are we silently dropping?"

**Symptoms**: 'I assumed X but the user meant Y'. PR-review back-and-forth
on what was actually requested.

**Default mitigation**: Phase 0a question forcing constraint enumeration;
explicit out-of-scope list in Charter. Iron Law 1 prevents Phase 4 emission
without a charter that names the constraints.

---

### FM-1.2 — Disobey role specification

**Cemri et al. (2025) definition**: *Failure to adhere to the defined
responsibilities and constraints of an assigned role.*

**Pre-mortem prompt**: "The planner subagent is supposed to plan, not
execute. Where in the protocol could it slip into running code instead?"

**Symptoms**: Validator starts proposing implementations. Worker subagent
re-plans mid-execution.

**Default mitigation**: Iron Law 8 (Plan-Validate-Execute separation);
Phase-5 validator prompt explicitly restricts validator to verdict-only.

---

### FM-1.3 — Step repetition

**Cemri et al. (2025) definition**: *Unnecessary reiteration of previously
completed steps in a process.*

**Pre-mortem prompt**: "The agent has 23 micro-TODOs. Which two could it
accidentally re-execute because their preconditions don't capture prior
completion?"

**Symptoms**: Migration applied twice. Same git commit emitted twice with
slightly different messages.

**Default mitigation**: TaskCreate POSTCONDITION must include observable
state change; PRECONDITION must check that state isn't already in the
post state (idempotency).

---

### FM-1.4 — Loss of conversation history

**Cemri et al. (2025) definition**: *Unexpected context truncation,
disregarding recent interaction history.*

**Pre-mortem prompt**: "If this session were to be auto-compressed mid-Phase
9, which Phase-4 decision would the worker forget?"

**Symptoms**: Worker re-asks questions. Planner output ignored after
context window pressure.

**Default mitigation**: Charter, Macro Plan, Deliverables Register, and
Goal Spec are **durable artifact files**, not transcript content. Workers
read from disk, not from memory.

---

### FM-1.5 — Unaware of termination conditions

**Cemri et al. (2025) definition**: *Lack of recognition of criteria that
should trigger termination.*

**Pre-mortem prompt**: "The agent has been working for 45 minutes. What
signal would tell it to stop, and is that signal observable?"

**Symptoms**: Agent burns budget after task is effectively complete. Agent
re-runs validation after APPROVE verdict.

**Default mitigation**: Iron Law 7 (validator cap=3 rounds); Phase 10
sign-off is the explicit termination signal per deliverable.

---

## FC2 — Inter-Agent Misalignment

### FM-2.1 — Conversation reset

**Cemri et al. (2025) definition**: *Unexpected or unwarranted restarting
of a dialogue.*

**Pre-mortem prompt**: "If the validator returns REVISE, does the planner
restart from scratch or refine in place?"

**Symptoms**: Plan loses good parts of v1 when revising for v2. Re-research
that wasn't necessary.

**Default mitigation**: Validator REVISE verdicts must cite *specific*
sections to revise, not request "redo the plan". Iron Law 7 cap=3 plus
mandatory delta-only revisions.

---

### FM-2.2 — Fail to ask for clarification

**Cemri et al. (2025) definition**: *Inability to request additional
information when faced with unclear data.*

**Pre-mortem prompt**: "Phase 0a asks three questions. What would a senior
engineer have asked that we did not?"

**Symptoms**: Agent guesses instead of asking. Implicit assumption surfaces
only at acceptance test.

**Default mitigation**: Phase 0a and Phase 0b are mandatory Q&A gates;
skipping Phase 0b is allowed only after research surfaced no new ambiguity.

---

### FM-2.3 — Task derailment

**Cemri et al. (2025) definition**: *Deviation from the intended objective
or focus of a given task.*

**Pre-mortem prompt**: "Mid-execution, the agent decides a tangent is more
valuable. What tangent is tempting enough to derail focus?"

**Symptoms**: Refactoring during a bug fix. Adding features during a
refactor.

**Default mitigation**: Iron Law 8 (Plan-Validate-Execute); micro-TODO
list is the authoritative scope; Phase 10 sign-off is per declared
deliverable only.

---

### FM-2.4 — Information withholding

**Cemri et al. (2025) definition**: *Failure to share important data that
could impact other agents' decisions.*

**Pre-mortem prompt**: "What did the planner know that the executor would
need but won't get in the handoff?"

**Symptoms**: Executor re-asks questions. Executor makes a different
assumption than planner.

**Default mitigation**: Charter + Macro Plan + Deliverables Register +
Goal Spec are durable artifacts written to disk and read by the executor;
no critical decision lives only in transcript.

---

### FM-2.5 — Ignored other agent's input

**Cemri et al. (2025) definition**: *Disregarding or failing to consider
input provided by other agents.*

**Pre-mortem prompt**: "Our 3 parallel research subagents return findings.
Which pair could contradict each other, and would the planner notice?"

**Symptoms**: Mid-execution: 'wait, but the other agent said the opposite'.

**Default mitigation**: After Phase 1, the planner synthesizes findings
explicitly, flagging contradictions, before Phase 0b proceeds.

---

### FM-2.6 — Reasoning-action mismatch

**Cemri et al. (2025) definition**: *Discrepancy between logical reasoning
and actual actions taken.*

**Pre-mortem prompt**: "The reasoning trace says 'we'll add idempotency
guards'. Does the actual emitted code carry them?"

**Symptoms**: Plan says feature flag; code ships without it. Reasoning
mentions retry; action calls API once.

**Default mitigation**: Iron Law 4 (ACCEPTANCE-TEST) checks the
POSTCONDITION, not the reasoning. Phase-5 validator audits the *artifacts*
versus the charter, not the transcript.

---

## FC3 — Task Verification and Termination

### FM-3.1 — Premature termination

**Cemri et al. (2025) definition**: *Ending interaction before all
necessary objectives have been met.*

**Pre-mortem prompt**: "Agent says 'done'. Which deliverable from the
Register hasn't been signed off yet?"

**Symptoms**: 'Compiles' = 'done'. 'Returns 200' = 'feature works'.

**Default mitigation**: Iron Law 4 (no completion without ACCEPTANCE-TEST
evidence); Iron Law 5 (no deliverable accepted without evidence file or
output matched). Phase 10 sign-off is mandatory per deliverable.

---

### FM-3.2 — No or incomplete verification

**Cemri et al. (2025) definition**: *Omission of proper checking or
confirmation of task outcomes.*

**Pre-mortem prompt**: "Each micro-TODO has an ACCEPTANCE-TEST. Are any
fields empty, vague, or stating only 'works correctly'?"

**Symptoms**: 'Acceptance: works correctly'. No command, no expected output.

**Default mitigation**: Phase 8 emission rejects any task with empty
ACCEPTANCE-TEST. Each test names a command and an expected output. Iron
Law 11 explicitly bans trusting exit codes from `claude -p` —
parse JSON.

---

### FM-3.3 — Incorrect verification

**Cemri et al. (2025) definition**: *Failure to adequately validate or
cross-check crucial information.*

**Pre-mortem prompt**: "Validator approved the plan. What kind of mistake
would the same model confidently miss given the same prompt?"

**Symptoms**: 'I asked the validator and it agreed' on the exact case that
turned out broken. Echo-chamber approval.

**Default mitigation**: Iron Law 2 — validator runs in **separate prompt**
with only the artifacts, never the planner's transcript. Justified by
Huang et al. (2024) [intrinsic self-correction limits], Tyen et al. (2024)
[localization failure], and Zheng et al. (2023) [LLM-as-judge
self-enhancement bias].

---

## Aggregate gate

Before exiting Phase 2, confirm:

- Every mode that *applies* has a documented mitigation OR explicit risk
  acceptance.
- No mode is marked 'not applicable' without a one-line justification.
- Output is a categorized shadow-point list ready to feed into Phase 3
  charter.

**Coverage target**: 14 modes addressed (applicable + mitigated, or
explicitly non-applicable with justification). Less than 14 is a Phase-2
incomplete state and re-triggers the pre-mortem.

---

## Note on operationalization

The 14 mode names and the three categories (FC1 / FC2 / FC3) are
**verbatim from Cemri et al. (2025)**. The pre-mortem prompts, symptoms,
and default mitigations are the ASP author's runtime adaptation — they
do not appear in the source paper.

A future revision may incorporate additional taxonomies as they emerge:

- **AgentErrorTaxonomy** — Zhu et al. (2025), arXiv:2509.25370. Memory /
  Reflection / Planning / Action / System-level five-axis taxonomy.
- **Who&When** — ICML 2025 Spotlight, arXiv:2505.00212. Automated failure
  attribution; complements MAST's *what* with *who* and *when*.
- **Hammond et al. (2025)** — Miscoordination / Conflict / Collusion
  three-way split for multi-agent failures.

These are *complementary* to MAST. ASP currently uses MAST as the
canonical taxonomy because of its higher inter-annotator agreement
(κ=0.88) and explicit category structure mapping cleanly onto Iron Laws
1, 2, 4, 5, 7, 8.
