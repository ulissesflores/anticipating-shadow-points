# Works — Complete artefact index

Every artefact produced in this project, with full GitHub links. Sorted by
relevance, not by directory.

**Repository**: https://github.com/ulissesflores/anticipating-shadow-points
**Documentation site**: https://ulissesflores.github.io/anticipating-shadow-points/
**Latest commits**:
- [`f5c65f6`](https://github.com/ulissesflores/anticipating-shadow-points/commit/f5c65f6) — v0.6.0 Iron Law 11 empirical addendum (N=50 → 60% silent refusal)
- [`5c656f1`](https://github.com/ulissesflores/anticipating-shadow-points/commit/5c656f1) — v0.4-v0.5.1 citation discipline + dual-paper restructure + pre-registered protocol

---

## 🎯 Headline empirical finding

**60.0% silent-refusal rate** on N=50 pre-registered trials against
`claude -p` (Claude Opus 4.7, Claude Code 2.1.143). 95% Clopper–Pearson
CI 46.5%–73.6%. Safety category: 100% silent refusal of all model-level
responses. Falsification verdict: **CONFIRMED (high)** per pre-registration
§3.6.

- Per-trial dataset: [`tests/iron-law-11/runs/published/2026-05-18T15-36-05Z-c1bceb85/`](https://github.com/ulissesflores/anticipating-shadow-points/tree/main/tests/iron-law-11/runs/published/2026-05-18T15-36-05Z-c1bceb85)
- Analysis report (human-readable): [`analysis-report.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/runs/published/2026-05-18T15-36-05Z-c1bceb85/analysis-report.md)
- Analysis JSON (machine-readable): [`analysis.json`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/runs/published/2026-05-18T15-36-05Z-c1bceb85/analysis.json)

---

## 📄 The two papers

### Paper 1 — Experience Report

> **ASP: An Operational Pre-Mortem Skill for LLM Coding Agents — An Experience Report**

5,300-word experience report on the system, with honest preliminary
empirics (n=8 author-adjudicated) and a generalist-to-specialist
introduction. Target venues: NeurIPS LLM-agents workshop, ICLR agents
workshop, AAAI agents track.

- **Canonical source**: [`paper/asp-preprint.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/paper/asp-preprint.md)
- LaTeX (outdated, MD is canonical): [`paper/asp-preprint.tex`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/paper/asp-preprint.tex)
- Bibliography: [`paper/references.bib`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/paper/references.bib)

### Paper 2 — Pre-Registered Protocol + Empirical Addendum

> **Graceful Refusals as Silent Successes: A Pre-Registered Protocol for Characterising `claude -p` Exit-Code Semantics**

Pre-registered protocol with the N=50 empirical addendum already folded
in (§10). 88% misclassification headline. Three constructive
recommendations to Anthropic in §10.8. Target venues: NeurIPS
LLM-tooling workshop, EMNLP system demonstrations, SoLaR workshop.

- **Canonical source**: [`paper/iron-law-11.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/paper/iron-law-11.md)
- §10 Empirical Addendum: same file, see §10
- Two-paper track explanation: [`paper/README.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/paper/README.md)

---

## 🧪 Pre-registered protocol — runnable scaffolding

The Iron Law 11 protocol is committed as runnable code. Anyone with
`claude` on PATH can reproduce N=50 in ~8 minutes for ~$5.

| File | Purpose |
|---|---|
| [`tests/iron-law-11/README.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/README.md) | Operational quick-start |
| [`tests/iron-law-11/preregistration.json`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/preregistration.json) | SHA-256 of every locked file + analysis plan + timestamp |
| [`tests/iron-law-11/refusal-phrases.txt`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/refusal-phrases.txt) | LOCKED phrase list used by `analyze.py` |
| [`tests/iron-law-11/random_seed.txt`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/random_seed.txt) | LOCKED seed for run-id determinism |
| [`tests/iron-law-11/scripts/run-protocol.sh`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scripts/run-protocol.sh) | Protocol dispatcher (Iron Laws 9/11/12 honored) |
| [`tests/iron-law-11/scripts/analyze.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scripts/analyze.py) | Pre-committed analysis (confusion matrix + Clopper–Pearson 95% CI + falsification verdict) |
| [`tests/iron-law-11/scripts/verify-prereg.sh`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scripts/verify-prereg.sh) | Hash-chain integrity check |
| [`tests/iron-law-11/scripts/_summarize-run.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scripts/_summarize-run.py) | Internal helper |

### The 50 locked scenarios

Pre-registered in 4 categories × 12–13 scenarios = 50 total. Hashed in
`preregistration.json`.

- **Category A — Explicit refusal** (N=13): [A.01](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.01.txt) · [A.02](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.02.txt) · [A.03](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.03.txt) · [A.04](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.04.txt) · [A.05](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.05.txt) · [A.06](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.06.txt) · [A.07](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.07.txt) · [A.08](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.08.txt) · [A.09](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.09.txt) · [A.10](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.10.txt) · [A.11](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.11.txt) · [A.12](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.12.txt) · [A.13](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/A.13.txt)
- **Category B — Capability refusal** (N=13): [B.01](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.01.txt) · [B.02](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.02.txt) · [B.03](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.03.txt) · [B.04](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.04.txt) · [B.05](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.05.txt) · [B.06](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.06.txt) · [B.07](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.07.txt) · [B.08](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.08.txt) · [B.09](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.09.txt) · [B.10](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.10.txt) · [B.11](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.11.txt) · [B.12](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.12.txt) · [B.13](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/B.13.txt)
- **Category C — Safety refusal** (N=12): [C.01](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.01.txt) · [C.02](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.02.txt) · [C.03](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.03.txt) · [C.04](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.04.txt) · [C.05](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.05.txt) · [C.06](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.06.txt) · [C.07](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.07.txt) · [C.08](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.08.txt) · [C.09](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.09.txt) · [C.10](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.10.txt) · [C.11](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.11.txt) · [C.12](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/C.12.txt)
- **Category D — Ambiguity refusal** (N=12): [D.01](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.01.txt) · [D.02](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.02.txt) · [D.03](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.03.txt) · [D.04](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.04.txt) · [D.05](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.05.txt) · [D.06](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.06.txt) · [D.07](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.07.txt) · [D.08](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.08.txt) · [D.09](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.09.txt) · [D.10](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.10.txt) · [D.11](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.11.txt) · [D.12](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/scenarios/D.12.txt)

### Smoke test (3 non-formal scenarios used during scaffolding)

- [S.01](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/smoke/scenarios/S.01.txt) — trivial math (2+2)
- [S.02](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/smoke/scenarios/S.02.txt) — safety refusal (first observation of failure mode in a new category)
- [S.03](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/iron-law-11/smoke/scenarios/S.03.txt) — ambiguity ("Fix the bug")

---

## 🐍 Benchmark Python package — deterministic adjudicator + cryptographic provenance

Python package (zero runtime deps) that replaces hand-adjudication with a
deterministic 4-layer matcher and produces a hash-chained manifest per run.
27/27 unit tests passing.

- [`benchmark/PROTOCOL.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/PROTOCOL.md) — Scientific specification
- [`benchmark/README.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/README.md) — Operational quick-start
- [`benchmark/pyproject.toml`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/pyproject.toml) — Package metadata

### Source modules

- [`src/asp_benchmark/hasher.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/src/asp_benchmark/hasher.py) — SHA-256 Merkle-style tree
- [`src/asp_benchmark/eval_parser.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/src/asp_benchmark/eval_parser.py) — Strict parser for eval markdown
- [`src/asp_benchmark/adjudicator.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/src/asp_benchmark/adjudicator.py) — 4-layer deterministic match
- [`src/asp_benchmark/runner.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/src/asp_benchmark/runner.py) — RED/GREEN dispatch + mock mode + Iron Laws 11/12
- [`src/asp_benchmark/manifest.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/src/asp_benchmark/manifest.py) — Build/verify hash chain
- [`src/asp_benchmark/report.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/src/asp_benchmark/report.py) — Markdown report
- [`src/asp_benchmark/env_fingerprint.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/src/asp_benchmark/env_fingerprint.py) — Python/OS/claude versions
- [`src/asp_benchmark/cli.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/src/asp_benchmark/cli.py) — `run` / `verify` / `list` subcommands

### Tests (27 passing)

- [`tests/test_hasher.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/tests/test_hasher.py) — 13 tests (hash stability, tamper detection)
- [`tests/test_adjudicator.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/tests/test_adjudicator.py) — 6 tests (each match layer + determinism)
- [`tests/test_eval_parser.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/tests/test_eval_parser.py) — 4 tests (parser correctness)
- [`tests/test_manifest.py`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/tests/test_manifest.py) — 4 tests (end-to-end + tamper detection)

### Published reproducible run

- [`runs/published/2026-05-18T00-27-43Z-b0a1bc7b/`](https://github.com/ulissesflores/anticipating-shadow-points/tree/main/benchmark/runs/published/2026-05-18T00-27-43Z-b0a1bc7b) — Full hash-chained evidence
- [`manifest.json`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/runs/published/2026-05-18T00-27-43Z-b0a1bc7b/manifest.json) — Manifest hash: `1a820c27f6076925fe135417b7c6b284ad98ce57171b346852ef6ccce2e3cdd9`
- [`report.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/benchmark/runs/published/2026-05-18T00-27-43Z-b0a1bc7b/report.md) — Human-readable report

---

## 🛠️ The ASP Skill (the thing the papers describe)

The actual Claude Code skill that implements the 13-phase protocol with
12 Iron Laws. Distributed via plugin marketplace, dev mode, or standalone.

- [`SKILL.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/SKILL.md) — Main skill file (13 phases + 12 Iron Laws)
- [`methodology.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/methodology.md) — Mitchell+Klein, MAST, Plan-and-Act, validator isolation
- [`mast-checklist.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/mast-checklist.md) — 14 modes verbatim from Cemri et al. (2025)
- [`question-frames.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/question-frames.md) — Phase 0a/0b Q&A frames
- [`claude-p-goal-runner.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/claude-p-goal-runner.md) — Subprocess spawn pattern + Iron Laws 9-12
- [`execution-kernel.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/execution-kernel.md) — Fallback in-session kernel

### Templates (artifacts emitted per phase)

- [`project-charter.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/templates/project-charter.md)
- [`macro-plan.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/templates/macro-plan.md)
- [`deliverables-register.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/templates/deliverables-register.md)
- [`micro-todo.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/templates/micro-todo.md)
- [`goal-spec.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/templates/goal-spec.md)
- [`acceptance-contract.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/templates/acceptance-contract.md)
- [`execution-report.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/templates/execution-report.md)

### The 5 ASP evaluations (used by Paper 1 + benchmark)

- [`evals/01-supabase-migration.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/evals/01-supabase-migration.md) (E1)
- [`evals/02-edge-function-deploy.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/evals/02-edge-function-deploy.md) (E2)
- [`evals/03-refactor-shared-util.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/evals/03-refactor-shared-util.md) (E3)
- [`evals/04-rls-policy-change.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/evals/04-rls-policy-change.md) (E4)
- [`evals/05-cron-skill-conflict.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/skills/anticipating-shadow-points/evals/05-cron-skill-conflict.md) (E5)

---

## 📦 Distribution (Claude Code plugin)

- [`.claude-plugin/plugin.json`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/.claude-plugin/plugin.json) — Official Anthropic plugin manifest
- [`.claude-plugin/marketplace.json`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/.claude-plugin/marketplace.json) — Self-host marketplace catalog
- [`commands/asp.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/commands/asp.md) — `/asp` slash command entry point
- [`scripts/install.sh`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/scripts/install.sh) — Standalone installer
- [`scripts/uninstall.sh`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/scripts/uninstall.sh) — Standalone uninstaller
- [`scripts/verify.sh`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/scripts/verify.sh) — Install verification

---

## 📚 Documentation

### Repository home + landing

- [`README.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/README.md) — GitHub repo home (marketing-first)
- [`index.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/index.md) — GitHub Pages landing (marketing-first)
- Live site: https://ulissesflores.github.io/anticipating-shadow-points/

### Deep-dive architecture

- [`docs/ARCHITECTURE.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/docs/ARCHITECTURE.md) — 10-part SOTA design doc (academic background, v1→v5 journey, Iron Law derivations, novelty claims)

### Translations

- [`docs/translations.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/docs/translations.md) — Translation index
- [`docs/README.es.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/docs/README.es.md) — Español 🇪🇸 (AI-assisted, pending native review)
- [`docs/README.pt.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/docs/README.pt.md) — Português 🇧🇷 (native)
- [`docs/README.it.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/docs/README.it.md) — Italiano 🇮🇹 (AI-assisted, pending native review)
- [`docs/README.he.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/docs/README.he.md) — עברית 🇮🇱 (AI-assisted, pending native review)

---

## 📣 Social-channel templates (research-release artefacts)

Channel-specific copy ready to post once Paper 2's notification step happens.

- [`social/README.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/social/README.md) — Staging plan + anti-patterns
- [`social/LINKEDIN.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/social/LINKEDIN.md) — Long-form article (~2,000 words, CTO + academic audience)
- [`social/TWITTER_THREAD.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/social/TWITTER_THREAD.md) — 12-tweet thread + canned responses
- [`social/HN_SHOW.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/social/HN_SHOW.md) — Show HN title + body + 7 canned responses
- [`social/REDDIT_ML.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/social/REDDIT_ML.md) — [R]-tagged post
- [`social/HF_PAPERS.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/social/HF_PAPERS.md) — Hugging Face Papers submission steps
- [`social/BLUESKY_MASTODON.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/social/BLUESKY_MASTODON.md) — Fediverse adaptation
- [`social/PERSONAL_BLOG.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/social/PERSONAL_BLOG.md) — Long-form blog outline (2,500–4,000 words)

---

## 🤝 Community / governance

- [`CITATION.cff`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CITATION.cff) — GitHub "Cite this repository" button
- [`CHANGELOG.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CHANGELOG.md) — Versioned history v0.1.0 → v0.6.0
- [`CONTRIBUTING.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CONTRIBUTING.md) — Contribution guide
- [`CODE_OF_CONDUCT.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CODE_OF_CONDUCT.md) — Code of conduct
- [`SECURITY.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/SECURITY.md) — Vulnerability disclosure
- [`AUTHORS`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/AUTHORS) — Maintainer + contributors
- [`AGENTS.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/AGENTS.md) — Rules for AI agents editing the repo
- [`PRIVACY.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/PRIVACY.md) — Privacy notice (no telemetry, client-side only)
- [`LICENSE`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/LICENSE) — MIT for software; paper text is CC BY 4.0

### GitHub config

- [`.github/workflows/ci.yml`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/.github/workflows/ci.yml) — CI pipeline
- [`.github/ISSUE_TEMPLATE/bug_report.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/.github/ISSUE_TEMPLATE/bug_report.md)
- [`.github/ISSUE_TEMPLATE/feature_request.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/.github/ISSUE_TEMPLATE/feature_request.md)
- [`.github/ISSUE_TEMPLATE/eval_contribution.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/.github/ISSUE_TEMPLATE/eval_contribution.md)
- [`.github/PULL_REQUEST_TEMPLATE.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/.github/PULL_REQUEST_TEMPLATE.md)
- [`.github/FUNDING.yml`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/.github/FUNDING.yml)

---

## 🧪 Earlier test artefacts (preliminary RED/GREEN battery)

Original n=8 hand-adjudicated battery used in Paper 1 §5.

- [`tests/baseline-pressure-tests.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/baseline-pressure-tests.md) — RED baseline scenarios
- [`tests/evals-summary.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/evals-summary.md) — Adjudication summary
- [`tests/claude-p-goal-runner-probe.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/claude-p-goal-runner-probe.md) — Original 4-test battery that surfaced Iron Law 11
- [`tests/goal-invocability-probe.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/goal-invocability-probe.md) — `/goal` invocability check
- [`tests/execution-report-v5-FINAL.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/execution-report-v5-FINAL.md) — Closure artifact from v5 design
- [`tests/advisor-final.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/advisor-final.md) — advisor() review record
- [`tests/criteria-final-checklist.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/criteria-final-checklist.md) — Acceptance criteria checklist
- [`tests/demo-charter.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/demo-charter.md) · [`tests/demo-deliverables.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/demo-deliverables.md) · [`tests/demo-execution-report.md`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/tests/demo-execution-report.md) — Demo artefacts

---

## 🔗 External references

- **arXiv preprint**: pending submission (Markdown source canonical in `paper/`)
- **Zenodo DOI**: pending registration (one-time GitHub-Zenodo OAuth on next tagged release)
- **Anthropic plugin directory listing**: pending review
- **Author site**: https://ulissesflores.com

### Verified primary citations referenced across the work

Top primary sources cited in `paper/asp-preprint.md` and `paper/iron-law-11.md`,
verified by direct URL fetch on 2026-05-17:

- Mitchell, D. J., Russo, J. E., & Pennington, N. (1989). [*Back to the Future*](https://onlinelibrary.wiley.com/doi/10.1002/bdm.3960020103) — primary source for the ~30% prospective-hindsight effect.
- Klein, G. (2007). [*Performing a Project Premortem*](https://hbr.org/2007/09/performing-a-project-premortem) — HBR operational recipe.
- Cemri, M., et al. (2025). [*Why Do Multi-Agent LLM Systems Fail?*](https://arxiv.org/abs/2503.13657) — MAST 14-mode taxonomy.
- Huang, J., et al. (2024). [*LLMs Cannot Self-Correct Reasoning Yet*](https://arxiv.org/abs/2310.01798) — ICLR 2024.
- Tyen, G., et al. (2024). [*LLMs Cannot Find Reasoning Errors, but Can Correct Them Given the Error Location*](https://arxiv.org/abs/2311.08516) — localization is the bottleneck.
- Zheng, L., et al. (2023). [*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*](https://arxiv.org/abs/2306.05685) — NeurIPS 2023 D&B, self-enhancement bias.
- Wang, H., et al. (2026). [*PreFlect: From Retrospective to Prospective Reflection*](https://arxiv.org/abs/2602.07187) — closest concurrent work.
- Erdogan, L. E., et al. (2025). [*Plan-and-Act*](https://arxiv.org/abs/2503.09572) — ICML 2025.
- Shinn, N., et al. (2023). [*Reflexion*](https://arxiv.org/abs/2303.11366) — NeurIPS 2023.
- Deng, X., et al. (2025). [*SWE-Bench Pro*](https://arxiv.org/abs/2509.16941) — arXiv.

Full bibliography (26 verified primary entries): [`paper/references.bib`](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/paper/references.bib)
