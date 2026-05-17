# ASP — Anticipating Shadow Points

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code 2.1.139+](https://img.shields.io/badge/Claude%20Code-2.1.139%2B-blue.svg)](https://code.claude.com)
[![Status: Beta](https://img.shields.io/badge/Status-Beta-orange.svg)](#status)
[![/goal-integrated](https://img.shields.io/badge/%2Fgoal-integrated-brightgreen.svg)](#goal-integration)

> **A Claude Code skill that turns ambitious tasks into shipped deliverables — through forced upfront research, pre-mortem shadow-point detection, validator-checked plans, contractual micro-TODOs, and `/goal`-driven autonomous execution.**

🇬🇧 English (this file) · [🇪🇸 Español](docs/README.es.md) · [🇧🇷 Português](docs/README.pt.md) · [🇮🇹 Italiano](docs/README.it.md) · [🇮🇱 עברית](docs/README.he.md)

📐 **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Full state-of-the-art design doc: academic background, v1→v5 architectural journey, empirical discoveries (incl. Iron Law 11 finding), user/advisor contributions, derivation of the 12 Iron Laws.

---

## What is ASP?

**ASP** stands for **Ant-Shadow-Point** — those tiny, easily-missed failure modes that hide in the shadows of any non-trivial task and surface later as bugs, incidents, or rejected PRs.

Invoked as `/asp <your task>`, this skill orchestrates a 13-phase protocol that:

1. **Asks the right questions** (≤3 pre-research, ≤3 post-research — never about implementation).
2. **Researches in parallel** (codebase + web + prior agentic-stack lessons).
3. **Pre-mortems the failure** (Klein 1998 + Berkeley MAST 14-mode taxonomy).
4. **Validates with an independent agent** (separate-prompt subagent — no self-critique collusion).
5. **Executes via `/goal`** (Anthropic's native worker/evaluator separation, released 2026-05-12).
6. **Signs off per deliverable**, then writes lessons back to durable memory.

The protocol is opinionated. It exists because skills that "just suggest" get ignored under pressure.

---

## Why use ASP?

If you've ever shipped something and 24 hours later thought *"why didn't I think of that?"*, ASP is for you.

**ASP is appropriate for:**
- Features that touch data or shared state
- Refactors across many files
- Migrations (schema, dependency, API)
- Deploys with external dependencies
- Architecture decisions
- Debug investigations needing root-cause discipline

**ASP is overkill for:**
- Typo fixes
- Single-line edits
- Questions you can answer by reading one file

---

## Quick Start

**Three install paths** — choose the one that fits your workflow:

### Path A — Plugin marketplace (recommended, Claude Code 2.1+)

One-step install via Claude Code's native plugin manager. In any Claude Code session:

```
/plugin marketplace add ulissesflores/anticipating-shadow-points
/plugin install anticipating-shadow-points@anticipating-shadow-points
```

Then invoke: `/anticipating-shadow-points:asp <task>` (plugin-namespaced).

Benefits: native update via `/plugin update`, clean uninstall via `/plugin uninstall`, marketplace discoverability.

### Path B — Local plugin dev mode (`--plugin-dir`)

For testing/development without installing permanently:

```bash
git clone https://github.com/ulissesflores/anticipating-shadow-points.git ~/Developer/ASP
claude --plugin-dir ~/Developer/ASP
```

Loaded only for that session. Invoke: `/anticipating-shadow-points:asp <task>`.

### Path C — Standalone install.sh (legacy, full control)

For users who want bare `/asp` invocation (no plugin namespace) or want to inspect/modify before install:

```bash
git clone https://github.com/ulissesflores/anticipating-shadow-points.git ~/Developer/ASP
cd ~/Developer/ASP
./scripts/verify.sh --pre-install   # 15/16 OK (skips staging check)
./scripts/install.sh --dry-run      # preview
./scripts/install.sh                # install to ~/.claude/skills/
```

Invoke: `/asp <task>` (no namespace). Uninstall: `./scripts/uninstall.sh`.

### Requirements

- **Required**: Claude Code 2.1.139+ (for `/goal` slash command in `claude -p` mode), `bash`, `jq`.
- **Optional**: `~/.agent/` agentic-stack (enables `recall.py` lessons retrieval; skipped silently if absent).

### Invoke

In any Claude Code session:

```
/asp Add a NOT NULL column `tier` (default 'free') to user_profiles. Table has 1M rows.
```

(Use `/anticipating-shadow-points:asp` if installed via Path A or B.) The skill takes over. Follow the 13 phases.

---

## How It Works — The 13 Phases

| # | Phase | Output |
|---|---|---|
| 0a | Pre-research Q&A (≤3) | Intake |
| 1 | Parallel research (codebase + web + recall.py) | Research summary |
| 0b | Post-research Q&A (≤3, skippable) | Refined intake |
| 2 | Shadow-Point Detection (Klein + MAST 14-mode) | Categorized list + mitigations |
| 3 | Project Charter | Filled charter |
| 4 | Macro Plan + Deliverables Register | Numbered deliverables D01..Dn |
| 5 | Independent validator (separate-prompt) | APPROVE / REVISE |
| 6 | Internal loop cap=3 + optional `advisor()` | Final plan |
| 7 | User approves all three artifacts | Go/No-Go |
| 8 | Micro-TODO (`TaskCreate`) + Goal Spec | N tasks + completion condition |
| 9 | Execution via `/goal` | Tasks completed with evidence |
| 10 | Per-deliverable sign-off | All `aceito` |
| 11 | Execution Report + memory write-back | Closure |
| 12 | (Opt-in) Public release | Only on user approval |

---

## The Non-Violation Contract

ASP's signature feature: when you accept the macro plan, the skill emits one `TaskCreate` per micro-step, each with five labeled fields:

```
PRECONDITION: <invariant before>
ACTION: <exact command>
POSTCONDITION: <what changed>
ACCEPTANCE-TEST: <command + expected output>
FALSIFICATION-TEST: <test that would prove failure>
DEPENDS-ON: <upstream tasks>
DELIVERABLE-ID: <which deliverable this contributes to>
```

No task can be marked `completed` without ACCEPTANCE-TEST passing with **fresh evidence**. If FALSIFICATION-TEST fires, execution halts and re-enters ASP.

---

## `/goal` Integration (v5, empirically validated 2026-05-17)

`/goal` (Claude Code 2.1.139, released 2026-05-12) is Anthropic's native primitive for autonomous multi-turn execution. ASP v5 uses it as Phase 9's **primary execution kernel** via `claude -p` subprocess:

```bash
echo '/goal "<completion-condition>"' | claude -p \
  --permission-mode bypassPermissions \
  --output-format json \
  --max-budget-usd $BUDGET \
  --max-turns $MAX_TURNS
```

- Spawns child Claude Code session with worker+evaluator built-in.
- Parent reconciles state via JSON output (`is_error`, `terminal_reason`, `total_cost_usd`).
- File-based coordination via `~/Developer/ASP/runtime/<session-id>/`.
- **Critical**: parses JSON, never trusts `$?` (Iron Law 11). Empirical battery 2026-05-17 confirmed `claude -p` returns exit 0 even when the agent gracefully refuses — see `tests/claude-p-goal-runner-probe.md`.

**Fallback paths**:
- `--no-claude-p`: native in-session kernel (`skill/execution-kernel.md`), used also for <5 micro-step tasks.
- `--no-kernel`: vanilla `executing-plans` skill, manual step-by-step.
- User-typed `/goal`: alternative interactive autonomous mode (not skill-triggered).

---

## Depth Flags (cost control)

| Flag | Behavior | Relative cost |
|---|---|---|
| `--quick` | Skip validator + `/goal` | 1× |
| `--standard` (default) | Pre-mortem + MAST + 1 validator round + `/goal` | 3× |
| `--paranoid` | + `advisor()` + 2 validators + 3 rounds + strict evaluator | 6×+ |
| `--no-goal` | Skip `/goal` (use `executing-plans` fallback) | −1× |

---

## File Structure

```
anticipating-shadow-points/
├── skill/                  # the actual skill (installed to ~/.claude/skills/)
│   ├── SKILL.md           # main entry
│   ├── methodology.md     # Klein + MAST + Plan-Validate-Execute reference
│   ├── mast-checklist.md  # 14 failure modes with per-mode pre-mortem prompts
│   ├── question-frames.md # ≤3 Q&A frames per phase
│   ├── templates/         # charter, macro-plan, deliverables, micro-todo, goal-spec, contract, report
│   └── evals/             # 5 structured evaluations
├── command/                # slash commands (installed to ~/.claude/commands/)
├── scripts/               # install / uninstall / verify
├── tests/                 # baseline pressure tests + RED/GREEN/REFACTOR artifacts
├── docs/                  # multilingual READMEs
└── .github/workflows/     # CI: yaml-lint + shellcheck + markdown-lint + verify
```

---

## Optional integrations

- **`~/.agent/` agentic-stack**: If present, Phase 1 also runs `python3 ~/.agent/tools/recall.py "<task>"` to surface prior lessons. Skipped silently if absent.
- **`/loop` skill**: Opt-in recurring supervision for long-running Phase 9 tasks (not iteration — that's `/goal`).
- **`advisor()` tool**: Used in `--paranoid` mode and at project close for high-signal review.

---

## Status

Beta. Built and validated in `~/Developer/ASP/` staging. Public release pending user inspection.

If you find ASP useful, please open issues or PRs:
- Native review of translated READMEs (currently machine-assisted).
- Additional evals from your domain.
- Refinements to the MAST 14-mode prompts.

---

## Contributing

```bash
# Fork + clone, then:
./scripts/verify.sh --pre-install   # must pass
# make changes
./scripts/verify.sh --pre-install   # must still pass
git commit -m "feat: <change>"
gh pr create
```

CI runs yaml-lint, shellcheck, markdown-lint, and verify on every PR.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Sources / Prior art

- Klein, G. (1998, 2007). "Performing a Project Premortem". *Harvard Business Review*.
- Cemri et al. (2025). "Why Do Multi-Agent LLM Systems Fail?" — arxiv [2503.13657](https://arxiv.org/abs/2503.13657).
- Erdogan et al. (2025). "Plan-and-Act: Improving Planning of Agents". arxiv [2503.09572](https://arxiv.org/abs/2503.09572).
- Shinn et al. (2023). "Reflexion: Language Agents with Verbal Reinforcement Learning".
- Anthropic. (2026). Claude Code `/goal` command (release 2.1.139, 2026-05-12).
- Anthropic Skills best practices — [platform.claude.com docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

---

## Acknowledgements

ASP integrates patterns from [obra/superpowers](https://github.com/obra/superpowers) (the skill discipline framework) and aligns with the [agentskills.io](https://agentskills.io) open standard.
