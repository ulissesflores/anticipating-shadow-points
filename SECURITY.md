# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.2.x | ✅ |
| 0.1.x | ⚠️ best-effort; please upgrade to 0.2.x |
| < 0.1 | ❌ |

## Reporting a vulnerability

**Do NOT open a public GitHub issue for security concerns.** Use private channels:

1. **Preferred**: GitHub Security Advisory — [Open a private advisory](https://github.com/ulissesflores/anticipating-shadow-points/security/advisories/new)
2. **Email**: c.ulisses@gmail.com with subject prefix `[asp-security]`
3. **Backup**: contact form at https://ulissesflores.com

Please include:
- A description of the issue and its potential impact.
- Steps to reproduce, including the install path (plugin marketplace / `--plugin-dir` / `install.sh`) and Claude Code version.
- Whether the issue is publicly known or under embargo.
- Suggested mitigation, if you have one.

## Response timeline

- **Acknowledgement**: within 72 hours.
- **Initial assessment**: within 7 days.
- **Patch + disclosure plan**: jointly agreed with the reporter; coordinated disclosure is preferred.

## Threat model (in scope)

ASP is a Claude Code skill. Realistic threat surfaces:

1. **`claude -p` subprocess spawn** (`skill/claude-p-goal-runner.md`). The runner uses `--permission-mode bypassPermissions` and processes user-supplied Goal Specs. A maliciously crafted Goal Spec could cause the child Claude session to execute unintended actions (file write, network, code execution). Mitigations are listed in Iron Laws 9 and 10 (file-based contract, `ASP_IN_GOAL` reentrancy guard).
2. **`recall.py` integration** (Phase 1). If a malicious `~/.agent/` is present, recall output is included in the planning context. Treat the agentic-stack as a trust boundary.
3. **Markdown template injection**. Templates use `{{placeholder}}` patterns rendered into text. They are not executed; no SSTI risk in normal usage.
4. **Install scripts** (`scripts/install.sh`, `uninstall.sh`). These run with the user's permissions and write to `~/.claude/`. Review the source before running in untrusted environments.
5. **Plugin manifest** (`.claude-plugin/plugin.json`). Static metadata; no execution surface.

## Out of scope

- Vulnerabilities in Claude Code itself, the `/goal` slash command, or Anthropic infrastructure → report to Anthropic.
- Issues in third-party plugins listed alongside ASP in marketplaces → report to those plugin maintainers.
- Social engineering against the maintainer (this is a personal repo, not an organization).

## Recognition

If you report a valid vulnerability, you will (with your permission) be credited in the security advisory, the release notes that ship the fix, and the `AUTHORS` file.
