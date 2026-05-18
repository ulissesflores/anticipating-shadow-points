# AGENTS.md — Rules for AI agents editing this repository

Rules for any AI coding agent (Claude Code, Cursor, Copilot, Codex, Gemini CLI, custom agents) that opens, edits, or commits to **`ulissesflores/anticipating-shadow-points`**.

These rules are meta-aligned with the skill itself: an "anticipating-shadow-points" repository should follow its own protocol when it accepts edits.

---

## Scope

This file applies to repository **editing** — manifest changes, code refactors, doc updates, test additions, CI changes. It does NOT apply to runtime invocation of the `/asp` skill on user tasks (that's governed by `skills/anticipating-shadow-points/SKILL.md`).

---

## Cardinal rule — repo vs publications separation

The repo is **the product**: skill, whitepapers (Markdown source), benchmark, pre-registered protocol, distribution manifests, documentation. Anything that supports a citing reader, user, or researcher of the work belongs here.

The repo is **not** ops. Marketing copy, social-media posts, launch calendars, engagement playbooks, status trackers, influencer DM templates, newsletter outreach drafts, scheduled-post metadata — **all of that lives outside the repo**, in `~/Developer/Publications/anticipating-shadow-points/<version>-launch/`, and is operated by a separate agent (or the human author manually). The publications dir is intentionally never committed to this repository.

The principle behind this separation, articulated by the maintainer: *artefato de geração ≠ produto gerado*. Every file in the repo must justify its presence as a product — not as a record of how the product was made. The journey is in `git log`, the build records are in commits, the changelog summarises versions. We do not duplicate that history as in-tree documents.

An agent editing this repo therefore:

- **MUST NOT** add a `social/`, `launch/`, `marketing/`, or `publications/` directory
- **MUST NOT** commit launch-status trackers, posting calendars, or social-media drafts
- **MUST NOT** add files that document journey-state (build journals, scratchpad reports, demo artefacts that aren't cited as evidence in a paper)
- **CAN** point at the external `~/Developer/Publications/...` path from docs or CHANGELOG when relevant, but only as an out-of-tree reference

---

## Layered responsibility

| Layer | Responsibility |
|---|---|
| **This repository** | Source of truth for the ASP skill, plugin manifest, marketplace catalog, multilingual docs, install/verify scripts. |
| **`skills/anticipating-shadow-points/SKILL.md`** | Runtime behavior when the skill is loaded into a user session. Not the place for repo maintenance rules. |
| **`docs/ARCHITECTURE.md`** | Living design document. Methodology changes MUST be reflected here. |
| **`tests/`** | Empirical evidence. Baselines, probes, eval results, advisor calls. Append-only style preferred (don't delete; archive). |

---

## Mandatory checks before committing

1. **Conventional Commits** message: `feat|fix|docs|refactor|test|chore|eval|i18n(<scope>): <imperative>`.
2. **DCO sign-off** on every commit: `git commit -s` (or `--signoff`). PRs without DCO are blocked.
3. **`./scripts/verify.sh --pre-install` passes** (19/20 OK; criterion 13 skipped pre-install).
4. **Iron Laws preserved** — any commit touching `claude-p-goal-runner.md`, `execution-kernel.md`, or `SKILL.md` must explicitly state which Iron Laws are affected and confirm they remain valid.
5. **No literal asset paths in marketplace.json descriptions** — Rule 5 from the netresearch marketplace contribution standard; apply same discipline here.

---

## Things that REQUIRE human approval before commit

| Change | Why |
|---|---|
| Modifying any **Iron Law** | Foundational discipline; changes need explicit human accept |
| Force-push to `main` | Public branch; rewriting history affects external consumers |
| Bumping major version (1.x) | Implies breaking changes to API/CLI/manifest |
| Removing an existing eval | Empirical evidence; archive rather than delete |
| Editing `docs/ARCHITECTURE.md` Part 7 (Iron Laws derivation) | Tied to the laws themselves |
| Touching `LICENSE` or `CITATION.cff` author fields | Identity/attribution |
| Public-facing description changes in `plugin.json` or `marketplace.json` | Visible in marketplaces |
| Changes to `_config.yml` or GitHub Pages structure | Affects published docs site |

For these, the agent should: propose the change in a PR, write the rationale, and wait for explicit human approval before merging.

---

## Things an agent CAN do autonomously

- Typo/grammar fixes in any prose file.
- Adding evals to `skills/anticipating-shadow-points/evals/` following the existing format.
- Updating `CHANGELOG.md` for the current `[Unreleased]` section.
- Translation refinements (with PR; native-speaker review is optional for grammar, required for semantic changes).
- Adding new `tests/evidence/` files when a verification run produces them.
- Closing stale issues per maintainer's instructions.
- CI/tooling improvements that don't change build outputs (e.g., faster shellcheck install).

---

## Working with the SOTA design doc

`docs/ARCHITECTURE.md` is the canonical methodology record. When making any change that affects methodology, the agent MUST:

1. Read the relevant section(s) of ARCHITECTURE.md FIRST.
2. Identify which Iron Law(s), MAST mode(s), or methodological principle(s) the change touches.
3. If methodology shifts, add an entry to the appropriate section (Part 3 for journey, Part 4 for empirical, Part 7 for Iron Law derivation).
4. Cross-reference: the SKILL.md change, the ARCHITECTURE.md update, and the CHANGELOG entry should all point at each other.

---

## Recall pattern

If `~/.agent/tools/recall.py` is available in the agent's environment AND the change is non-trivial (deploy, migration, schema change, security touch, dependency bump), the agent SHOULD run recall first:

```bash
python3 ~/.agent/tools/recall.py "<short description of the planned change>"
```

Surface the results in a `Consulted lessons before editing:` block in the commit message body or PR description.

---

## What to do if you're unsure

1. Open a Draft PR with the proposed change.
2. Explain your uncertainty in the PR description.
3. Tag the maintainer ([@ulissesflores](https://github.com/ulissesflores)) if no review in 72 hours.
4. Do NOT force-push or merge your own PRs.

---

## Why this file exists

ASP is a meta-skill — its own existence demonstrates the value of structured planning for high-stakes work. The repository, therefore, should be edited under the same discipline it preaches. This file makes that discipline explicit so any agent (human-augmented or autonomous) operates with shared expectations.
