# Execution Report — {{projeto}}

> ASP Phase 11 output. The closure artifact for the project. Written before `memory_reflect.py` + `learn.py` calls.

## Entregue

| ID | Deliverable | Evidence path |
|---|---|---|
| D01 | <name> | <path> |

## Pendente (com razão)

| ID | Deliverable | Razão | Próximo passo |
|---|---|---|---|

## Bloqueado (com ação requerida)

| ID | Deliverable | Bloqueador | Ação requerida | Owner |
|---|---|---|---|---|

## Métricas

| Métrica | Valor |
|---|---|
| Turns LLM consumidos | |
| Elapsed time | |
| USD (se tracking ativo) | |
| Shadow points identificados (Phase 2) | |
| Shadow points que se concretizaram durante execução | |
| Shadow points mitigados com sucesso | |
| Validator rounds | |
| Advisor calls | |
| FALSIFICATION fires | |
| Re-entries em ASP | |

## Lições (3-5 bullets)

1.
2.
3.

## Memory write-back commands (rodar logo após este report)

```bash
# Episodic + semantic entries:
python3 ~/.agent/tools/memory_reflect.py \
    "<categoria>" \
    "<ação realizada>" \
    "<resultado conciso>" \
    --importance <5-10> \
    --note "<lição não-óbvia que precisa sobreviver à sessão atual>"

# Durable rule (only if Phase 2 surfaced a rule worth keeping):
python3 ~/.agent/tools/learn.py \
    "<regra phrased as principle>" \
    --rationale "<incidente específico que ensinou>"
```

## Project close confirmation

- [ ] All Iron Laws respected (audit by advisor() final call)
- [ ] Execution Report archived in repo / project dir
- [ ] Memory write-back commands executed
- [ ] Deliverables Register fully `aceito` (or remaining items moved to backlog with owners)
- [ ] If Phase 12 opt-in: public release artifact list confirmed inspected by user
