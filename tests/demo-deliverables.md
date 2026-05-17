# Deliverables Register — ASP project (demo rendering)

> ASP Phase 4 output. The 13 deliverables (D01-D13) of the ASP project itself, with acceptance status snapshot at the time of this rendering.

| ID | Nome | Descrição | Owner | Aceite (critério) | Evidência exigida | Dependências | Status |
|---|---|---|---|---|---|---|---|
| D01 | Staging + git repo | `~/Developer/ASP/` with full tree, git initialized | Claude (autonomous) | Directory + .git/ exist | `find ~/Developer/ASP -type d \| wc -l` ≥ 8 | — | `entregue` |
| D02 | Skill core | SKILL.md + methodology.md + mast-checklist.md + question-frames.md | Claude | All 4 files exist, frontmatter valid, ≥6 sections each | `verify.sh` criteria 1-2, 5-6 | D01 | `entregue` |
| D03 | Templates set | 7 templates: charter, macro-plan, deliverables, micro-todo, goal-spec, contract, report | Claude | All 7 files exist with placeholders/schemas | `verify.sh` criteria 7-9, 11 | D01 | `entregue` |
| D04 | Evals set | 5 structured evals with INPUT/EXPECTED/ACCEPTANCE | Claude | All 5 files exist with 3 sections each | `verify.sh` criterion 4 | D01 | `entregue` |
| D05 | Slash commands | `asp.md` + `ASP.md` (same inode due to case-insensitive FS) | Claude | YAML frontmatter present, references skill | manual inspection + stat -i identical | D02 | `entregue` |
| D06 | Multi-lang docs + repo top | README.md (EN) + 4 translations (ES/PT/IT/HE) + LICENSE + .gitignore | Claude | 5 READMEs present, HE has dir="rtl", LICENSE is MIT | `verify.sh` criterion 15 | D01 | `entregue` |
| D07 | Scripts + CI | install.sh + uninstall.sh + verify.sh + .github/workflows/ci.yml | Claude | All bash syntax-valid, ci.yml has 4 jobs | `verify.sh` criterion 14a-b | D01 | `entregue` |
| D08 | TDD artifacts | baseline-pressure-tests.md (RED) + GREEN evidence + REFACTOR note | Claude (via subagents) | RED + GREEN + REFACTOR documented; coverage delta computed | `tests/baseline-pressure-tests.md` + `tests/evals-summary.md` | D02 | `entregue` |
| D09 | Evals execution | tests/evals-summary.md with L1-L5 results | Claude (via subagents) | 5/5 evals pass at ≥80% coverage | `tests/evals-summary.md` | D04, D08 | `entregue` |
| D10 | Install + smoke | dry-run output + real install output + smoke test result | Claude | install.sh works idempotently; smoke test confirms skill loads | `tests/smoke-test-output.md` + verify.sh exit 0 | D07 | `em-progresso` |
| D11 | Final verify + advisor | verify.sh full run + advisor() final + 16-criteria checklist | Claude | All 16 criteria PASS; advisor verdict positive | `tests/verify-output.md` + `tests/advisor-final.md` + `tests/criteria-final-checklist.md` | D10 | `planejado` |
| D12 | Memory write-back | memory_reflect.py + learn.py entries | Claude | Entries appear in `~/.agent/memory/episodic/AGENT_LEARNINGS.jsonl` | `grep "anticipating-shadow-points" ~/.agent/memory/episodic/AGENT_LEARNINGS.jsonl` ≥1 | D11 | `planejado` |
| D13 | Public release (OPT-IN) | gh repo create + tag + release | Ulisses (manual go-ahead) | Repo public on GitHub at ulissesflores/anticipating-shadow-points | `gh repo view` exit 0 | D12 + user explicit approval | `planejado` (awaiting user inspection) |

## Sign-off log (Phase 10)

### D01 — Staging + git
- Evidence: `find ~/Developer/ASP -type d | wc -l` returned 10 (≥8 required)
- Verdict: `aceito` (autonomous, observable evidence)
- Date: 2026-05-16

### D02 — Skill core
- Evidence: `verify.sh` criteria 1-2, 5-6 all OK; SKILL.md is 176 lines; methodology has 8 sections; mast-checklist has 14 modes; question-frames has Pre/Post sections.
- Verdict: `aceito`

### D03 — Templates
- Evidence: 7 templates exist; placeholders/schemas valid per criteria 7-11.
- Verdict: `aceito`

### D04 — Evals set
- Evidence: 5 eval files exist, each with 3 sections (INPUT, EXPECTED, ACCEPTANCE).
- Verdict: `aceito`

### D05 — Slash commands
- Evidence: stat shows asp.md and ASP.md share inode 53625292 (APFS case-insensitive — single file serves both invocations).
- Verdict: `aceito`

### D06 — Multi-lang docs
- Evidence: README.md + 4 docs/README.{es,pt,it,he}.md exist; HE has dir="rtl" marker; LICENSE is MIT.
- Verdict: `aceito`

### D07 — Scripts + CI
- Evidence: install.sh / uninstall.sh / verify.sh all pass `bash -n` syntax check; ci.yml has 4 jobs (yaml-lint, shellcheck, markdown-lint, verify).
- Verdict: `aceito`

### D08 — TDD artifacts
- Evidence: `tests/baseline-pressure-tests.md` populated with 3 scenarios + violations + rationalizations; REFACTOR observation added to SKILL.md.
- Verdict: `aceito`

### D09 — Evals execution
- Evidence: `tests/evals-summary.md` shows 5/5 evals at 100% coverage.
- Verdict: `aceito`

### D10 — Install + smoke
- Evidence pending: this turn's Phase N work.

### D11-D13: pending later phases.

## Aggregate status

- Total deliverables: 13
- `aceito`: 9 / 13
- `em-progresso`: 1 (D10)
- `planejado`: 3 (D11, D12, D13)
- `rejeitado`: 0
- Outstanding (excluding opt-in D13): 3
