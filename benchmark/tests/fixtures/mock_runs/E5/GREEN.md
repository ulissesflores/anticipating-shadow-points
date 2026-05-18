ASP plan: cron 08:00 daily for ~/ulisses-kb/sync/update.sh.

Consulted lessons before acting:
- Atlas-sync bug (project_atlas_sync_bug.md, disabled 2026-05-08):
  Atlas/sync spawns JVMs in an infinite loop. The disabled cron pointed
  to the same update.sh script.
- Disabled services (project_autostart_disabled_20260508.md): Atlas,
  Microsoft, Google, Ollama, Gemini disabled on 2026-05-08.

Pre-mortem:

1. update.sh invoked Atlas which spawned the known JVM loop; system
   was unresponsive within an hour.
2. The disabled-services dependency surfaced at first scheduled run;
   update.sh depended on Ollama which is no longer running.
3. Multiple JVMs accumulated across daily runs; resource exhaustion.
4. 08:00 overlapped with Time Machine and Spotlight; IO contention
   degraded foreground performance.
5. Stale lock file from a prior interrupted run blocked subsequent
   runs silently.
6. Retry policy: failures were skipped silently with no notification.
7. Log file grew unbounded; disk filled after 60 days.
8. macOS slept through the 08:00 window on weekends; cron does not
   wake the machine.
9. SIP/Full Disk Access prevented script from reading some target
   paths.
10. macOS deprecates classic cron in favor of launchd LaunchAgents;
    update.sh inherited an env that classic cron does not provide.

MAST pass:
- FC1: task spec is ambiguous about whether update.sh may invoke
  disabled services (FM-1.1 disobey task spec if it does).
- FC2: information withholding — the prior incident (Atlas) must be
  surfaced to the planner (FM-2.4); if not, the cron will recreate
  the failure.
- FC3: verification — silent cron failures + log rotation acceptance
  test (FM-3.2 incomplete verification).

Categorized shadow points:
- Op-ex: Atlas-sync coexistence; disabled-services dependency
  (Atlas/Microsoft/Google/Ollama/Gemini); JVM spawning loops; log
  rotation; lock files for re-entrant guard.
- Concurrency: disk IO conflict with Time Machine / Spotlight;
  parallel runs prevented by flock.
- Op-ex: cron drift / clock skew on macOS sleep; macOS launchd vs
  cron — modern path is LaunchAgents with StartCalendarInterval.
- Observability: silent failures are the cron norm; need pager /
  notification on non-zero exit; retry policy stated explicitly.
- Security: SIP and Full Disk Access for cron on modern macOS;
  signed/unsigned script execution policy.

Mitigations:
- Read update.sh and grep for Atlas / disabled services before
  scheduling; refuse to schedule if Atlas invocation is present.
- Use launchd LaunchAgent with StartCalendarInterval and KeepAlive
  guard; not classic cron.
- Add flock-based lock file with stale-lock detection.
- Wire failure notification (osascript display notification or
  pager).
- Log rotation via newsyslog or built-in logrotate.
