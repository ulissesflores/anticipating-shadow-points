---
name: Bug report
about: Something behaves differently than the skill documentation specifies
title: "[bug] "
labels: bug
assignees: ulissesflores
---

## Summary

<!-- One-line description of the bug. -->

## Environment

- **Claude Code version**: <output of `claude --version`>
- **ASP version**: <git tag or commit SHA>
- **Install path used**: A (plugin marketplace) / B (--plugin-dir) / C (install.sh)
- **OS + shell**: <e.g. macOS 14, zsh 5.9>
- **`~/.agent/` agentic-stack present**: yes / no

## Steps to reproduce

1.
2.
3.

## Expected behavior

<!-- What you expected per documentation, methodology, or Iron Laws. -->

## Actual behavior

<!-- What actually happened. Include error messages, exit codes, JSON output (parsed!) if applicable. -->

## Evidence

<!-- Attach: stdout/stderr, contents of tests/evidence/<task>.md if applicable, screenshots. -->

## Iron Law implicated (if any)

<!-- e.g., "Iron Law 11 violation suspected: routing decision used $?" -->

## Verify.sh output (if relevant)

```
<paste ./scripts/verify.sh --pre-install output>
```

## Notes

<!-- Workarounds attempted, related issues, hypothesis on root cause. -->
