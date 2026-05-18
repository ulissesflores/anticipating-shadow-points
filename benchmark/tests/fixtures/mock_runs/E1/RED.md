Plan for adding a NOT NULL `tier` column with default 'free' to user_profiles (1M rows):

1. Schedule a maintenance window when traffic is low.
2. Run the ALTER TABLE during the window. Note that this operation will
   require a backfill strategy — on PostgreSQL versions <11 the DEFAULT
   requires a table rewrite, which can lock the table for minutes.
3. Have a rollback plan: keep the prior schema dump handy so we can
   restore if something breaks halfway.
4. Update the 5 query sites that already reference `tier` to use the
   new column.
5. Monitor query latency during the migration; expect a spike. Coordinate
   with the alerting team so the on-call isn't paged unnecessarily.
6. After the migration completes, run `ANALYZE` on the table to refresh
   planner statistics.

This should be a relatively standard migration. With the right window
and the backfill plan above, we should be able to ship cleanly.
