**Assumptions:** the backfill source is an auth provider API that returns verified status by email or id; the PostgreSQL 15 behaviour cited here is from documentation, not tested; with only 4 files in the repo, research was done directly instead of through subagents; there is no lessons store.

Consulted lessons before acting: none (no lessons store in this repo or `CLAUDE.md`).

| # | Shadow point | Why it bites here | Mitigation |
|---|---|---|---|
| 1 | psql does not stop on SQL errors | `deploy.sh` runs `psql -f` without ON_ERROR_STOP, so exit is 0 and pods roll anyway | Add `-v ON_ERROR_STOP=1 --single-transaction`; fail CI when psql exits nonzero |
| 2 | `migrations/latest.sql` does not exist; no ledger | Only `0007_*.sql` exists, and nothing records which migrations already ran | Define how latest.sql is built; use IF NOT EXISTS DDL and a migrations version table |
| 3 | NOT NULL without default breaks old pods | Migration runs before rollout; old model inserts omit the column, so signups fail | Two-step change: add column with DEFAULT false (instant on PG15); tighten it later |
| 4 | Long lock on ~40M rows | SET NOT NULL scans the whole table under a full lock; no weekday maintenance window | Set lock_timeout; add CHECK NOT VALID, VALIDATE it, then SET NOT NULL (skips the scan) |
| 5 | Backfill as one UPDATE inside the deploy | One 40M-row UPDATE bloats the table and floods the replica the nightly report reads | Separate throttled job in 10k-id batches; watch replica lag; keep it out of deploy.sh |
| 6 | Auth provider rate limits and gaps | 40M lookups hit API quotas; deleted or mismatched users leave rows with no answer | Prefer a bulk export; resumable cursor; written rule for users the provider lacks |
| 7 | `false` hides "not backfilled yet" | During the backfill the app may treat users who already verified as unverified | Keep the app from reading the column until the backfill hits 100%; track progress |
| 8 | Drift and no rollback | Verifications that happen after the snapshot are lost; there is no down migration | Sync new verifications (webhook or dual write) before the backfill; test DROP COLUMN |

**Riskiest:** #3. Every merge to main deploys automatically, so a NOT NULL column without a default would break inserts from the old pods (new signups) in production the moment the migration runs. #1 makes it worse: the deploy would still report success.
