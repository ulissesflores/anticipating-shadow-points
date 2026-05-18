---
title: "Español"
layout: default
parent: Translations
nav_order: 1
---

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

## Casos de Uso (Ejemplos)

Escenarios concretos donde ASP brilla. Cada uno proviene de los 5 evals estructurados que acompañan al skill (`skills/anticipating-shadow-points/evals/`).

### 1. Migración de schema en tabla de producción
> *"Agrega columna NOT NULL `tier` (default 'free') en `user_profiles`. Tabla tiene ~1M filas en prod."*

ASP fuerza auditoría upfront de: políticas RLS, estrategia de backfill + lock contention, replica lag durante DDL, orden de deploy app vs migration, interacción con triggers, locks en cascada vía FK, plan de rollback, spike de monitoring, ventana de downtime, recarga del schema cache de PostgREST.

### 2. Refactor de util usado en muchos archivos
> *"Refactoriza `formatDate(d: Date): string` para aceptar timezone opcional. Usado en 30 archivos."*

ASP saca a la luz: semántica del contrato API, implicaciones de locale/i18n, enumeración de callsites vía `ts-morph` (no grep), tests de límite DST, deprecation period, estrategia de branches, dependency graph transitivo.

### 3. Deploy de edge function con dependencia externa
> *"Deploy edge function `notify-on-signup` que llama a Resend (rate limit 100 req/sec)."*

ASP fuerza diseño upfront de: `RESEND_API_KEY` en `supabase secrets`, backoff vía outbox pattern, idempotency keys, cold-start timeout, observabilidad estructurada, heurísticas anti-bot, deliverability (SPF/DKIM/DMARC).

### 4. Cambio de RLS policy referenciando nueva columna
> *"Actualiza RLS de `user_profiles` para que usuarios vean solo filas con su mismo tier."*

ASP captura: ambigüedad de spec, recursión self-reference, vulnerabilidad de self-promotion, `FORCE ROW LEVEL SECURITY`, transacción atómica, helper `SECURITY DEFINER` con `search_path` fijado.

### 5. Cron que puede conflictuar con servicios deshabilitados
La integración `recall.py` de Phase 1 saca a la luz memoria de incidente previo. En el eval empírico, el validator subagent **rechazó la implementación** al descubrir que el path del script coincide con servicio previamente deshabilitado.

### 6. Decisión de arquitectura cross-team
Phase 3 (Project Charter) + Phase 4 (Deliverables Register con aceptación per-deliverable + owners) elimina el "creí que era tuyo".

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

## Autor

**Ulisses Flores** — CTO & Chief Researcher en [Codex Hash Research Laboratory](https://ulissesflores.com); MSc AI candidate, American Global Tech University. São Paulo, Brasil.

- 🌐 [ulissesflores.com](https://ulissesflores.com)
- 🐙 [@ulissesflores en GitHub](https://github.com/ulissesflores)
- ✉️ c.ulisses@gmail.com (divulgación de seguridad en [SECURITY.md](../SECURITY.md))

Áreas: Finanzas Cuantitativas & Web3, Hardware & IoT, IA & Ciencia de Datos. Idiomas del mantenedor: Portugués (nativo), Inglés/Español (fluido), Italiano (conversacional), Hebreo (lectura académica). Revisión por hablantes nativos de ES/IT/HE bienvenida vía PR.

**Co-autor**: Claude (Anthropic, Opus 4.7) — síntesis de investigación y drafting bajo dirección human-in-the-loop. Ver [AUTHORS](../AUTHORS).

## Comunidad

- [CONTRIBUTING.md](../CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) · [SECURITY.md](../SECURITY.md) · [CHANGELOG.md](../CHANGELOG.md)

## Licencia

MIT — ver [LICENSE](../LICENSE).
