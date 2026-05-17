# Pull Request

## Summary

<!-- 1-3 bullets describing what this PR changes and why. -->

-

## Type of change

- [ ] `feat` — new feature or methodology refinement
- [ ] `fix` — bug fix
- [ ] `docs` — documentation only
- [ ] `eval` — new eval added (specify domain)
- [ ] `refactor` — code change without functional impact
- [ ] `test` — TDD baseline or eval test changes
- [ ] `chore` — tooling, CI, dependencies
- [ ] `i18n` — translation contribution (specify language)

## Affected components

<!-- Check all that apply. -->

- [ ] `skills/anticipating-shadow-points/SKILL.md`
- [ ] `skills/anticipating-shadow-points/methodology.md` or `mast-checklist.md`
- [ ] `skills/anticipating-shadow-points/claude-p-goal-runner.md` or `execution-kernel.md`
- [ ] `skills/anticipating-shadow-points/templates/`
- [ ] `skills/anticipating-shadow-points/evals/`
- [ ] `commands/`
- [ ] `scripts/` (install/uninstall/verify)
- [ ] `tests/` (baselines, probes, evidence)
- [ ] `docs/` (ARCHITECTURE, translations)
- [ ] README.md
- [ ] CI / `.github/workflows/`
- [ ] `.claude-plugin/` manifests

## Iron Laws check

<!-- Check all that apply to confirm this PR respects the relevant Iron Laws. -->

- [ ] No methodology change OR change is reflected in ARCHITECTURE.md (Iron Law 6).
- [ ] No new `claude -p` invocation OR new invocation uses `--output-format json|stream-json` and parses JSON (Iron Laws 11, 12).
- [ ] If touching execution kernel: evaluator dispatch preserved at checkpoints (Iron Law 8).
- [ ] If touching reentrancy: `ASP_IN_GOAL` env-var guard intact (Iron Law 9).
- [ ] Acceptance evidence captured for non-trivial changes (Iron Law 4): output, screenshot, or test result attached below.

## Verification

```bash
./scripts/verify.sh --pre-install
```

Expected: **19/20 OK** (criterion 13 skipped in pre-install mode).
Actual result here: <paste output>

## Translation PRs only

- [ ] Structural parallelism with English README preserved.
- [ ] Disclaimer about machine-assisted translation updated (or removed, if you are a native-speaker reviewer).
- [ ] Native-speaker review status (self-attestation) added to PR description below.

## DCO sign-off

- [ ] All commits in this PR include `Signed-off-by:` trailer (use `git commit -s`).

## Notes for maintainer

<!-- Anything that would help review: rationale for unusual choices, links to relevant discussion, follow-up work expected after merge, etc. -->

---

By submitting this pull request, I confirm that my contribution is made under the terms of the project's MIT license and that I have the right to make this contribution.
