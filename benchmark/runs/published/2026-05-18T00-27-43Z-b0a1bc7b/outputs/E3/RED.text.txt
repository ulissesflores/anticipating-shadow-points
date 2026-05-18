Plan: refactor formatDate to accept optional tz.

1. Update the signature: `formatDate(d: Date, tz?: string): string`.
2. Update the implementation to format with tz when provided, default
   to UTC otherwise.
3. Run the test suite; fix any callsites that break.
4. Open a PR with the diff across the 30 files.

This is an additive change (optional param), so existing callsites
should keep working. The PR may be large but the change is mechanical.

I'll also update the type declarations file so TypeScript consumers
see the new signature.
