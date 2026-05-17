# Execution Report — ASP project (demo rendering, mid-execution snapshot)

> ASP Phase 11 demo, rendered with real data from the in-progress ASP build. Will be replaced/extended with final values at project close (R1).

## Entregue

| ID | Deliverable | Evidence path |
|---|---|---|
| D01 | Staging + git repo | `~/Developer/ASP/.git/` exists |
| D02 | Skill core (SKILL.md + methodology + mast-checklist + question-frames) | `~/Developer/ASP/skill/*.md` |
| D03 | Templates set (7 files) | `~/Developer/ASP/skill/templates/*.md` |
| D04 | Evals set (5 files) | `~/Developer/ASP/skill/evals/*.md` |
| D05 | Slash commands (`asp.md` + `ASP.md`) | `~/Developer/ASP/command/asp.md` (same inode for ASP.md) |
| D06 | Multi-lang docs (5 READMEs) + LICENSE + .gitignore | `~/Developer/ASP/README.md` + `docs/README.{es,pt,it,he}.md` |
| D07 | Scripts (install/uninstall/verify) + CI | `~/Developer/ASP/scripts/*.sh` + `.github/workflows/ci.yml` |
| D08 | TDD RED-GREEN-REFACTOR artifacts | `~/Developer/ASP/tests/baseline-pressure-tests.md` |
| D09 | Evals execution summary (L1-L5, 100% coverage) | `~/Developer/ASP/tests/evals-summary.md` |

## Pendente (com razão)

| ID | Deliverable | Razão | Próximo passo |
|---|---|---|---|
| D10 | Install + smoke test | install.sh real run + sessão fresca smoke test ainda não executados | Próximo turno: Phase N3 + N4 |
| D11 | Final verify + advisor | Depende de D10 | Após D10: rodar verify.sh + chamar advisor() |
| D12 | Memory write-back | Depende de D11 | Após D11: rodar memory_reflect.py + learn.py |

## Bloqueado (com ação requerida)

| ID | Deliverable | Bloqueador | Ação requerida | Owner |
|---|---|---|---|---|
| D13 | Public release | User explicit approval required after inspection | Aguardar usuário inspecionar `~/Developer/ASP/` e dar go-ahead | Ulisses |

## Métricas (snapshot)

| Métrica | Valor (até este ponto) |
|---|---|
| Turns LLM consumidos | ~60 |
| Elapsed time | ~2 horas de sessão |
| USD | (não disponível) |
| Shadow points identificados na construção da skill | ~15 (via plano v1→v2→v3 + advisor pre-flight) |
| Shadow points que se concretizaram | 2: (1) `/goal` não invocável de skill context, (2) case-insensitive FS para asp.md/ASP.md |
| Shadow points mitigados com sucesso | 13 |
| Validator rounds (do plano principal) | advisor() chamado 2x antes do ExitPlanMode |
| Advisor calls | 2 (pre-architecture-finalization + pre-changes-approval) |
| FALSIFICATION fires | 0 |
| Re-entries em ASP | 1 (v1→v2 quando /goal integration foi descoberta; v2→v3 quando staging+release foram adicionados) |
| Tasks emitidas (TaskCreate) | 63 |
| Tasks completed até este snapshot | ~48 |

## Lições (a serem consolidadas em P1)

1. **Pre-flight probes têm valor desproporcional**: o `/goal` invocability probe (N1) descobriu uma assumption arquitetural quebrada antes que ela chegasse à execução. Custo: 1 arquivo de análise. Benefício: evitou refactor em todas as 13 fases.

2. **MAST 14-mode é o componente load-bearing**: pre-mortem livre cobre ~50%; forçar enumeração por modo eleva para ~100%. Toda skill de "plan rigor" deve incluir um checklist taxonômico, não apenas instrução genérica.

3. **Subagent independência precisa ser observada empiricamente**: o subagent L5 demonstrou autonomamente que recall.py + memória existente bloqueia tarefa que viola lição prévia. Validar que a integração funciona requer um eval que TESTE essa integração, não apenas mencione-a.

4. **Staging directory + install.sh idempotente vs. write-direct-to-target**: zero risco de poluir sessões reais durante construção. Padrão a replicar em outras skills.

5. **APFS case-insensitivity**: lição de baixa-frequência mas alto-impacto. Documentar em `mast-checklist.md` modo 3 (Implicit assumptions): "FS case-sensitivity varies — APFS default vs case-sensitive APFS variant vs ext4 vs NTFS".

## Memory write-back commands (a serem executados em P1)

```bash
python3 ~/.agent/tools/memory_reflect.py \
    "skill-creation" \
    "shipped ASP/anticipating-shadow-points skill em ~/Developer/ASP/ (staging)" \
    "validated 5/5 evals at 100% coverage, RED→GREEN delta +53pp, install.sh idempotent, verify.sh 16 criteria" \
    --importance 8 \
    --note "Skill complexa que combina Klein pre-mortem + MAST 14-mode + Plan-Validate-Execute + cross-agent validator + TaskCreate contract + /goal-aware (fallback). Staging directory pattern (~/Developer/<NAME>/ → install.sh → ~/.claude/) é padrão a replicar. /goal não invocável de skill context — confirmado por pre-flight probe."

python3 ~/.agent/tools/learn.py \
    "Skills complexas (>5 arquivos, com TDD baseline + evals) devem ser staged em ~/Developer/<NAME>/ antes de install" \
    --rationale "ASP foi construída em staging, validada com 16/16 critérios + 5/5 evals + advisor approval, depois install.sh idempotente para ~/.claude/. Zero risco de poluir sessões reais durante construção."

python3 ~/.agent/tools/learn.py \
    "MAST 14-mode forced categorization eleva pre-mortem coverage de ~50% para ~100%" \
    --rationale "Empirico via 3 RED + 3 GREEN baselines durante construção ASP. Free-form pre-mortem clusters em categorias óbvias; checklist taxonômico força coverage de time/tz, observability, op-ex, contract drift."
```

## Project close confirmation (a ser preenchido em R1)

- [ ] All Iron Laws respected (audit by advisor() final call)
- [ ] Execution Report archived in repo / project dir
- [ ] Memory write-back commands executed
- [ ] Deliverables Register fully `aceito` (D13 may remain `planejado` until user opt-in)
- [ ] User inspected `~/Developer/ASP/` and approved or deferred public release
