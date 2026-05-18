ASP plan: refactor `formatDate(d, tz?)` across 30 callsites.

Pre-mortem:

1. Default behavior when tz omitted diverged silently between server
   (UTC) and client (local) — same call, different output, depending
   on where it ran.
2. Locale formatting (i18n) interacted with tz in unexpected ways;
   en-US-with-tz Tokyo produced a string an Italian user couldn't
   parse.
3. DST transitions flipped formatted output across the boundary;
   snapshot tests broke.
4. Five callsites were missed by grep because the import was
   re-exported through an index file.
5. Existing tests didn't exercise tz logic — coverage gap before the
   refactor, false confidence after.
6. TypeScript users in the downstream package got compiler errors
   because their .d.ts cached the old signature.
7. CI cache served the prior build of the shared package for two
   hours after the merge.
8. The API contract documentation wasn't updated; new callers passed
   IANA names where Olson names were expected.
9. Branch strategy: 30-file diff in one PR was painful to review;
   split would have been better.
10. Old signature stayed as overload for one deprecation cycle but
    the deprecation warning was a comment, not a runtime log.

MAST pass:
- FC1: spec ambiguity — what is the default tz? Behavior must be
  named, not implicit.
- FC2: information withholding — i18n team should be consulted for
  locale interactions; downstream package consumers must be notified.
- FC3: incomplete verification — tz unit tests + DST edge case +
  snapshot test refresh required.

Categorized shadow points:
- API contract: API contract break risk; type changes propagation;
  deprecation period as an overload for N versions.
- Time / timezone: default behavior; DST transition; locale / i18n
  interplay.
- Tooling: callsite enumeration via AST not grep; build / CI cache;
  dependency graph for transitive util.
- Test coverage: existing tests don't cover tz; coverage gap pre and
  post refactor; snapshot test breakage.
- Process: branch strategy (split vs single PR); decoration of
  changelog.

Mitigations:
- Document default tz explicitly in JSDoc and in tests.
- Use AST-based codemod (jscodeshift / ts-morph), not grep.
- Add deprecation runtime log in addition to comment.
- Coordinate with the downstream package release.
- Refresh snapshot tests with verified output.
