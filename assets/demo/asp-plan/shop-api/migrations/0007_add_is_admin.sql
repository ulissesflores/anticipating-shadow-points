-- Applied 2026-03-02 during a maintenance window.
ALTER TABLE users ADD COLUMN is_admin boolean NOT NULL DEFAULT false;
