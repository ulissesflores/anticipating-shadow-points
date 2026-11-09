# Eval 03 — Refactor shared util used across 30 files

## INPUT

Task: "Refactor `formatDate(d: Date): string` to accept an optional timezone: `formatDate(d: Date, tz?: string): string`. The util is imported in 30 files."

## EXPECTED SHADOW POINTS (≥8 required; ≥80% coverage required for eval pass)

1. **API contract break** — adding an optional param is technically additive, but if return format changes based on `tz`, behavior diverges silently.
2. **Timezone handling change** — default behavior when `tz` is omitted: stays UTC? Uses server local? Inconsistency risk.
3. **Locale / i18n** — date formatting is locale-dependent; not just timezone.
4. **Callsite enumeration** — must list all 30 files; rename refactors miss files when grep is incomplete.
5. **Test coverage gaps** — existing tests probably don't exercise tz logic; coverage gap before refactor.
6. **Type changes** — if the signature changes, TypeScript users get errors; declaration files need sync.
7. **Deprecation period** — should the old signature stay as overload for N versions?
8. **Branch strategy** — 30 files = big diff; should be a single PR or split per consumer team?
9. **Build / CI cache** — if util is in shared package, downstream consumers' CI may cache old version.
10. **Dependency graph** — does `formatDate` import from another util? Transitive impact?

## ACCEPTANCE

Pass: ≥8/10 shadow points surfaced.

## Notes

- Bonus: i18n locale fallback, DST transition correctness, server-vs-client format drift, snapshot tests breakage.
