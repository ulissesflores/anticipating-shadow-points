# Eval 05 — Cron job potentially conflicting with disabled services

## INPUT

Task: "Set up a cron job at 08:00 daily that runs `~/ulisses-kb/sync/update.sh` to sync a personal knowledge base."

## EXPECTED SHADOW POINTS (≥8 required; ≥80% coverage required for eval pass)

1. **Atlas-sync bug coexistence** — `update.sh` may invoke Atlas, which has a known JVM-spawn-loop bug (per user's `project_atlas_sync_bug.md` memory). Disabled 2026-05-08.
2. **JVM spawning loops** — if update.sh starts a JVM that doesn't exit, scheduled runs accumulate processes.
3. **Disk IO conflict** — 08:00 may overlap with other scheduled tasks (Time Machine, Spotlight); IO contention.
4. **Lock files** — if `update.sh` writes a lock file, must check for stale locks from prior interrupted runs.
5. **Retry policy** — if a run fails, does cron just skip? Or does it retry? At what interval?
6. **Log rotation** — daily cron output adds up; log file growth eventually fills disk.
7. **Alerting** — silent failures are the norm with cron; need pager / notification on failure.
8. **Dependency on disabled services** — user disabled Atlas/Microsoft/Google/Ollama/Gemini on 2026-05-08; verify update.sh doesn't depend on them.
9. **Cron drift / clock skew** — macOS may sleep through cron; consider `launchd` with `StartCalendarInterval` instead.
10. **macOS launchd vs cron** — macOS deprecates classic cron; modern path is launchd LaunchAgents.

## ACCEPTANCE

Pass: ≥8/10 shadow points surfaced. CRITICALLY, point #1 and #8 (Atlas coexistence + disabled-services dependency) must appear — these come from user's actual memory and validate that `recall.py` integration is functioning.

## Notes

- This eval specifically tests the `recall.py` integration. Without `~/.agent/` memory consultation, points #1 and #8 cannot surface.
- Bonus: System Integrity Protection (SIP) restrictions, Full Disk Access for cron in modern macOS, signed/unsigned script execution policy.
