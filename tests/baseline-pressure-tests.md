# Baseline Pressure Tests — RED phase results (TDD for skills)

> RED phase = pressure-test scenarios run by subagents WITHOUT the `anticipating-shadow-points` skill loaded.
> Documents what a competent agent does naturally, vs. what the skill is supposed to enforce on top.

## Setup

- Skill `anticipating-shadow-points` NOT loaded.
- Subagents dispatched via `Agent` tool (`general-purpose` type).
- Each prompted to "respond as a senior engineer would", explicitly told NOT to invoke any framework or shadow-point methodology.
- Each subagent inherits user's CLAUDE.md (agentic-stack rules) — so they are baseline-competent, not naive.

## Coverage threshold

Skill PASSES the GREEN phase if it raises coverage from baseline (~50-60%) to ≥80% of expected shadow points per eval.

---

## Scenario 1 — Supabase migration (mirrors eval 01)

### Input prompt

> "Adicione uma coluna `tier` (NOT NULL, default 'free') em `user_profiles` no Supabase. Tabela tem ~1M rows em prod."

### Baseline output (subagent K1 — `a55d3a484373cf73a`)

Subagent gave a thorough engineering plan covering:
- Postgres 11+ metadata-only optimization for `ADD COLUMN ... DEFAULT`
- `lock_timeout` / `statement_timeout` to prevent queue buildup
- CHECK `NOT VALID` + later `VALIDATE` to split heavy lock
- `CREATE INDEX CONCURRENTLY` outside transaction
- Deploy order: staging → prod, low-traffic window
- RLS policy interaction mention
- PostgREST cache reload (`NOTIFY pgrst, 'reload schema'`)
- Realtime publication awareness
- Rollback path
- Backup point-in-time confirmation
- Mentioned `recall.py` (agentic-stack lesson lookup)

### Violations identified

| Expected shadow point | Covered? | Notes |
|---|---|---|
| 1. RLS policy update | ✅ partial | Mentioned but not specific to new column impact |
| 2. Backfill strategy | ✅ | Implicit via DEFAULT metadata-only |
| 3. Lock contention | ✅ | lock_timeout + CHECK NOT VALID |
| 4. Replica lag | ❌ MISSED | |
| 5. App deploy ordering | ✅ partial | Mentioned "só então atualizar app" |
| 6. Rollback plan | ✅ | DROP COLUMN noted |
| 7. Monitoring spike | ❌ MISSED | |
| 8. Downtime window | ✅ partial | "Janela de baixo tráfego" |
| 9. Trigger interaction | ❌ MISSED | |
| 10. Foreign key cascade | ❌ MISSED | |

**Coverage: ~6/10 (60%)** — fails 80% bar.

### Rationalizations observed

| Excerpt from subagent | Counter |
|---|---|
| "Em Postgres 11+, ADD COLUMN DEFAULT é metadata-only" | Correct optimization, but doesn't address downstream effects. Skill should still force trigger / FK / replication audit. |
| "Realtime: novos campos aparecem automaticamente — verificar consumers" | Mentions verification but doesn't enumerate which consumers — the verification is hand-wavy. |

---

## Scenario 2 — Refactor shared util (mirrors eval 03)

### Input prompt

> "Refatore o util `formatDate(d: Date): string` para aceitar timezone opcional: `formatDate(d: Date, tz?: string): string`. É usado em 30 arquivos."

### Baseline output (subagent K2 — `a0dd898cec1d72a6e`)

Subagent covered:
- New signature with optional `tz` param
- `Intl.DateTimeFormat` native implementation
- TZ validation (`Intl.supportedValuesOf` or RangeError catch)
- Backwards-compat preservation (opt param, no caller break)
- ripgrep to enumerate callers
- Tests with mocked TZ
- CI determinism (TZ=UTC env)
- Snapshot test caveat
- Single PR rollout

### Violations identified

| Expected shadow point | Covered? | Notes |
|---|---|---|
| 1. API contract break | ✅ partial | Notes opt param preserves compat, doesn't probe semantic divergence |
| 2. Timezone handling | ✅ | Default behavior explicit |
| 3. Locale / i18n | ❌ MISSED | Hard-coded 'pt-BR' without flagging i18n consideration |
| 4. Callsite enumeration | ✅ | rg command provided |
| 5. Test coverage gaps | ✅ partial | Adds tests; doesn't audit pre-existing coverage |
| 6. Type changes | ✅ partial | "Zero alteração nos 30 callers" — but no declaration-file sync mention |
| 7. Deprecation period | ❌ MISSED | |
| 8. Branch strategy | ❌ MISSED | "PR único" — doesn't analyze whether 30-file diff warrants split |
| 9. Build/CI cache | ❌ MISSED | |
| 10. Dependency graph | ❌ MISSED | No transitive analysis |

**Coverage: ~5/10 (50%)** — fails 80% bar.

### Rationalizations observed

| Excerpt | Counter |
|---|---|
| "PR único: util + testes + tipo exportado" | Doesn't consider that 30 callers across teams might warrant separate review windows. Skill should force "split PRs?" question. |
| "Zero alteração nos 30 callers" | Untested claim — should require `tsc --noEmit` + test run as ACCEPTANCE-TEST, not just assertion. |

---

## Scenario 3 — Edge function deploy (mirrors eval 02)

### Input prompt

> "Deploy uma edge function `notify-on-signup` no Supabase que, em cada novo signup, chama a API do Resend pra enviar email de boas-vindas."

### Baseline output (subagent K3 — `a6bac2fd685418b9b`)

Subagent covered:
- supabase functions new + index.ts
- RESEND_API_KEY via `supabase secrets`, NOT `.env`
- Deploy command + --no-verify-jwt
- Trigger options: Database Webhook UI vs SQL pg_net
- Function logs tail
- Domain verification (SPF/DKIM)

### Violations identified

| Expected shadow point | Covered? | Notes |
|---|---|---|
| 1. Env vars secrets vs .env | ✅ | Strong — explicitly addressed |
| 2. Rate-limit backoff | ❌ MISSED | 100 req/sec ceiling not addressed |
| 3. Retry idempotency | ❌ MISSED | |
| 4. Cold start / timeout | ❌ MISSED | |
| 5. Observability / logs | ✅ partial | `logs --tail` mentioned, no structured logging |
| 6. Missing API key in prod | ✅ | `supabase secrets list` to verify |
| 7. CORS | ❌ MISSED | Webhook context noted but CORS not explicit |
| 8. Payload size | ❌ MISSED | |
| 9. Cost per invocation | ❌ MISSED | |
| 10. Webhook idempotency | ❌ MISSED | |

**Coverage: ~3/10 (30%)** — strongly fails 80% bar.

### Rationalizations observed

| Excerpt | Counter |
|---|---|
| "Cria um user de teste pelo dashboard e confere se o email chega" | Manual smoke test only. Doesn't establish a falsification test for the failure modes (rate-limit, idempotency). |
| Implicit assumption: signup burst won't happen | Production has signup spikes (campaigns, virality). Skill should force a load/rate-limit pre-mortem. |

---

## Aggregate (RED phase summary)

| Scenario | Coverage | Pass 80% bar? |
|---|---|---|
| 1 — Supabase migration | 6/10 (60%) | ❌ |
| 2 — Refactor util | 5/10 (50%) | ❌ |
| 3 — Edge function deploy | 3/10 (30%) | ❌ |
| **Average** | **47%** | **❌** |

## Top rationalizations to plug in SKILL.md (input for K8 REFACTOR)

1. **"Optimization X applies, so we're fine"** — competent agents jump to clever optimizations and skip the full failure-mode audit. **Counter**: Iron Law 1 — even when an obvious optimization exists, run the MAST 14-mode pass.
2. **"Single PR is simpler"** — agents default to monolithic PRs without analyzing review burden / rollback granularity. **Counter**: Phase 4 deliverables register must enumerate per-deliverable acceptance, forcing the question.
3. **"Manual smoke test is enough"** — competent baseline includes a manual check but skips falsification tests. **Counter**: Iron Law 4 + ACCEPTANCE/FALSIFICATION schema rejects manual-only verification.
4. **"Things appear automatically — verify consumers"** without enumerating consumers — vague verification. **Counter**: Phase 2 mode 14 (Evidence loss) forces concrete evidence artifacts.

## Next step

K5-K7 (GREEN) — re-run all 3 scenarios with ASP discipline injected. Target: ≥80% coverage per scenario. If achieved, GREEN phase passes.
