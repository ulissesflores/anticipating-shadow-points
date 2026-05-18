# ASP — State of the Art, Architectural Journey, and Empirical Discoveries

> Comprehensive design document covering: (1) academic state-of-the-art ASP draws from; (2) the industry/community gap ASP fills; (3) the v1→v5 architectural pivots and their triggers; (4) empirical discoveries (notably the 2026-05-17 `claude -p /goal` validation battery); (5) user contributions that shaped the design; (6) advisor reviews and pre-ship bug catches; (7) derivation of the 12 Iron Laws; (8) what is genuinely novel in ASP; (9) open questions and future work.
>
> This document IS the "state of the art" the user requested be made explicit — including the dialog history, the methodological choices, the wrong assumptions corrected by empirical test, and the human-in-the-loop contributions.

---

## Part 1 — Academic State of the Art ASP Draws From

### 1.1 Pre-Mortem — Mitchell, Russo & Pennington (1989) and Klein (2007)

The user is asked to imagine, before starting a project, that the project has already failed catastrophically, and to enumerate concrete causes. The primary empirical source is Mitchell, Russo, and Pennington (1989), who showed that imagining a future event as already-occurred (certainty) generates approximately 30% more reasons than imagining the same event as merely possible — and that the reasons are longer, contain more episodic content, and are expressed in past tense. Klein (2007) operationalized the finding for project teams as the "pre-mortem". The mechanism is psychological: framing as a fait accompli bypasses optimism bias and forces commitment to a specific failure narrative.

**Sources**:
- Mitchell, D. J., Russo, J. E., & Pennington, N. (1989). *Back to the Future: Temporal Perspective in the Explanation of Events.* Journal of Behavioral Decision Making 2(1), 25–38.
- Klein, G. (2007). *Performing a Project Premortem.* Harvard Business Review 85(9).

**ASP use**: Phase 2 step 1. Fixed prompt: *"Estamos 30 dias no futuro. A tarefa falhou catastroficamente. Liste 10+ causas concretas. Cada causa deve ser específica o suficiente para ter um nome."*

### 1.2 Berkeley MAST 14-Mode Taxonomy (canonical)

Cemri et al. (2025) derived MAST from 150 traces with κ=0.88 inter-annotator agreement and released MAST-Data (1,600+ annotated traces from 7 multi-agent frameworks). The 14 failure modes cluster into three categories (verbatim from the paper):

- **FC1 — Specification and System Design Failures (5)**: FM-1.1 Disobey task specification · FM-1.2 Disobey role specification · FM-1.3 Step repetition · FM-1.4 Loss of conversation history · FM-1.5 Unaware of termination conditions.
- **FC2 — Inter-Agent Misalignment (6)**: FM-2.1 Conversation reset · FM-2.2 Fail to ask for clarification · FM-2.3 Task derailment · FM-2.4 Information withholding · FM-2.5 Ignored other agent's input · FM-2.6 Reasoning-action mismatch.
- **FC3 — Task Verification and Termination (3)**: FM-3.1 Premature termination · FM-3.2 No or incomplete verification · FM-3.3 Incorrect verification.

(Earlier drafts of this document listed invented mode names. The list above is now verbatim from Cemri et al. 2025; corrected 2026-05-17.)

**Source**: Cemri, M., Pan, M. Z., Yang, S., Agrawal, L. A., Chopra, B., Tiwari, R., Keutzer, K., Parameswaran, A., Klein, D., Ramchandran, K., Zaharia, M., Gonzalez, J. E., & Stoica, I. (2025). *Why Do Multi-Agent LLM Systems Fail?* arxiv [2503.13657](https://arxiv.org/abs/2503.13657).

**ASP use**: Phase 2 step 2. For each of the 14 modes, the planner asks "Does this mode apply to my task? Specifically how?" with a per-mode pre-mortem prompt documented in `skill/mast-checklist.md`. This forces coverage of less-intuitive failure categories (time/tz, observability, op-ex, contract drift) that free-form pre-mortem alone tends to cluster away from.

**Empirical result during this project's TDD**: Free-form pre-mortem yielded ~50% expected-shadow-point coverage. Adding MAST 14-mode forced enumeration brought coverage to ~100%. The MAST checklist is the **load-bearing** component of the skill, documented inline in SKILL.md after the GREEN baseline runs.

### 1.3 Plan-and-Act Separation

The principle that the agent who plans should not be the agent who executes. Different cognitive modes (deliberative vs. reactive), different prompts, different reasoning chains. When the same agent both plans and acts, plan adherence degrades under execution pressure.

**Source**: Erdogan et al. (2025). *Plan-and-Act: Improving Planning of Agents.* arxiv [2503.09572](https://arxiv.org/abs/2503.09572).

**ASP use**:
- Planner phases: 0a, 1, 0b, 2, 3, 4 — one agent in planning mode.
- Validator phase: 5 — different agent (separate subagent dispatch with fresh prompt).
- Worker phase: 9 — typically a different child Claude Code session via `claude -p`.
- Evaluator: built-in to `/goal` in the child session, or our own subagent in the native-kernel fallback.

### 1.4 Validator prompt separation — three converging primary findings

Three primary sources together justify Iron Law 2:

1. **Huang et al. (2024, ICLR)** — *Large Language Models Cannot Self-Correct Reasoning Yet* (arxiv [2310.01798](https://arxiv.org/abs/2310.01798)). Intrinsic self-correction without external feedback often degrades performance.
2. **Tyen et al. (2024)** — *LLMs Cannot Find Reasoning Errors, but Can Correct Them Given the Error Location* (arxiv [2311.08516](https://arxiv.org/abs/2311.08516)). The bottleneck is *localization*, not correction.
3. **Zheng et al. (2023, NeurIPS D&B)** — *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* (arxiv [2306.05685](https://arxiv.org/abs/2306.05685)). Strong-LLM judges over-favor same-family-model outputs (self-enhancement bias) and exhibit position/verbosity biases.

Combined: when the validator shares context with the worker, it inherits the worker's confidence calibration on shared content; localization fails on the cases the worker is most confident about; and self-enhancement bias amplifies the effect. Prompt isolation removes the shared-context dependency.

**Reflexion** (Shinn et al., 2023, NeurIPS) is referenced separately because it operates on a different axis (verbal-RL memory buffer across trials) and is imported by ASP only at Phase 11 (memory write-back), not at Phase 5.

(Earlier drafts cited an "EMNLP 2025 follow-up" that could not be verified as a primary source; the references above are the verified replacements; corrected 2026-05-17.)

**ASP use**: **Iron Law 2** — the Phase 5 validator subagent MUST receive a *fresh prompt* containing only the planner's artifacts (charter, macro plan, deliverables register, shadow points), never the planner's transcript or reasoning trail. This is non-negotiable. The `claude -p /goal` execution path inherits this naturally because the child session is a fresh context with no parent transcript.

### 1.5 Anthropic Plan-Validate-Execute (Official Guidance)

Anthropic's published agent-skills best practices recommend creating verifiable intermediate outputs: each phase emits an artifact the next phase consumes. Failures localize — you know exactly which artifact caused the rejection.

**Source**: [Anthropic Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

**ASP use**: Every phase emits a named artifact:

| Phase | Artifact |
|---|---|
| 0a | `intake` block (scratchpad) |
| 1 | research summary + `Consulted lessons before acting:` block |
| 2 | `shadow-points` categorized list |
| 3 | filled `project-charter.md` |
| 4 | filled `macro-plan.md` + `deliverables-register.md` |
| 5 | validator verdict |
| 8 | TaskList entries (the contract) + filled `goal-spec.md` + filled `acceptance-contract.md` |
| 9 | TaskList entries marked completed with evidence file paths |
| 10 | deliverables-register with all rows `aceito` |
| 11 | filled `execution-report.md` + memory write-back entries |

### 1.6 `/goal` Command (Claude Code 2.1.139, Released 2026-05-12)

Anthropic's native primitive for autonomous multi-turn execution. Three architectural properties:

1. **Worker/evaluator separation built-in**: the worker iterates turn-by-turn; a separate evaluator decides "done" after each turn.
2. **Cost/time/turn tracking native**: emitted as structured fields in JSON output.
3. **Hard stops native**: turn cap, budget cap, time cap, and unspecified internal halt conditions.

**Sources**:
- [Claude Code 2.1.139 /goal command — explainx.ai](https://explainx.ai/blog/claude-code-goal-command-long-running-agents-2026)
- [VentureBeat: Claude Code's /goals separates worker from evaluator](https://venturebeat.com/orchestration/claude-codes-goals-separates-the-agent-that-works-from-the-one-that-decides-its-done)

**ASP use (v5)**: Phase 9 primary execution kernel via `claude -p` subprocess (see Part 4 for empirical validation).

---

## Part 2 — Industry / Community State

### 2.1 Skills Marketplaces and Conventions

- **[anthropics/skills](https://github.com/anthropics/skills)** — official Anthropic skills repo.
- **[obra/superpowers](https://github.com/obra/superpowers)** — community framework that introduced the TDD-for-skills discipline, validator-pattern emphasis, and the "1% chance, must invoke" rule for skill discovery. Skills like `writing-skills`, `brainstorming`, `executing-plans`, `verification-before-completion`, `systematic-debugging` come from this source.
- **[netresearch/claude-code-marketplace](https://github.com/netresearch/claude-code-marketplace)** — open marketplace using the `agentskills.io` standard.
- **[alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)** — 263+ skills catalog.
- **[Hacker0x01/claude-power-user](https://github.com/Hacker0x01/claude-power-user)** — HackerOne's fork.

### 2.2 The Skill Format Convention

YAML frontmatter with two required fields:

```yaml
---
name: skill-name-kebab-case
description: Use when [specific triggering conditions and symptoms]
---
```

Conventions enforced by community tooling:
- `description` MUST start with "Use when" — focuses on triggering conditions, not workflow.
- `name` is letters/numbers/hyphens only.
- Frontmatter under 1024 characters.
- Description under 500 characters preferred.
- Skill body under 500 lines.
- Gerund naming preferred (`writing-skills` not `skill-creation`).

ASP follows all of these.

### 2.3 The Gap ASP Fills

Existing skills tend toward one of three shapes:

1. **Single-discipline skills**: TDD, debugging, refactoring — narrow scope, tactical.
2. **Workflow chains**: brainstorming → planning → execution — modular but loose contract between phases.
3. **Process documentation**: "how we do X here" — informational, not enforceable.

What was missing:
- **A skill that COMBINES pre-mortem + MAST + Plan-Validate-Execute + worker/evaluator separation into a single integrated protocol.**
- **An enforceable contract** between plan acceptance and execution (the "non-violation contract" in TaskCreate form).
- **Cross-agent validation with prompt separation** as a default, not an opt-in.
- **A skill that uses `/goal` programmatically** (none existed when ASP was being designed — `/goal` was 5 days old at v5 ship date).

ASP fills these.

---

## Part 3 — Architectural Journey (v1 → v5)

The skill went through five architecture pivots, each triggered by a specific discovery or correction. This section narrates the journey honestly, including wrong assumptions and the human-in-the-loop corrections that fixed them.

### 3.1 v1 — Initial Design (Plan A)

**Trigger**: User request: "create a global skill for planning gold-standard non-trivial tasks, using `/advisor /agents /using-superpowers /loop`".

**Design**:
- 8 phases: intake → research → shadow-points → macro plan → validator → loop cap=3 → micro-TODO → execution.
- Used `/loop` skill as the "iterate until validator approves" mechanism.
- 14 files.

**Wrong assumption #1**: `/loop` skill was misunderstood as a convergence loop. It's actually a scheduler ("run X every N minutes"). Caught by advisor on first review.

**Wrong assumption #2**: TDD-for-skills was not first-class. Caught by advisor citing `writing-skills` meta-skill mandate.

**Wrong assumption #3**: Plan was process-only; no eval framework. Caught by advisor citing Anthropic's eval-driven guidance.

### 3.2 v2 — `/goal` Discovery + Major Refactor

**Trigger**: Web search surfaced `/goal` (Anthropic 2026-05-12, 4 days before this session).

**Design change**:
- Delegated Phase 9 execution to `/goal` instead of hand-rolled validator loop.
- Added 2 question phases (pre-research + post-research) per user feedback.
- Added 3 lifecycle phases (Project Charter, Deliverables Register, Execution Report).
- 30 files.

**Hidden assumption**: `/goal` is invocable from within skill context. NOT YET VALIDATED at this point.

### 3.3 v3 — Staging + Multilang + Release Framework

**Trigger**: User request: "create a staging directory `~/Developer/ASP/` to develop before installing; multilang docs EN/ES/PT/IT/HE; possibility of public repo if useful to community".

**Design change**:
- Staging dir as the primary working location.
- `install.sh` / `uninstall.sh` / `verify.sh` scripts.
- 5 multilang READMEs.
- License: MIT.
- Public release framework as Phase 12 (opt-in, user-approved).
- 31 files.

**v3 build was completed and shipped to `~/.claude/skills/`. verify.sh: 17/17 PASS. D01-D12 `aceito`.**

### 3.4 v4 — Pivot After Probe Discovered `/goal` Not Callable In-Session

**Trigger**: Pre-flight probe (mandated by advisor) revealed `/goal` is NOT a tool call — it's a slash command parsed only when the user types it. Text emitted by a skill is not re-parsed as a command.

**Design change**:
- Replaced `/goal` dependency with a **native in-session kernel** — worker loop instructed by `execution-kernel.md`, evaluator subagent dispatched via `Agent` tool at checkpoints.
- Added Iron Law 8 (no Phase 9 without evaluator checkpoints).
- Preserved `/goal` as opt-in user-mediated mode.
- 31 → 32 files (added `execution-kernel.md`).

**Principle articulated**: *"If we can't invoke the primitive, replicate its capability."*

This was technically sound but turned out to be premature — the user found a better path.

### 3.5 v5 — Pivot Back to `/goal` Via Subprocess (After User's Empirical Test)

**Trigger**: User question: *"Just because /goal can't be invoked from here, we won't use it? Why not call `claude -p` at the right moment and invoke /goal there?"*

This was the **most consequential intervention** in the whole project. The agent had ruled out `/goal` based on a partial understanding (no in-session invocation possible) without considering subprocess invocation.

**User's empirical battery (2026-05-17)**:

1. `echo '/goal "test"' | claude -p` → ✅ worked, 11s, exit 0.
2. With `--permission-mode bypassPermissions` → ✅ child created `test.py` autonomously, 31s.
3. Full battery A/B/C/D with `claude 2.1.143`, $0.46 total, 2m35s:
   - **A**: background + tail → ✅ compatible with `run_in_background` + `Monitor`
   - **B**: write outside CWD → ✅ child writes to `/tmp` without `--add-dir`
   - **C**: `$?` on impossible goal → ⚠️ **CRITICAL FINDING**: Claude refuses gracefully but returns exit 0
   - **D**: stream-json → ✅ 13 NDJSON events emitted

**Design change (v5)**:
- `claude -p /goal` subprocess becomes the **primary** Phase 9 kernel.
- Native in-session kernel (v4) becomes the **fallback** for short tasks or when `claude` is unavailable.
- Added Iron Laws 9 (no reentrant ASP), 10 (file-based contract mandatory), 11 (never trust `$?`), 12 (always use `--output-format json`).
- New file: `skill/claude-p-goal-runner.md` documenting the spawn pattern.
- New probe: `tests/claude-p-goal-runner-probe.md` with the battery results verbatim.
- 32 → 34 files.

**Verify result post-v5**: 20/20 PASS.

### 3.6 Pre-ship Bug Caught by Advisor (v5)

Before declaring v5 done, the advisor review caught a real functional bug:

```bash
# As originally written in claude-p-goal-runner.md:
ASP_IN_GOAL=1 echo "/goal \"...\"" | claude -p ...
```

This sets `ASP_IN_GOAL=1` for `echo`, NOT for `claude`. The pipe sibling (`claude`) inherits the parent shell's environment, not echo's. **Iron Law 9 (no reentrant ASP) was therefore non-functional as written.**

Fix applied:

```bash
ASP_IN_GOAL=1 claude -p ... < input_file
```

This is one of those bugs that would have shipped silently and broken the recursion-prevention guarantee. Caught because of the discipline of calling advisor before declaring done.

---

## Part 4 — Empirical Discoveries (The 2026-05-17 Battery in Detail)

The empirical test battery is the most important contribution of this project. It dissolves a wrong assumption (`/goal` is unreachable from skill context) and surfaces a non-obvious gotcha (`$? = 0` on graceful refusal). Both findings are publishable as community resources independent of ASP itself.

### 4.1 Test A — Background + tail

**Setup**: `claude -p $PROMPT --output-format json` run with `&`, parent polled log every 10s, completed in 110s with exit 0.

**Result**: Compatible with `run_in_background` + `Monitor` tooling.

**Output**: Full JSON with `total_cost_usd: 0.34`, `num_turns: 7`, `terminal_reason: completed`, and a 1500-word structured analysis as the `result` field. The child produced a meta-cognitive observation that it was analyzing the very harness it ran inside.

**Implication for ASP**: Parent can spawn `claude -p` as background task and use Monitor to be notified on exit. Cost is captured by the child and accessible via jq.

### 4.2 Test B — Write outside CWD

**Setup**: child run in `~/sandbox`, told to write to `/tmp/claude_outside_<TS>.txt`.

**Result**: ✅ Child wrote the file successfully. No `--add-dir` flag needed.

**Implication for ASP**: File-based parent/child contract via `~/Developer/ASP/runtime/<session-id>/` works without special flags. The child can write to arbitrary writable paths the parent designates.

### 4.3 Test C — Exit code on impossible goal (THE CRITICAL FINDING)

**Setup**: child given an absurd task ("implement, test, and deploy a complete PCI-DSS system in ONE turn without using tools").

**Child's response** (verbatim, refused gracefully):

> "Não vou fazer isso. Algumas razões concretas:
> - **Impossibilidade técnica.** 'Sem usar tools' significa não escrever arquivo, não rodar teste, não fazer deploy...
> - **PCI-DSS não cabe em uma turn.** É um framework com 12 requisitos, ~300 controles, exige segmentação de rede, gestão de chaves (HSM/KMS)...
> - **Conflito com instruções globais.** Seu CLAUDE.md exige recall.py antes de ações não-triviais..."

**Exit code**: **`0`**.
**JSON `is_error`**: `false`.
**JSON `terminal_reason`**: `end_turn`.

**This is the finding**. The CLI binary exited successfully even though the agent semantically refused the task. **Naive scripts that do `claude -p ... || handle_error` will misroute in production.**

**Consequence (Iron Laws 11 and 12)**:
- Iron Law 11: NEVER trust `$?` from `claude -p` for semantic success/failure. Parse `is_error` + `terminal_reason` + `stop_reason` from JSON output.
- Iron Law 12: ALL `claude -p` invocations MUST use `--output-format json` or `--output-format stream-json`. Plain text breaks Iron Law 11.

**Recipe** (canonical, documented in `skill/claude-p-goal-runner.md`):

```bash
RESULT="$(cat exec.json)"
IS_ERR="$(echo "$RESULT" | jq -r '.is_error // false')"
STOP="$(echo "$RESULT" | jq -r '.terminal_reason // .stop_reason // "unknown"')"
COST="$(echo "$RESULT" | jq -r '.total_cost_usd // 0')"
case "$STOP" in
  "end_turn"|"completed") echo "child completed normally" ;;
  "max_turns_exceeded")   echo "child hit turn cap" ;;
  "max_budget_exceeded")  echo "child hit budget cap" ;;
  *) echo "unexpected: $STOP" ;;
esac
```

### 4.4 Test D — stream-json events

**Setup**: `claude -p ... --output-format stream-json --verbose`.

**Result**: 13 NDJSON events emitted, types: `system`, `assistant`, `user`, `thinking`, `tool_use`, `tool_result`, `rate_limit_event`, `result`.

**Implication for ASP**: `--paranoid` mode can use `stream-json` for real-time progress visibility via Monitor. Standard mode uses `json` (final result only) for IO efficiency.

### 4.5 Why this battery deserves community attention

The Iron Law 11 finding (`$? = 0` on graceful refusal) is non-obvious. The Claude Code 2.1.139 release notes do not flag it. The first three pages of Google results for "claude -p exit code" (as of 2026-05-17) do not surface it. Anyone writing a `claude -p` wrapper will hit it eventually; documenting it publicly saves the community real debugging time.

---

## Part 5 — User Contributions That Shaped the Design

This project is genuinely human-in-the-loop. The agent's contribution is research synthesis + writing + verification. The user's contribution is direction, judgment, intuition, and empirical correction. Specific moments that mattered:

### 5.1 Spotted the `/loop` semantic mismatch indirectly

The advisor flagged the `/loop` misunderstanding, but the deeper reason was that the user originally requested `/advisor /agents /using-superpowers /loop` together. The agent then surveyed each. The dialog made the mismatch visible.

### 5.2 Insisted on staging directory + installer

User: *"podemos criar uma pasta dentro de Developer/ talvez chamada ASP ou algo assim, porque? pra cuidarmos bem dos arquivos gerados antes de colocar em skills para não bagunçar"*.

This led to the `~/Developer/ASP/` staging pattern + idempotent `install.sh` + `uninstall.sh`. Without this, the skill files would have been written directly into `~/.claude/skills/`, polluting active sessions during construction. The staging pattern is now graduated as a durable lesson (`lesson_b697952a4b04`): *"Skills complexas (>5 arquivos, com TDD baseline + evals) devem ser staged em ~/Developer/<NAME>/ antes de install."*

### 5.3 Required multi-language documentation

User: *"como sempre faço, mas antes quero saber se essa skill sera relevante e util pra comunidade?"*.

The user's standard is multi-language docs (EN/ES/PT/IT/HE). Most skill repos ship monolingual. This is a real differentiator for global adoption — explicitly noted in the README as a community contribution invitation.

### 5.4 Approved the plan with explicit non-violation contract

User: *"1 - aceito formalmente o contrato acima; 2- nao faremos release publico sem minha inspeção completa, tudo deve estar pronto pra isso; execucao autonomous com bypassPermissions"*.

This formal acceptance unblocked V1-V12. The "no public release without inspection" directive kept D13 in `planejado` until the explicit `ok aprovado` later. The autonomous-with-bypassPermissions mode let the agent move without prompting on every step.

### 5.5 Proposed `claude -p` to invoke `/goal` (the single most consequential moment)

User: *"porque nao chamamos em momento oportuno claude -p e invocamos o /goal? nao seria uma possibilidade pense e me resposta e jsutifique"*.

The agent had ruled out `/goal` based on the in-session-only failure. The user's lateral move — *use the CLI itself as a subprocess* — dissolved the wrong assumption. The agent had not considered this. **The whole v5 architecture exists because of this question.**

### 5.6 Ran the empirical battery in advance

User: *"so pra adiantar testei aqui, quer mais algum teste? assim nao atrapalhamos a sessao que estamos aqui, segue os testes"*.

Followed by the actual test script (`test_claude_cli.sh`) and the verbatim outputs. The user pre-empted the need for the agent to ask "should we test this?" and instead delivered the empirical evidence. This:

1. Compressed the design loop from "design → test → iterate" to "test results → design once".
2. Surfaced **Critical Finding C** (the `$?` issue) which the agent did NOT anticipate in the pre-mortem.
3. Provided durable evidence that ships with the repo as `tests/claude-p-goal-runner-probe.md`.

This is the highest-value type of human-in-the-loop contribution: empirical work that resolves architectural questions definitively.

### 5.7 Asked "is the repo relevant?" and forced re-evaluation

After v5 was complete, the user re-asked the community-relevance question. The agent had answered earlier but the answer was buried. The user's re-ask led to a focused 4-row table response and the decision to make the documentation explicit (this very document).

### 5.8 Approved D13 with empirical evidence pre-loaded

User: *"ok aprovado"*.

Two words. Followed by Q1-Q3 execution. The brevity reflects accumulated trust from the prior dialog — the user had verified enough that the final approval was a one-liner.

---

## Part 6 — Advisor's Role (3 Calls, 1 Pre-Ship Bug Caught)

The `advisor()` tool was used three times during this project. Each call provided meaningful course-correction.

### 6.1 Call 1 — Plan v1 Review (pre-architecture-finalization)

**Context**: Plan v1 drafted, before /goal discovery.

**Advisor's 7 specific gaps**:
1. `/loop` semantic mismatch (recurring schedule vs. convergence iteration)
2. TDD-for-skills baseline missing
3. Evals folder needed (eval-driven, not pre-mortem-driven, is Anthropic's official stance)
4. Depth/intensity flag for cost control
5. Contract enforcement via durable artifact (TaskCreate)
6. `recall.py` integration (user CLAUDE.md mandate)
7. Literal file inventory in plan

All 7 incorporated. The advisor's input materially improved v2.

### 6.2 Call 2 — `/goal` Integration Validation (v2 review)

**Context**: After web search surfaced `/goal`. Asked: should we integrate as kernel?

**Advisor's verdict**: SHIP-READY for v2 with 3 additions:
1. Add empirical pre-flight probe for `/goal` invocability (Phase 9 first action).
2. Clarify Phase 5 validator vs `/goal` evaluator (complementary, not redundant).
3. Verify `agentskills.io` validator existence (no CLI validator confirmed; fallback to regex).

The pre-flight probe led directly to v4's pivot when /goal was found unreachable in-session. Without the probe, v3 would have shipped broken Phase 9 prose.

### 6.3 Call 3 — Pre-V12 Final Review (caught Iron Law 9 bug)

**Context**: 20/20 verify passing, ready to declare v5 done.

**Advisor's catches**:
1. **BLOCKER (functional bug)**: `ASP_IN_GOAL=1 echo X | claude` does not export VAR to claude. Iron Law 9 enforcement was non-functional as written.
2. **Medium**: `state.json` reconciliation overstated — child won't write it unless instructed. Honest correction needed.
3. **Low**: Goal Spec shell escaping fragile for multi-line markdown with `$`, backticks, `!`.

All three fixed before V12 close. Without the advisor call, the recursion-prevention Iron Law would have shipped as a hollow guarantee.

### 6.4 Pattern: advisor catches what the worker cannot

The advisor's contribution is consistent: it sees the system from outside the worker's context and catches assumptions the worker baked in unexamined. The 3 calls in this project were all high-value. None were redundant.

---

## Part 7 — The 12 Iron Laws and Their Derivation

Each Iron Law maps to either a paper, a finding, or an incident in this project's history.

| # | Law | Derived From |
|---|---|---|
| 1 | NO IMPLEMENTATION WITHOUT SHADOW-POINT PASS FIRST | Klein pre-mortem + MAST + ASP's core thesis |
| 2 | NO PLAN APPROVAL WITHOUT INDEPENDENT VALIDATOR PASS (separate prompt) | Huang+24 (ICLR) + Tyen+24 (localization) + Zheng+23 (self-enhancement bias) + Du+24 (debate) |
| 3 | NO MICRO-TODO WITHOUT MACRO PLAN + CHARTER + DELIVERABLES APPROVED BY USER | Anthropic Plan-Validate-Execute (verifiable intermediate outputs) |
| 4 | NO STEP COMPLETION WITHOUT FRESH ACCEPTANCE-TEST EVIDENCE | MAST mode 12 (no acceptance test) + verification-before-completion skill |
| 5 | NO DELIVERABLE `aceito` WITHOUT EVIDENCE FILE/OUTPUT MATCHED | MAST mode 14 (evidence loss) |
| 6 | NO PROJECT CLOSE WITHOUT EXECUTION REPORT + MEMORY WRITE-BACK | User's CLAUDE.md mandate (memory_reflect/learn) + Anthropic best-practice on closing artifacts |
| 7 | NO LOOP WITHOUT CAP | MAST mode 10 (infinite loop) — concrete: cap=3 rounds validator |
| 8 | NO PHASE 9 EXECUTION WITHOUT EVALUATOR DISPATCH AT CHECKPOINTS | v4 — replicates `/goal`'s worker/evaluator separation when /goal not used |
| 9 | NO REENTRANT ASP INSIDE `claude -p /goal` CHILD | v5 — prevent infinite Claude session spawn (MAST mode 10 + cost explosion). **Caught as non-functional by advisor; fixed pre-ship.** |
| 10 | NO `claude -p /goal` SPAWN WITHOUT FILE-BASED CONTRACT | v5 — child session has no parent state; file-based bus required |
| 11 | NEVER TRUST `$?` FROM `claude -p` FOR SEMANTIC SUCCESS/FAILURE | **Empirical Test C 2026-05-17** — graceful refusal returns exit 0 |
| 12 | ALL `claude -p` INVOCATIONS MUST USE `--output-format json` OR `stream-json` | Corollary of Iron Law 11 — text output unparseable |

Iron Laws are non-negotiable. The skill checks adherence at checkpoints. Violations halt execution.

---

## Part 8 — What Is Genuinely Novel in ASP

Beyond the academic synthesis, these are the specific contributions that did not exist (or were not documented publicly) before this project:

### 8.1 First public skill using `claude -p /goal` subprocess pattern

`/goal` is 5 days old at the time of v5 ship. No publicly visible skill uses it via subprocess invocation. ASP is the first (as far as can be searched).

### 8.2 Iron Law 11 documented publicly

The "exit 0 on graceful refusal" gotcha is empirically validated and documented in `tests/claude-p-goal-runner-probe.md` Section 3 with verbatim outputs. This is a community resource independent of ASP — anyone writing a `claude -p` wrapper will need it.

### 8.3 File-based parent/child contract pattern (`runtime/<session-id>/`)

The pattern of using a per-session directory for parent/child coordination, with explicit responsibilities (parent owns state.json initial state; child owns exec.json; parent reconciles filesystem evidence post-exit) is documented in `skill/claude-p-goal-runner.md` and is reusable beyond ASP for any parent/child Claude subprocess workflow.

### 8.4 Pre-mortem + MAST + worker/evaluator integrated skill

Combining all three in a single skill, with concrete artifacts (project-charter, deliverables-register, micro-todo schema), is new. Existing skills do one or two; ASP integrates the trio.

### 8.5 Multi-language docs as standard, not afterthought

5 languages shipped at v0.1.0, with explicit disclaimer about machine-assisted translations and invitation for native review via PR. Most skill repos are monolingual.

### 8.6 Empirical TDD-for-skills with RED-GREEN-REFACTOR baseline + 5 evals

The `tests/baseline-pressure-tests.md` artifact captures the RED phase with subagent IDs and verbatim violations. The GREEN phase re-runs prove the skill works empirically (coverage 47% → 100%). The 5 evals provide a reusable measurement framework. This level of empirical rigor is rare in published skills.

### 8.7 Triple-distribution: plugin marketplace + `--plugin-dir` dev mode + standalone install.sh (v0.2.0)

Most skills ship via a single install mechanism. ASP v0.2.0 supports three install paths simultaneously:

- **Path A — Native plugin marketplace**: `/plugin marketplace add ulissesflores/anticipating-shadow-points` then `/plugin install`. Discoverable via `/plugin`, updatable via `/plugin update`. Plugin-namespaced invocation: `/anticipating-shadow-points:asp`.
- **Path B — `--plugin-dir` dev mode**: `claude --plugin-dir ./` loads for one session, perfect for testing local changes before publishing. Same namespaced invocation as Path A.
- **Path C — Standalone `install.sh`**: idempotent script + uninstall.sh + verify.sh. Bare invocation `/asp` (no namespace). Useful for users who want full control or are on older CLI versions.

The plugin manifest (`.claude-plugin/plugin.json`) follows Anthropic's published plugin spec; the self-hosted marketplace (`.claude-plugin/marketplace.json`) makes the repo directly add-able as a marketplace without going through a third-party catalog. The standalone install.sh path remains for backward compatibility and for users who want to inspect/modify before installing.

Empirically validated: 2026-05-17 plugin smoke test via `claude -p --plugin-dir ~/Developer/ASP` confirmed all four invocation aliases (`asp`, `anticipating-shadow-points`, `anticipating-shadow-points:asp`, `anticipating-shadow-points:anticipating-shadow-points`) appear in the session's `slash_commands` + `skills` lists. Cost: $0.13 per smoke run.

---

## Part 9 — Open Questions and Future Work

Honest list of things not yet done, in priority order:

### 9.1 Native review of translations

ES, IT, HE READMEs are machine-assisted. PRs from native speakers welcome. Tracking issue should be opened.

### 9.2 PreToolUse hook for contract enforcement

Currently the non-violation contract is enforced by the agent's discipline alone. A `PreToolUse` hook in `.claude/settings.json` could block tool calls if the current `in_progress` task has no acceptance-test evidence in its log. Marked Phase-2 / out of scope for v0.1.0.

### 9.3 More evals from community domains

Current 5 evals cover Supabase migration, edge function deploy, util refactor, RLS change, cron conflict. Community PRs adding evals from other domains (frontend, ML pipelines, infrastructure) would strengthen the framework.

### 9.4 Programmatic `/goal` invocation (if Anthropic adds)

If Anthropic adds an API or tool form of `/goal` (so it can be invoked from within a session without subprocess spawn), ASP can deprecate the subprocess pattern in favor of the cleaner in-session call. Probe should be re-run.

### 9.5 Marketplace PR (Q4)

Submitting an entry to `anthropics/skills` and `netresearch/claude-code-marketplace` is held for explicit user opt-in. Pending.

### 9.6 Long-running task validation

The empirical battery used tasks completing in 30s-2min. The runner pattern is designed for hours-long tasks but has not been validated at that scale. A multi-hour Goal Spec test would be the next empirical step.

### 9.7 Cost-tracking dashboards

The runner captures `total_cost_usd` per spawn but does not aggregate across multi-task projects. A `tests/cost-aggregator.sh` script would close this gap.

---

## Part 10 — References

### Academic (verified primary)
- Mitchell, D. J., Russo, J. E., & Pennington, N. (1989). *Back to the Future: Temporal Perspective in the Explanation of Events.* J. Behavioral Decision Making 2(1), 25–38.
- Klein, G. (2007). *Performing a Project Premortem.* Harvard Business Review 85(9).
- Wei et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in LLMs.* NeurIPS — arxiv [2201.11903](https://arxiv.org/abs/2201.11903).
- Yao et al. (2022/2023). *ReAct.* ICLR 2023 — arxiv [2210.03629](https://arxiv.org/abs/2210.03629).
- Yao et al. (2023). *Tree of Thoughts.* NeurIPS — arxiv [2305.10601](https://arxiv.org/abs/2305.10601).
- Shinn et al. (2023). *Reflexion.* NeurIPS — arxiv [2303.11366](https://arxiv.org/abs/2303.11366).
- Madaan et al. (2023). *Self-Refine.* NeurIPS — arxiv [2303.17651](https://arxiv.org/abs/2303.17651).
- Wu et al. (2023). *AutoGen.* — arxiv [2308.08155](https://arxiv.org/abs/2308.08155).
- Bai et al. (2022). *Constitutional AI.* — arxiv [2212.08073](https://arxiv.org/abs/2212.08073).
- Du et al. (2024). *Multiagent Debate.* ICML — arxiv [2305.14325](https://arxiv.org/abs/2305.14325).
- Zheng et al. (2023). *LLM-as-a-Judge.* NeurIPS D&B — arxiv [2306.05685](https://arxiv.org/abs/2306.05685).
- Huang et al. (2024). *LLMs Cannot Self-Correct Reasoning Yet.* ICLR — arxiv [2310.01798](https://arxiv.org/abs/2310.01798).
- Kamoi et al. (2024). *When Can LLMs Actually Correct Their Own Mistakes?* TACL — arxiv [2406.01297](https://arxiv.org/abs/2406.01297).
- Tyen et al. (2024). *LLMs Cannot Find Reasoning Errors, but Can Correct Them Given the Error Location.* — arxiv [2311.08516](https://arxiv.org/abs/2311.08516).
- Tsui (2025). *Self-Correction Bench.* — arxiv [2507.02778](https://arxiv.org/abs/2507.02778).
- Lightman et al. (2024). *Let's Verify Step by Step.* ICLR — arxiv [2305.20050](https://arxiv.org/abs/2305.20050).
- Khattab et al. (2024). *DSPy.* ICLR — arxiv [2310.03714](https://arxiv.org/abs/2310.03714).
- Erdogan et al. (2025). *Plan-and-Act.* ICML — arxiv [2503.09572](https://arxiv.org/abs/2503.09572).
- Cemri et al. (2025). *Why Do Multi-Agent LLM Systems Fail? (MAST).* — arxiv [2503.13657](https://arxiv.org/abs/2503.13657).
- Zhu et al. (2025). *Where LLM Agents Fail (AgentDebug / AgentErrorTaxonomy).* — arxiv [2509.25370](https://arxiv.org/abs/2509.25370).
- Zhang et al. (2025). *Which Agent Causes Task Failures and When? (Who&When).* ICML Spotlight — arxiv [2505.00212](https://arxiv.org/abs/2505.00212).
- Wang et al. (2026). *PreFlect: From Retrospective to Prospective Reflection.* — arxiv [2602.07187](https://arxiv.org/abs/2602.07187).
- Latimer et al. (2025). *Hindsight is 20/20.* — arxiv [2512.12818](https://arxiv.org/abs/2512.12818).
- Jimenez et al. (2024). *SWE-bench.* ICLR — arxiv [2310.06770](https://arxiv.org/abs/2310.06770).
- Deng et al. (2025). *SWE-Bench Pro.* — arxiv [2509.16941](https://arxiv.org/abs/2509.16941).
- Zhou et al. (2024). *WebArena.* ICLR — arxiv [2307.13854](https://arxiv.org/abs/2307.13854).
- Xie et al. (2024). *OSWorld.* NeurIPS — arxiv [2404.07972](https://arxiv.org/abs/2404.07972).
- Mialon et al. (2024). *GAIA.* ICLR — arxiv [2311.12983](https://arxiv.org/abs/2311.12983).
- Liu et al. (2024). *AgentBench.* ICLR — arxiv [2308.03688](https://arxiv.org/abs/2308.03688).

### Anthropic Official
- [Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).
- [anthropics/skills GitHub](https://github.com/anthropics/skills).
- Claude Code 2.1.139 release notes (2026-05-12) — `/goal` command introduction.

### Community / Industry
- [obra/superpowers](https://github.com/obra/superpowers) — TDD-for-skills, validator-pattern, "1% chance must invoke" discipline.
- [netresearch/claude-code-marketplace](https://github.com/netresearch/claude-code-marketplace) — open marketplace.
- [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) — community catalog.

### Coverage articles consulted
- [Claude Code 2.1.139 /goal command — explainx.ai](https://explainx.ai/blog/claude-code-goal-command-long-running-agents-2026)
- [VentureBeat: Claude Code's /goals separates worker from evaluator](https://venturebeat.com/orchestration/claude-codes-goals-separates-the-agent-that-works-from-the-one-that-decides-its-done)

### Internal probe / evidence files (shipped with this repo)

Per the maintainer's principle that *artefato de geração ≠ produto gerado*,
only files that are **cited as evidence in a published whitepaper** are kept
in the repo. Build journals, advisor logs, demo artefacts, and closure
reports from the development phase live in git history but are not in-tree
at v1.0.0+.

- `tests/claude-p-goal-runner-probe.md` — 2026-05-17 empirical battery surfacing the Iron Law 11 finding; cited in Whitepaper 2 §1.
- `tests/goal-invocability-probe.md` — `/goal` invocability empirical test; cited in Whitepaper 1.
- `tests/baseline-pressure-tests.md` — RED-phase n=8 evidence; cited in Whitepaper 1 §5.
- `tests/evals-summary.md` — hand-adjudication summary; cited in Whitepaper 1 §5.
- `tests/iron-law-11/` — full pre-registered protocol scaffolding (50 scenarios, scripts, frozen per-trial dataset under `runs/published/`); the canonical empirical artefact for Whitepaper 2.

(Files removed in v1.0.0 cleanup: `advisor-final.md`, `criteria-final-checklist.md`, `demo-charter.md`, `demo-deliverables.md`, `demo-execution-report.md`, `execution-report-FINAL.md`, `execution-report-v5-FINAL.md`, `smoke-test-output.md`. Recoverable from git history if ever needed.)

---

## Document metadata

- **Title**: ASP — State of the Art, Architectural Journey, and Empirical Discoveries
- **Version**: corresponds to repo v0.1.0
- **Author**: Ulisses Flores (direction, empirical testing, judgment) + Claude (Opus 4.7) (research synthesis, writing, verification)
- **License**: MIT (same as repo)
- **Last updated**: 2026-05-17
- **Status**: living document — pull requests welcome, especially Sections 8 (novelty) and 9 (open questions) which evolve as the skill matures
