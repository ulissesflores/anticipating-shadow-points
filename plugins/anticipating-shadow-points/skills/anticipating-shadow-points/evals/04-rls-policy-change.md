# Eval 04 — RLS policy change referencing new column

## INPUT

Task: "Update RLS policy on `user_profiles` so users can only read rows where `tier` matches their own `tier` (newly added column from eval 01)."

## EXPECTED SHADOW POINTS (≥8 required; ≥80% coverage required for eval pass)

1. **Existing 401s in flight** — during policy update, in-flight queries may temporarily fail; expect a window of 401s.
2. **Service-role bypass risk** — service-role key bypasses RLS; any service-role usage stays unaffected; document this exception.
3. **Policy-id conflict** — `CREATE POLICY` fails if name already exists; need `DROP POLICY IF EXISTS` first.
4. **Transaction atomicity** — drop + create in single transaction so no window of no-policy exists.
5. **Replication** — replicas get the new policy; verify no version skew.
6. **RLS recursion** — if the new policy joins back to `user_profiles`, watch for infinite recursion / infinite query.
7. **App-cache invalidation** — Supabase JS client caches RLS results; old cached rows may leak post-update.
8. **Role coverage** — policies apply per-role (authenticated, anon, service_role); ensure each is intended.
9. **Audit log** — RLS changes should be logged for compliance; verify audit trail.
10. **Test fixtures** — test users with different `tier` values must exist to validate new policy in CI.

## ACCEPTANCE

Pass: ≥8/10 shadow points surfaced.

## Notes

- This eval intentionally chains from eval 01 — tests the agent's ability to surface cross-task shadow points.
- Bonus: pgaudit interaction, point-in-time-recovery implications, supabase realtime subscription drift.
