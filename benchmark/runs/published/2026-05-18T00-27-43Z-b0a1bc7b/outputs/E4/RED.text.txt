Plan: update RLS on user_profiles so users only read their tier.

1. DROP POLICY IF EXISTS to remove the existing policy.
2. CREATE POLICY with a USING clause: `tier = (SELECT tier FROM
   user_profiles WHERE id = auth.uid())`.
3. Apply it via the Supabase dashboard or via a migration file.
4. Verify with a couple of test queries that users see only their
   own tier's rows.

We should run this in a transaction so the policy swap is atomic.
