The plan for soft-deleting users has passed independent review and stops at Phase 6. No project files were changed; the plan is saved at `claude-home/plans/standard-add-soft-delete-lucky-rose.md`.

**What I checked:** I read the backend models, data access code, user/item/login/private routes, auth dependencies, migrations, tests and the admin screens. I skipped web research because this is a well-known pattern. The project keeps no lessons file, so there were no past lessons to consult.

**Assumptions** (instead of asking you):
1. Both deletes become soft deletes: an admin deleting a user (`DELETE /users/{id}`) and a user deleting themselves (`DELETE /users/me`).
2. "Hidden" means:
   - the user can't log in;
   - tokens issued before the delete stop working;
   - password reset and recovery do nothing;
   - the user is left out of the default user list and its count.
3. Items stay unchanged. Superusers still see them; the owner can't, because they can't log in.
4. The 30 days run from a new `deleted_at` timestamp, stored in UTC with timezone, and the day count is a setting. Restore works up to and including 30 days; after that it returns 410 and the account stays soft-deleted.
5. Automatic permanent deletion after 30 days is out of scope. The template has no scheduler, and purging would delete the items you asked to keep.
6. A soft-deleted user's email stays reserved, so a restore can never collide with a new account.
7. The existing `is_active` flag keeps its meaning (an admin disabling an account) and is separate from `deleted_at`.

**Plan:**
1. **Database:** add `deleted_at`. Change the item→user link from "deleting a user deletes their items" to "block deleting a user who has items", and remove the same cascade from the model. The migration can be reversed.
2. **Login and access:** block deleted users at every point where a user is loaded, including the admin-only password-email preview route and the private create-user route.
3. **Endpoints:** both deletes switch to soft delete; the user list gets an `include_deleted` option; a new admin-only `POST /users/{id}/restore` returns 200, 404, 409 or 410.
4. **Admin screens:** regenerate the API client; update the delete dialog text; add a deleted badge with days remaining and a Restore action.
5. **Tests:** one pytest per branch, plus tests for exactly 30 days and 30 days + 1 second, tokens from before the delete, items surviving, and both directions of the migration. One browser test covers delete then restore.

| # | Shadow point | Why it bites here | Mitigation |
|---|---|---|---|
| 1 | Items get deleted along with the user | The delete route removes items explicitly, the model cascades the delete, and the database link deletes items too | Remove all three; switch the link to block the delete; a test proves a direct delete now fails |
| 2 | Tokens issued before the delete keep working | The token check only looks at `is_active` | Treat a deleted user as "User not found"; test with a token from before the delete |
| 3 | Password reset brings the account back | Reset, recovery and the admin password-email preview only look up the email | Deleted users get "Invalid token", 404, or nothing happens |
| 4 | Email collision on re-signup or restore | Email is unique; the private create route doesn't check it, so it crashes with a 500 | Keep the email reserved; the private route returns 400; test that email changes still get 409 |
| 5 | Off-by-one or timezone error in the 30-day window | New timestamp columns default to no timezone; "within 30 days" is ambiguous | Store with timezone; restore works up to and including 30 days; pass the current time into the check; test both boundaries |
| 6 | Deleted users still show in the admin list or count | The user list and its count query aren't filtered | Filter both the same way; add an `include_deleted` option |
| 7 | Restore conflicts with the existing active flag | `is_active` and `deleted_at` could be mixed up | Restore clears only `deleted_at`; keep the two separate |
| 8 | Migration can't be reversed | The original link to users was created without an explicit name | Write both directions by hand; a test reads the link rule from the database |
| 9 | Setup and test helpers misbehave | Startup won't recreate a soft-deleted first admin; the test token helper would update a deleted user | Record the startup behaviour; make the test helper raise an error |
| 10 | Admin screens and user expectations drift | The delete dialog says "permanently deleted"; the generated client is stale | Regenerate the client; rewrite the dialog text; browser test of delete then restore |

Validator: independent reviewer asked for changes (REVISE) in round 1 with 8 issues, all checked against the code and fixed; round 2 APPROVED, with two minor notes now in the plan.
Riskiest: #1. Today items are deleted along with the user in three separate places, and missing any one of them permanently loses the items the task says to keep.