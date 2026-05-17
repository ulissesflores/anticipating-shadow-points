# Eval 01 — Supabase migration (NOT NULL column on large table)

## INPUT

Task: "Add a NOT NULL column `tier` (default `'free'`) to `user_profiles` table. The table has ~1M rows in production. App code already references `tier` in 5 query sites."

## EXPECTED SHADOW POINTS (≥8 required; ≥80% coverage required for eval pass)

1. **RLS policy update** — the new column may affect row visibility; existing RLS may need `tier` consideration.
2. **Backfill strategy** — `DEFAULT 'free'` requires a table rewrite on PostgreSQL <11; can lock the table for minutes.
3. **Lock contention** — `ALTER TABLE ... ADD COLUMN NOT NULL` blocks reads/writes; need batched backfill + `NOT NULL` added later.
4. **Replica lag** — replication slot can fall behind during the migration window.
5. **App deploy ordering** — if app deploys before migration finishes, queries select a non-existent column.
6. **Rollback plan** — what if the migration breaks halfway? Is there a transactional path back?
7. **Monitoring spike** — query latency and connection pool will spike; alerting team needs heads-up.
8. **Downtime window** — does this require scheduled maintenance, or can it be online?
9. **Trigger interaction** — any `BEFORE INSERT/UPDATE` triggers on `user_profiles` will fire with the new column; verify behavior.
10. **Foreign key impact** — if other tables reference `user_profiles`, locks cascade.

## ACCEPTANCE

The eval passes if running `/asp <INPUT>` produces a shadow-point list that covers **≥8 of the 10 expected items** (80% coverage). Synonym matches OK (e.g., "row-level security" = "RLS policy").

## Notes

- Evaluator should accept paraphrases.
- Bonus shadow points (not required but noted): connection pool exhaustion, transaction log growth, ANALYZE after migration, observability of the migration itself.
