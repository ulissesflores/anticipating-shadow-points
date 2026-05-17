# Smoke Test — Post-Install Verification (N4)

> Note: A true "fresh session" smoke test requires the user to open a new Claude Code session and invoke `/asp` manually. Within this session, we can verify the installed skill state, structural integrity, and Skill-tool discoverability.

## Install state (post-N3)

```
~/.claude/skills/anticipating-shadow-points/
├── SKILL.md                  (11 KB)
├── methodology.md            (6.2 KB)
├── mast-checklist.md         (7.3 KB)
├── question-frames.md        (4.0 KB)
├── templates/                (7 files)
└── evals/                    (5 files)

~/.claude/commands/
├── asp.md                    (1.1 KB)
└── ASP.md                    (1.1 KB)

Total: 16 skill files + 2 command files = 18 installed artifacts.
```

## Frontmatter validation (sanity smoke)

```
$ awk '/^---$/{i++; if(i==2)exit} i==1' ~/.claude/skills/anticipating-shadow-points/SKILL.md | tail -n +2
name: anticipating-shadow-points
description: Use when starting any non-trivial task ...
```

- `name` field present ✅
- `description` starts with "Use when" ✅
- YAML parses without error ✅

## Discoverability check

The skill description includes high-CSO trigger words: "non-trivial task", "feature", "refactor", "migration", "deploy", "schema change", "debug", "investigation", "architecture decision". These should match the `using-superpowers` skill's "1% chance" invocation heuristic for any non-trivial software task.

The slash commands `/asp` and `/ASP` are present in `~/.claude/commands/` and contain `allowed-tools` frontmatter referencing `Skill`, `Agent`, `TaskCreate`, `TaskUpdate`, `TaskList`, `Bash`, `Read`, `Grep`, `Glob`, `Write`, `Edit`, `AskUserQuestion`.

## Manual smoke test instructions (for the user to perform)

The skill is now live. To complete the smoke test, the user should:

1. Open a fresh Claude Code session.
2. Type: `/asp test invocation`.
3. Observe:
   - The Skill tool should load `anticipating-shadow-points` (not Read).
   - The skill should ask Phase 0a Q&A (≤3 questions) before researching.
   - Output should reference Iron Laws and the 13-phase protocol.
4. To stop the test without executing a full ASP run, type "abort" or close the session.

## Limitations of in-session smoke

- Cannot open a fresh session from within this session to test the Skill tool's auto-invocation.
- `/goal` invocability already established as FAIL via pre-flight probe (`tests/goal-invocability-probe.md`); `--no-goal` is the effective default.
- The user inspection is the canonical smoke test for D13 (public release decision).

## Verdict

Install state: **OK**. Files present, frontmatter valid, commands discoverable. Skill ready for the user's fresh-session smoke test.
