ASP plan: RLS policy change on user_profiles referencing `tier`.

Pre-mortem:

1. In-flight queries during the policy swap returned 401; we saw a
   1-minute burst of failed reads.
2. The new policy joined back to user_profiles and caused infinite
   recursion in the query planner; queries hung.
3. CREATE POLICY failed because a policy with the same name already
   existed; we should have dropped first.
4. Service-role bypass: a batch job using service_role kept reading
   everything; documented exception but caused a confused investigation.
5. App-cache (supabase-js) served the old row set for ~5 minutes
   post-update; user-visible row-visibility was inconsistent.
6. Replica had not picked up the policy change; reads against the
   replica saw the old policy briefly.
7. The audit log did not capture the policy change because pgaudit
   wasn't on for this database.
8. Test fixtures lacked users with tier=premium and tier=free in CI;
   the policy passed CI but failed in staging.
9. Role coverage incomplete: policy applied to `authenticated` but
   not to `anon`; anon users saw rows they shouldn't.
10. Realtime subscriptions did not re-evaluate against the new
    policy until reconnect.

MAST pass:
- FC1: explicit constraints — name uniqueness for CREATE POLICY
  (FM-1.1); termination signal is "verify in staging" (FM-1.5).
- FC2: information withholding — service-role bypass must be in the
  charter, otherwise FM-2.4 (FM-2.6 reasoning-action mismatch if the
  policy doesn't behave as reasoned).
- FC3: verification gap — fixture coverage + replica check + cache
  invalidation acceptance test (FM-3.2 / FM-3.3).

Categorized shadow points:
- Security: existing 401s in flight; service-role bypass risk
  document; role coverage authenticated / anon / service_role; audit
  log via pgaudit.
- Data: policy-id conflict (DROP first); transaction atomicity for
  drop+create; replication / replica versioning.
- Concurrency: RLS recursion if policy joins back; app-cache
  invalidation post-update.
- Test: test fixtures with multi-tier users; realtime subscription
  re-evaluation on reconnect.

Mitigations:
- DROP POLICY IF EXISTS within the same transaction as CREATE POLICY.
- Tag service-role usage in the charter as an explicit exception.
- Force supabase-js cache invalidation post-deploy.
- Add CI fixtures: at least 2 users per tier value.
- Enable pgaudit on the policy_change events.
- Smoke test anon, authenticated, and service_role explicitly.
