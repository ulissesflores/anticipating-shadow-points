# Changelog

All notable changes to ASP are documented in this file.

Format follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning 2.0.0](https://semver.org/).

## [Unreleased]

### Planned
- Native-speaker review of ES/IT/HE translations (community PRs welcome).
- Additional evals from community domains.
- Optional `PreToolUse` hook for contract enforcement.
- Zenodo DOI activation on next tagged release (one-time GitHub-Zenodo OAuth).
- arXiv preprint submission (LaTeX source ready in `paper/`).

## [0.3.0] — 2026-05-17

### Added

Research-release artifacts, organized for a staged scientific-style announcement.

- **`paper/`** — LaTeX preprint source ready for arXiv submission:
  - `paper/asp-preprint.tex` — full ~10-page article (`article` class, ~3000 words) covering Abstract, Introduction, Related Work, The ASP Protocol, Empirical Evaluation, the `claude -p /goal` exit-code finding (Section 5), Discussion, Limitations, Future Work, References, Appendix A (empirical battery), Appendix B (software availability).
  - `paper/references.bib` — BibTeX bibliography with Klein, Cemri (MAST), Erdogan (Plan-and-Act), Shinn (Reflexion), Anthropic skill docs, the two cited `/goal` walkthroughs, and the community marketplace repos.
  - `paper/README.md` — build instructions, arXiv submission checklist, license notes (CC BY 4.0 for paper text; MIT for software).
- **`social/`** — copy-paste-ready templates for staged community announcement, organized by channel and posting cadence:
  - `social/README.md` — staging plan with anti-patterns and cross-channel consistency rules.
  - `social/LINKEDIN.md` — long-form (~2000 words) article framed for CTO + academic audience.
  - `social/TWITTER_THREAD.md` — 12-tweet thread with figure hooks and 3 canned-response templates.
  - `social/HN_SHOW.md` — title, body, and 7 canned responses for predictable Show HN critique categories.
  - `social/REDDIT_ML.md` — [R]-tagged submission with anticipated-critique answers (n-size, paraphrase tolerance, methodology vs prompt engineering, SWE-bench comparison).
  - `social/HF_PAPERS.md` — Hugging Face Papers submission steps (post arXiv).
  - `social/BLUESKY_MASTODON.md` — 5-post adaptation for the academic AI fediverse with server recommendations.
  - `social/PERSONAL_BLOG.md` — long-form blog post outline (2500–4000 words) for ulissesflores.com with SEO notes.
- **`PRIVACY.md`** — explicit privacy notice clarifying that ASP runs entirely client-side, collects no telemetry, and the only outbound network calls are `git` (for plugin install) and `claude -p` subprocess (governed by Anthropic's privacy policy).

### Changed

- **`CITATION.cff`** — added explicit `identifiers:` block with placeholders for the forthcoming arXiv ID and Zenodo DOI; added optional `orcid:` line (commented placeholder) for the author block.

### Why

ASP shipped through v0.2.x as a usable open-source skill with marketplace distribution and a polished marketing landing. v0.3.0 elevates it from "OSS release" to "research release" by adding the artifacts academic CS expects: a citable preprint, a software DOI deposit path, a privacy notice, and channel-specific announcement templates that respect community norms (academic AI fediverse, r/MachineLearning rigor, Show HN engagement pattern). Posting to social channels without these foundations would feel like marketing-push; posting with them positions ASP as an independent research contribution.

## [0.2.3] — 2026-05-17

### Changed
- **Landing page (`index.md`) rewritten as marketing-first SOTA showcase** — following patterns observed in shadcn/ui, biomejs.dev, bun.sh, htmx.org, and claude.com/product/claude-code. Hero is now action/benefit-oriented ("Ship ambitious work without missing the obvious."); subhead leads with numerical claim ("47% to 100% coverage"); proof block (3 big metrics + real before/after from RED/GREEN baseline) appears immediately after hero; feature grid as visual cards instead of bullet list; `/asp` demo block shows real structured output; "When to reach for ASP" green/red two-column matrix; footer is dense small-text for citation/community/license.
- **`README.md` rewritten with the same marketing-first structure**, adapted for GitHub repo home audience: kept badges, language switcher inline, three install paths with collapsible `<details>` for B/C, dedicated Troubleshooting section, Community section header.
- **Version field bumped in `.claude-plugin/plugin.json` (0.2.0 → 0.2.3)** so the version visible in `claude plugin details` aligns with the current release tag.
- **`CITATION.cff` version field bumped (0.2.1 → 0.2.3)** for the same alignment reason.

### Removed (from main flow — moved to footer or other docs)
- Big "Citing this work" section in body (now 1-line footer pointer to CITATION.cff).
- "What's new vN.x" version-history section.
- "How It Works — The 13 Phases" expansion (linked to ARCHITECTURE.md).
- "The Non-Violation Contract" body section (covered in `See it run` demo + ARCHITECTURE).
- "Depth Flags", "File Structure", "Optional integrations", "Status" sections.
- "Sources / Prior art" listing (lives in CITATION.cff and ARCHITECTURE.md).

### Why
The prior `index.md` and `README.md` were documentation-heavy: cold visitors got 2 lines of intro followed by academic citations and install paths, which doesn't sell the project. SOTA OSS landings answer three questions in the first 5 seconds: (a) what is this, (b) why should I care, (c) where do I click. The redesign delivers exactly that.

## [0.2.2] — 2026-05-17

### Added
- `CITATION.cff` — repository is now formally citable; references the four foundational papers (Klein 1998/2007, Berkeley MAST arxiv 2503.13657, Plan-and-Act arxiv 2503.09572, Reflexion).
- `CONTRIBUTING.md` — formal contribution guide with workflow, commit conventions, and PR expectations.
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1 adoption + reporting/enforcement procedures.
- `SECURITY.md` — vulnerability disclosure policy.
- `AUTHORS` — maintainer and contributor list with attribution model.
- `AGENTS.md` — rules for AI agents editing this repository (meta-skill alignment).
- `.github/ISSUE_TEMPLATE/` — bug report, feature request, eval contribution templates + config.
- `.github/PULL_REQUEST_TEMPLATE.md` — DCO-aware PR checklist.
- `.github/FUNDING.yml` — sponsor button placeholder (opt-in).
- `plugin.json` author field expanded with `email` and `url` (homepage).
- `marketplace.json` owner field expanded with `email`.

### Changed
- `plugin.json` `author.url` is now `https://ulissesflores.com` (was GitHub URL only).

## [0.2.1] — 2026-05-17

### Added
- "Example Use Cases" section in README and four translations (EN/ES/PT/IT/HE).
- "Troubleshooting" section consolidating SSH→HTTPS workaround, `/asp` vs `/anticipating-shadow-points:asp` invocation, and `recall.py` opt-in notes.
- Plugin homepage URL in manifests pointing to GitHub Pages.
- Docs badge in README.

### Changed
- GitHub Pages enabled with `just-the-docs` remote theme — published at https://ulissesflores.github.io/anticipating-shadow-points/.
- Jekyll front-matter added to README and key docs for navigation.
- CI workflow paths updated post-v0.2.0 restructure; added `plugin.json` and `marketplace.json` validation jobs.

### Fixed
- `verify.sh` shellcheck warnings (removed unused `COMMAND_SRC` and `HOME_CMDS` variables).

## [0.2.0] — 2026-05-17

### Added
- `.claude-plugin/plugin.json` manifest (official Anthropic plugin spec).
- `.claude-plugin/marketplace.json` — repo is now a self-host marketplace; one-step install via `/plugin marketplace add ulissesflores/anticipating-shadow-points`.
- Triple-distribution model documented in `docs/ARCHITECTURE.md` Section 8.7.

### Changed
- **BREAKING (file layout)**: `skill/` → `skills/anticipating-shadow-points/`; `command/` → `commands/`. Plugin spec requires plural directory names and per-skill subdirectories. `install.sh` and `verify.sh` source paths updated.
- Plugin namespace: invocation is `/anticipating-shadow-points:asp` when installed via plugin manager; bare `/asp` remains via `install.sh` standalone path.

### Empirical validation
- `claude --plugin-dir ~/Developer/ASP` smoke test confirms all four invocation aliases register in session `slash_commands` and `skills` lists.
- `claude plugin marketplace add` + `claude plugin install` validated end-to-end.

## [0.1.1] — 2026-05-17

### Added
- `docs/ARCHITECTURE.md` — comprehensive state-of-the-art design document (10 parts: academic background, v1→v5 journey, empirical discoveries, Iron Law derivation, novelty claims, open questions, references).
- Cross-links from README and four translations to ARCHITECTURE.md.

## [0.1.0] — 2026-05-17

### Initial release
- 13-phase planning protocol: Klein pre-mortem, Berkeley MAST 14-mode, Plan-and-Act, independent validator subagent, contractual TaskCreate micro-TODO, `claude -p /goal` subprocess execution kernel, per-deliverable sign-off, memory write-back.
- 12 Iron Laws documented in `skills/anticipating-shadow-points/SKILL.md`.
- Iron Law 11 empirically discovered 2026-05-17: NEVER trust `$?` from `claude -p` for semantic success/failure — parse JSON instead.
- 5 structured evals + RED/GREEN/REFACTOR baseline tests showing coverage lift from ~47% to ~100%.
- Multilingual documentation (EN/ES/PT/IT/HE) — EN native; ES/IT/HE machine-assisted with native review welcomed.
- Idempotent `install.sh` + `uninstall.sh` + `verify.sh` (16 success criteria → expanded to 19 in v0.2.0).
- MIT license.

[Unreleased]: https://github.com/ulissesflores/anticipating-shadow-points/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/ulissesflores/anticipating-shadow-points/compare/v0.2.3...v0.3.0
[0.2.3]: https://github.com/ulissesflores/anticipating-shadow-points/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/ulissesflores/anticipating-shadow-points/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/ulissesflores/anticipating-shadow-points/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/ulissesflores/anticipating-shadow-points/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/ulissesflores/anticipating-shadow-points/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ulissesflores/anticipating-shadow-points/releases/tag/v0.1.0
