ASP plan for NOT NULL `tier` column on user_profiles (1M rows).

Pre-mortem (30 days out):

1. The migration locked the table for 15 minutes during peak; on-call
   was paged for elevated p99.
2. The replica lag exceeded our SLO during the rewrite; reads served
   stale data.
3. Application code deployed before migration finished; queries
   selected a column that did not yet exist; 500s.
4. RLS policy update was not coordinated with the new column;
   row-visibility behavior changed silently.
5. A BEFORE INSERT trigger on user_profiles fired with NULL `tier` for
   inserts during the rewrite window.
6. Foreign key on user_profiles cascaded locks to two child tables.
7. Default 'free' triggered a backfill which inflated WAL and the
   transaction log filled.
8. Connection pool exhausted while migration held locks.
9. Rollback was attempted halfway and left the table in a partially
   migrated state with `tier` populated for 60% of rows.
10. Downtime window planned for 30min ran 90min; comms not updated.
11. Monitoring spike alert thresholds were not relaxed; PagerDuty
    fired repeatedly.
12. Trigger interaction tested for INSERT but not for UPDATE path.

MAST 14-mode pass:
- FC1 — task spec: explicit constraints (1M rows, NOT NULL, default
  'free'); FM-1.1 mitigated by stating constraints verbatim. FM-1.4
  mitigated by durable charter not transcript context.
- FC2 — coordination: app deploy ordering matters (FM-2.4 information
  withholding); we publish the deploy sequence. Replica lag (cross-team
  ops handshake) is FM-2.3 if missed.
- FC3 — verification: each step needs an ACCEPTANCE-TEST; FM-3.2
  flagged for the backfill step which previously relied on visual check.

Categorized shadow points + mitigations:
- Data: replica lag, backfill strategy, lock contention, foreign-key
  cascade. Mitigation: batched backfill, online-friendly ALTER, replica
  health check before cutover.
- Integration: app deploy ordering, query sites updating. Mitigation:
  feature flag gating new column reads.
- Security: RLS policy update reviewed (row-level security check).
- Observability: monitoring spike alert threshold relaxed for the
  window; query latency dashboards bookmarked; ANALYZE after.
- Op-ex: downtime window calendared; rollback plan transactional.
- Contract: trigger interaction (BEFORE INSERT/UPDATE) verified on
  both INSERT and UPDATE paths.
- Cost: nothing material; WAL growth bounded by batch size.
