# ASP — Anticipating Shadow Points (Anticipando Puntos de Sombra)

> **Skill para Claude Code que convierte tareas ambiciosas en entregables enviados — mediante investigación previa obligatoria, detección pre-mortem de "shadow points", planes validados por agente independiente, micro-TODOs contractuales y ejecución autónoma vía `/goal`.**

[🇬🇧 English](../README.md) · 🇪🇸 Español (este archivo) · [🇧🇷 Português](README.pt.md) · [🇮🇹 Italiano](README.it.md) · [🇮🇱 עברית](README.he.md)

📐 **[ARCHITECTURE.md](ARCHITECTURE.md)** — Doc completa del estado del arte: contexto académico, jornada v1→v5, descubrimientos empíricos (incl. Iron Law 11), contribuciones user/advisor, derivación de las 12 Iron Laws.

> Traducción asistida por IA — revisión nativa bienvenida vía PR.

---

## ¿Qué es ASP?

**ASP** viene de **Ant-Shadow-Point** — esos pequeños puntos de falla fácilmente desapercibidos que se esconden en las sombras de cualquier tarea no trivial y aparecen luego como bugs, incidentes o PRs rechazados.

Invocada con `/asp <tu tarea>`, esta skill orquesta un protocolo de 13 fases que:

1. **Hace las preguntas correctas** (≤3 pre-investigación, ≤3 post-investigación).
2. **Investiga en paralelo** (codebase + web + lecciones previas).
3. **Hace pre-mortem de la falla** (Klein 1998 + taxonomía MAST de 14 modos de Berkeley).
4. **Valida con agente independiente** (prompt separado — sin colusión de auto-crítica).
5. **Ejecuta vía `/goal`** (separación worker/evaluator nativa Anthropic, lanzada 2026-05-12).
6. **Acepta por entregable** y luego escribe lecciones a memoria duradera.

---

## ¿Por qué usar ASP?

Si alguna vez enviaste algo y 24h después pensaste *"¿por qué no pensé en eso?"*, ASP es para ti.

**ASP es apropiada para:**
- Features que tocan datos o estado compartido
- Refactors en muchos archivos
- Migraciones (schema, dependencia, API)
- Deploys con dependencias externas
- Decisiones de arquitectura
- Investigaciones de debug que exigen disciplina de root-cause

---

## Quick Start

```bash
git clone https://github.com/ulissesflores/anticipating-shadow-points.git ~/Developer/ASP
cd ~/Developer/ASP
./scripts/verify.sh --pre-install
./scripts/install.sh --dry-run
./scripts/install.sh
```

Invocar:

```
/asp Agrega columna `tier` (NOT NULL, default 'free') en user_profiles. Tabla tiene 1M filas.
```

Desinstalar:

```bash
./scripts/uninstall.sh
```

---

## Cómo Funciona — Las 13 Fases

| # | Fase | Output |
|---|---|---|
| 0a | Pre-investigación Q&A (≤3) | Intake |
| 1 | Investigación paralela | Resumen |
| 0b | Post-investigación Q&A (≤3, omisible) | Intake refinado |
| 2 | Detección Shadow Points (Klein + MAST 14) | Lista + mitigaciones |
| 3 | Project Charter | Charter completado |
| 4 | Macro Plan + Deliverables Register | Entregables D01..Dn |
| 5 | Validador independiente | APPROVE / REVISE |
| 6 | Loop interno cap=3 + advisor() opcional | Plan final |
| 7 | Usuario aprueba 3 artefactos | Go/No-Go |
| 8 | Micro-TODO contractual + Goal Spec | N tasks + completion condition |
| 9 | Ejecución vía `/goal` | Tasks completed con evidencia |
| 10 | Sign-off por entregable | Todos `aceito` |
| 11 | Execution Report + memory write-back | Cierre |
| 12 | (Opt-in) Release público | Solo tras aprobación |

---

## Contrato de No-Violación

Cada micro-paso emite un `TaskCreate` con 5 campos:

```
PRECONDITION: <invariante antes>
ACTION: <comando exacto>
POSTCONDITION: <qué cambió>
ACCEPTANCE-TEST: <comando + salida esperada>
FALSIFICATION-TEST: <test que probaría falla>
DEPENDS-ON: <tasks upstream>
DELIVERABLE-ID: <a qué entregable contribuye>
```

Ningún task se marca `completed` sin **evidencia fresca** del ACCEPTANCE-TEST.

---

## Flags de Profundidad

| Flag | Comportamiento | Costo |
|---|---|---|
| `--quick` | Omite validator + `/goal` | 1× |
| `--standard` (default) | Pre-mortem + MAST + 1 validator + `/goal` | 3× |
| `--paranoid` | + `advisor()` + 2 validators + 3 rounds | 6×+ |
| `--no-goal` | Fallback `executing-plans` | −1× |

---

## v5 (2026-05-17) — `claude -p /goal` como kernel primario

Validación empírica confirmó que `claude -p` acepta `/goal` como first piped input. ASP v5 promueve ese patrón a kernel primario de Phase 9. Native kernel (in-session) queda como fallback. **Iron Law crítica**: nunca confiar en `$?` de `claude -p` — parsear JSON (`is_error`, `terminal_reason`, `total_cost_usd`). Detalles en `tests/claude-p-goal-runner-probe.md`.

## Licencia

MIT — ver [LICENSE](../LICENSE).
