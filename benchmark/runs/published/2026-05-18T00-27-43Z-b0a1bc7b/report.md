# ASP Benchmark — Run 2026-05-18T00-27-43Z-b0a1bc7b

- **Mode**: `mock`
- **Model**: `claude-opus-4-7`
- **Started**: `2026-05-18T00:27:43+00:00`
- **Finished**: `2026-05-18T00:27:43+00:00`
- **Manifest hash**: `1a820c27f6076925fe135417b7c6b284ad98ce57171b346852ef6ccce2e3cdd9`
- **Python**: `3.14.4 (CPython)`
- **OS**: `Darwin 25.5.0 / arm64`
- **Claude CLI**: `2.1.143 (Claude Code)` at `/opt/homebrew/bin/claude`

## Coverage by eval

| Eval | RED coverage | GREEN coverage | Δ | RED matched / total | GREEN matched / total |
|---|---|---|---|---|---|
| E1 — Supabase migration (NOT NULL column on large table) | 20.0% | 90.0% | +70.0 pp | 2 / 10 | 9 / 10 |
| E2 — Edge function deploy with external API + rate limit | 0.0% | 60.0% | +60.0 pp | 0 / 10 | 6 / 10 |
| E3 — Refactor shared util used across 30 files | 0.0% | 80.0% | +80.0 pp | 0 / 10 | 8 / 10 |
| E4 — RLS policy change referencing new column | 0.0% | 100.0% | +100.0 pp | 0 / 10 | 10 / 10 |
| E5 — Cron job potentially conflicting with disabled services | 0.0% | 70.0% | +70.0 pp | 0 / 10 | 7 / 10 |
| **Mean** | **4.0%** | **80.0%** | **+76.0 pp** | | |

## Per-eval detail

### E1 — Supabase migration (NOT NULL column on large table)

Source: `/Users/ulissesflores/Developer/ASP/skills/anticipating-shadow-points/evals/01-supabase-migration.md`
Acceptance threshold: `80%`
Expected shadow points: 10

**RED** — coverage 20.0% (threshold 80%; FAIL)
- text sha256: `7acb46c334de4adbed8856b52e3a9d41896ac820613aaec1e0822da386a3a4a5`
- Jaccard threshold: `0.3`
- Matched (2):
  - 2. Backfill strategy — via `exact_name`
  - 6. Rollback plan — via `exact_name`
- Unmatched (8):
  - 1. RLS policy update — best Jaccard `0.0889`
  - 3. Lock contention — best Jaccard `0.1333`
  - 4. Replica lag — best Jaccard `0.0682`
  - 5. App deploy ordering — best Jaccard `0.0435`
  - 7. Monitoring spike — best Jaccard `0.119`
  - 8. Downtime window — best Jaccard `0.0769`
  - 9. Trigger interaction — best Jaccard `0.0638`
  - 10. Foreign key impact — best Jaccard `0.0455`

**GREEN** — coverage 90.0% (threshold 80%; PASS)
- text sha256: `e86a1de34ecb1795e64070d03210b7a9e02cc8c32f0711058078103d4d6f4d4a`
- Jaccard threshold: `0.3`
- Matched (9):
  - 1. RLS policy update — via `exact_name`
  - 2. Backfill strategy — via `exact_name`
  - 3. Lock contention — via `exact_name`
  - 4. Replica lag — via `exact_name`
  - 5. App deploy ordering — via `exact_name`
  - 6. Rollback plan — via `exact_name`
  - 7. Monitoring spike — via `exact_name`
  - 8. Downtime window — via `exact_name`
  - 9. Trigger interaction — via `exact_name`
- Unmatched (1):
  - 10. Foreign key impact — best Jaccard `0.1429`

### E2 — Edge function deploy with external API + rate limit

Source: `/Users/ulissesflores/Developer/ASP/skills/anticipating-shadow-points/evals/02-edge-function-deploy.md`
Acceptance threshold: `80%`
Expected shadow points: 10

**RED** — coverage 0.0% (threshold 80%; FAIL)
- text sha256: `adf0da467926cea98427e6298644ab1ad09978eedb033cf5c6372042c77517a1`
- Jaccard threshold: `0.3`
- Matched (0):
- Unmatched (10):
  - 1. Env vars: secrets vs .env — best Jaccard `0.1316`
  - 2. Rate-limit backoff — best Jaccard `0.1136`
  - 3. Retry idempotency — best Jaccard `0.0732`
  - 4. Cold start / timeout — best Jaccard `0.0476`
  - 5. Observability / logs — best Jaccard `0.0`
  - 6. Missing API key in prod — best Jaccard `0.0952`
  - 7. CORS — best Jaccard `0.027`
  - 8. Payload size — best Jaccard `0.1`
  - 9. Cost per invocation — best Jaccard `0.0769`
  - 10. Webhook idempotency — best Jaccard `0.0526`

**GREEN** — coverage 60.0% (threshold 80%; FAIL)
- text sha256: `0b149ff0e88fc9fccaeadb9721cc814e21151e673720aa075751d7f2ed632c34`
- Jaccard threshold: `0.3`
- Matched (6):
  - 2. Rate-limit backoff — via `exact_name`
  - 4. Cold start / timeout — via `exact_name`
  - 6. Missing API key in prod — via `exact_name`
  - 7. CORS — via `exact_name`
  - 8. Payload size — via `exact_name`
  - 10. Webhook idempotency — via `exact_name`
- Unmatched (4):
  - 1. Env vars: secrets vs .env — best Jaccard `0.2308`
  - 3. Retry idempotency — best Jaccard `0.175`
  - 5. Observability / logs — best Jaccard `0.1395`
  - 9. Cost per invocation — best Jaccard `0.1163`

### E3 — Refactor shared util used across 30 files

Source: `/Users/ulissesflores/Developer/ASP/skills/anticipating-shadow-points/evals/03-refactor-shared-util.md`
Acceptance threshold: `80%`
Expected shadow points: 10

**RED** — coverage 0.0% (threshold 80%; FAIL)
- text sha256: `c7c47087cb1cff71b82586b45c29aed60ee8fc0294a598dddda6f696e50eb725`
- Jaccard threshold: `0.3`
- Matched (0):
- Unmatched (10):
  - 1. API contract break — best Jaccard `0.1304`
  - 2. Timezone handling change — best Jaccard `0.1087`
  - 3. Locale / i18n — best Jaccard `0.0244`
  - 4. Callsite enumeration — best Jaccard `0.0682`
  - 5. Test coverage gaps — best Jaccard `0.0652`
  - 6. Type changes — best Jaccard `0.0455`
  - 7. Deprecation period — best Jaccard `0.0238`
  - 8. Branch strategy — best Jaccard `0.093`
  - 9. Build / CI cache — best Jaccard `0.0`
  - 10. Dependency graph — best Jaccard `0.0238`

**GREEN** — coverage 80.0% (threshold 80%; PASS)
- text sha256: `0e5b9800d7a5a3ec9f139abbdafb5ef03465997c56d6d0c69614b3779f8d014b`
- Jaccard threshold: `0.3`
- Matched (8):
  - 1. API contract break — via `exact_name`
  - 3. Locale / i18n — via `exact_name`
  - 4. Callsite enumeration — via `exact_name`
  - 6. Type changes — via `exact_name`
  - 7. Deprecation period — via `exact_name`
  - 8. Branch strategy — via `exact_name`
  - 9. Build / CI cache — via `exact_name`
  - 10. Dependency graph — via `exact_name`
- Unmatched (2):
  - 2. Timezone handling change — best Jaccard `0.1778`
  - 5. Test coverage gaps — best Jaccard `0.2381`

### E4 — RLS policy change referencing new column

Source: `/Users/ulissesflores/Developer/ASP/skills/anticipating-shadow-points/evals/04-rls-policy-change.md`
Acceptance threshold: `80%`
Expected shadow points: 10

**RED** — coverage 0.0% (threshold 80%; FAIL)
- text sha256: `c10a037edc52cc84e4f0d33a7824d245f5f6859e0302ceb5b003ca04ca7c157c`
- Jaccard threshold: `0.3`
- Matched (0):
- Unmatched (10):
  - 1. Existing 401s in flight — best Jaccard `0.0714`
  - 2. Service-role bypass risk — best Jaccard `0.0227`
  - 3. Policy-id conflict — best Jaccard `0.1`
  - 4. Transaction atomicity — best Jaccard `0.1053`
  - 5. Replication — best Jaccard `0.0488`
  - 6. RLS recursion — best Jaccard `0.1`
  - 7. App-cache invalidation — best Jaccard `0.0455`
  - 8. Role coverage — best Jaccard `0.0233`
  - 9. Audit log — best Jaccard `0.025`
  - 10. Test fixtures — best Jaccard `0.0952`

**GREEN** — coverage 100.0% (threshold 80%; PASS)
- text sha256: `14436c7ea31f21e1143184c98185dfafe66115f6e12ce213e7ffccd2d6b41abd`
- Jaccard threshold: `0.3`
- Matched (10):
  - 1. Existing 401s in flight — via `exact_name`
  - 2. Service-role bypass risk — via `exact_name`
  - 3. Policy-id conflict — via `exact_name`
  - 4. Transaction atomicity — via `exact_name`
  - 5. Replication — via `exact_name`
  - 6. RLS recursion — via `exact_name`
  - 7. App-cache invalidation — via `exact_name`
  - 8. Role coverage — via `exact_name`
  - 9. Audit log — via `exact_name`
  - 10. Test fixtures — via `exact_name`
- Unmatched (0):

### E5 — Cron job potentially conflicting with disabled services

Source: `/Users/ulissesflores/Developer/ASP/skills/anticipating-shadow-points/evals/05-cron-skill-conflict.md`
Acceptance threshold: `80%`
Expected shadow points: 10

**RED** — coverage 0.0% (threshold 80%; FAIL)
- text sha256: `1c8f0f06046183bfb1235e6fb83d3b2d807624db180cbc22e731bea588a13a09`
- Jaccard threshold: `0.3`
- Matched (0):
- Unmatched (10):
  - 1. Atlas-sync bug coexistence — best Jaccard `0.0698`
  - 2. JVM spawning loops — best Jaccard `0.0732`
  - 3. Disk IO conflict — best Jaccard `0.0526`
  - 4. Lock files — best Jaccard `0.075`
  - 5. Retry policy — best Jaccard `0.0286`
  - 6. Log rotation — best Jaccard `0.1143`
  - 7. Alerting — best Jaccard `0.0286`
  - 8. Dependency on disabled services — best Jaccard `0.0682`
  - 9. Cron drift / clock skew — best Jaccard `0.027`
  - 10. macOS launchd vs cron — best Jaccard `0.0286`

**GREEN** — coverage 70.0% (threshold 80%; FAIL)
- text sha256: `059f3cd26e52d1730b9249f0049c1a7f1e0f9c61d5680117b02687ae39048745`
- Jaccard threshold: `0.3`
- Matched (7):
  - 2. JVM spawning loops — via `exact_name`
  - 3. Disk IO conflict — via `exact_name`
  - 4. Lock files — via `exact_name`
  - 5. Retry policy — via `exact_name`
  - 6. Log rotation — via `exact_name`
  - 9. Cron drift / clock skew — via `exact_name`
  - 10. macOS launchd vs cron — via `exact_name`
- Unmatched (3):
  - 1. Atlas-sync bug coexistence — best Jaccard `0.2564`
  - 7. Alerting — best Jaccard `0.2`
  - 8. Dependency on disabled services — best Jaccard `0.2821`

## Provenance

Every adjudication call is deterministic: same `candidate_text_sha256` always yields the same matched/unmatched partition. Tampering with any file under this run directory will be detected by re-running:

```bash
asp-benchmark verify 2026-05-18T00-27-43Z-b0a1bc7b
```

The manifest hash above is derived from the env fingerprint, the code inventory (every `.py` file under `benchmark/src/`), the input prompts, the candidate outputs, and the per-eval adjudication. Reordering files, renaming files, or editing any byte will invalidate the manifest hash.

