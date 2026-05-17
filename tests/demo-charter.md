# Project Charter — ASP / Anticipating Shadow Points (demo rendering)

> ASP Phase 3 output, rendered from `skill/templates/project-charter.md` with this very ASP project's data. Serves both as a Phase-3 demo and as the project's own charter.

## Projeto

ASP (`anticipating-shadow-points`) — a global Claude Code skill for pre-mortem-driven, validator-checked, contract-backed planning of non-trivial engineering tasks.

## Problema

LLM-driven coding agents (Claude Code, Cursor, etc.) routinely ship work that has hidden failure modes the agent didn't think about — RLS not updated, env vars in `.env` instead of secrets, callsites missed in refactors, cron jobs re-triggering known incidents. These "shadow points" surface 24-72 hours later as bugs, incidents, or rejected PRs. Existing skills suggest discipline but don't enforce it; agents under pressure rationalize past unstructured guidance.

## Outcome desejado (mensurável)

A skill that, when invoked on a task with at least 8 expected shadow points, produces output covering ≥80% of them in baseline evaluations, vs. ~47% average for the same agent without the skill. Verified empirically via 5 structured evals (`skill/evals/`).

## In-scope

- Skill files (`SKILL.md` + methodology + MAST checklist + Q&A frames + 7 templates + 5 evals).
- Slash commands `/asp` and `/ASP`.
- Staging directory `~/Developer/ASP/` with full repo structure.
- Install/uninstall/verify scripts (idempotent).
- Multilingual READMEs (EN/ES/PT/IT/HE).
- TDD baseline (RED-GREEN-REFACTOR with subagent evidence).
- CI workflow skeleton.

## Out-of-scope

- Public GitHub release (deferred to Phase 12 opt-in after user inspection).
- PreToolUse hook for automatic contract enforcement (deferred to Phase-2).
- Native `/goal` invocation from within skill context (impossible per pre-flight probe; documented in `tests/goal-invocability-probe.md`).
- Native review of machine-translated docs (community contribution invited).
- PR submission to `anthropics/skills` marketplace.

## Stakeholders

| Quem | O que aceita |
|---|---|
| Ulisses Flores (primary user) | All deliverables D01-D13 |
| Community (post-release) | Repo via PRs and issues — only after Phase 12 explicit go-ahead |

## Critério global de sucesso

`scripts/verify.sh` exits 0 with all 16 criteria PASS, `advisor()` final call returns positive ship verdict, `tests/evals-summary.md` shows ≥4/5 evals at ≥80% coverage, and the user inspects + explicitly approves before any public push.

## Top-3 riscos

1. **`/goal` not tool-invocable from skill context** — confirmed by pre-flight probe. Mitigated by `--no-goal` fallback being the effective default; Goal Spec is emitted as user-typeable guidance.
2. **Translation quality** — ES/IT/HE are machine-translated. Mitigated by explicit disclaimer + PR invitation for native review.
3. **Skill bloat** — 30 files is substantial. Mitigated by clear separation (skill/ vs repo-only), staged install, and verify.sh ensuring nothing leaks pre-install.

## Custo estimado

| Recurso | Estimativa real (até este ponto) |
|---|---|
| Turns LLM | ~60 turns (file creation + 8 subagent dispatches + verify) |
| Elapsed time | ~2 hours of session time |
| USD | (não disponível neste session — Claude Code não expõe cost tracking aqui) |

## Aprovação

- [x] Stakeholder primário aprovou o plano v3 (`ExitPlanMode` accepted)
- [x] Validator subagent (Phase 5) aprovou implicitamente via RED/GREEN/REFACTOR (não houve REVISE)
- [x] Shadow points top-3 têm mitigação documentada
