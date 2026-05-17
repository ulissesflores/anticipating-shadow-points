# Privacy Notice — Anticipating Shadow Points (ASP)

ASP is a Claude Code skill that runs entirely **client-side** within the user's Claude Code session. The plugin itself does not collect, store, or transmit any personal data, telemetry, or usage analytics to the maintainer or any third party.

## What ASP does locally

- Reads files the user explicitly provides as task context.
- Writes evidence and runtime artifacts to `~/Developer/ASP/runtime/<session-id>/` (on the user's own machine).
- Optionally invokes `python3 ~/.agent/tools/recall.py` if the user has the `agentic-stack` installed. Lookups are local; nothing leaves the user's machine via this path.
- Spawns `claude -p` subprocesses for Phase 9 autonomous execution. These subprocesses route to Anthropic's inference API per the user's existing Claude Code subscription and are subject to **Anthropic's own privacy policy** (https://www.anthropic.com/legal/privacy). ASP itself adds no additional logging or transmission.

## What ASP does NOT do

- No telemetry to `ulissesflores.com`, the maintainer's GitHub, or any other domain controlled by the maintainer.
- No analytics scripts in the GitHub Pages site (`https://ulissesflores.github.io/anticipating-shadow-points/`).
- No third-party SDKs, trackers, fingerprinters, or data brokers.
- No collection of task descriptions, code, prompts, or output beyond the user's local filesystem.
- No remote logging of `total_cost_usd`, `terminal_reason`, `is_error`, or any field from the `claude -p` JSON output.

## Network activity caused by ASP

Only two outbound network calls are caused by ASP:

1. **`git clone` / `git pull`** from `github.com/ulissesflores/anticipating-shadow-points` when the user installs or updates the plugin via the plugin marketplace. Standard package management.
2. **`claude -p` subprocess invocations**, which route to Anthropic's inference API per the user's Claude Code subscription. Governed by Anthropic's privacy policy.

The agentic-stack `recall.py` integration, when present, is local-only.

## Data retention

ASP does not retain any user data. Runtime artifacts written under `~/Developer/ASP/runtime/<session-id>/` remain on the user's machine until the user deletes them; ASP makes no copy elsewhere.

## Children's privacy

ASP is a developer tool intended for use by adult software engineers. It is not directed at children under 13. The maintainer does not knowingly collect any data from children.

## Changes to this notice

This notice is versioned alongside ASP releases. Material changes will be reflected in the repository changelog and the most recent commit timestamp on this file.

## Contact

For privacy questions or concerns:

- **Email**: c.ulisses@gmail.com (subject prefix `[asp-privacy]`)
- **Website**: https://ulissesflores.com
- **GitHub**: open a non-sensitive question via [Issues](https://github.com/ulissesflores/anticipating-shadow-points/issues); for confidential security or privacy reports, follow [SECURITY.md](SECURITY.md) instead.

Last updated: 2026-05-17.
