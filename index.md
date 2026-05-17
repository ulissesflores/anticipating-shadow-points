---
title: Home
layout: default
nav_order: 1
description: "ASP — Anticipating Shadow Points: 13-phase planning protocol for Claude Code. Klein pre-mortem + Berkeley MAST 14-mode + claude -p /goal subprocess execution kernel + 12 Iron Laws. MIT. Multilingual docs (EN/ES/PT/IT/HE)."
permalink: /
---

# ASP — Anticipating Shadow Points
{: .fs-9 }

A Claude Code skill that turns ambitious tasks into shipped deliverables — through forced upfront research, pre-mortem shadow-point detection, validator-checked plans, contractual micro-TODOs, and `claude -p /goal` subprocess execution.
{: .fs-5 .fw-300 }

[Quick install](#quick-install){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/ulissesflores/anticipating-shadow-points){: .btn .fs-5 .mb-4 .mb-md-0 }
[Architecture](docs/ARCHITECTURE){: .btn .fs-5 .mb-4 .mb-md-0 .ml-2 }

---

## What is ASP?

**ASP** stands for **Ant-Shadow-Point** — those tiny, easily-missed failure modes that hide in the shadows of any non-trivial task and surface later as bugs, incidents, or rejected PRs.

Invoked as `/asp <your task>`, this skill orchestrates a 13-phase protocol combining:

- **Klein's pre-mortem** (Harvard Business Review, 1998/2007)
- **Berkeley MAST 14-mode failure taxonomy** ([arxiv 2503.13657](https://arxiv.org/abs/2503.13657))
- **Plan-and-Act separation** with independent validator subagent (prompt isolation)
- **Contractual `TaskCreate` micro-TODO** (PRE / ACT / POST / ACCEPTANCE / FALSIFICATION fields)
- **`claude -p /goal` subprocess execution kernel** (Anthropic, 2026-05-12)
- **12 Iron Laws** enforced at every checkpoint

Empirically validated 2026-05-17: coverage of expected shadow points rises from **~47% (baseline)** to **~100% (with ASP loaded)**.

---

## Quick install

**One-step install via Claude Code's native plugin manager:**

```bash
claude plugin marketplace add ulissesflores/anticipating-shadow-points
claude plugin install anticipating-shadow-points@anticipating-shadow-points
```

Then invoke `/anticipating-shadow-points:asp <task>` in any Claude Code session.

Two more install paths (dev mode `--plugin-dir`; standalone `install.sh` for bare `/asp` invocation) are documented in the [GitHub README](https://github.com/ulissesflores/anticipating-shadow-points#quick-start).

---

## Why ASP

If you've ever shipped something and 24 hours later thought *"why didn't I think of that?"*, ASP is for you.

| Appropriate for | Overkill for |
|---|---|
| Features touching data or shared state | Typo fixes |
| Migrations (schema, dependency, API) | Single-line edits |
| Refactors across many files | Read-only questions |
| Deploys with external dependencies | |
| Architecture decisions | |
| Root-cause debug investigations | |

---

## What's new — v0.2.2

- **`CITATION.cff`** — repository is now academically citable (the four foundational papers are listed as references).
- **`CONTRIBUTING.md`**, **`CODE_OF_CONDUCT.md`** (Contributor Covenant 2.1), **`SECURITY.md`** — full community signal.
- **`AGENTS.md`** — meta-aligned rules for AI agents editing this repository (the skill applied to its own development).
- **`AUTHORS`**, **`CHANGELOG.md`** (Keep-a-Changelog format).
- **GitHub issue + PR templates** — DCO-aware, Iron Laws checklist.
- **Author profile complete** across `plugin.json`, `marketplace.json`, and all 5 language READMEs.

See the [full changelog](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CHANGELOG.md) for prior versions (v0.1.0 → v0.2.2).

---

## Documentation

- **[Full README on GitHub](https://github.com/ulissesflores/anticipating-shadow-points)** — quick start, all three install paths, troubleshooting.
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — 10-part state-of-the-art design document: academic background, v1→v5 journey, empirical discoveries (incl. Iron Law 11 finding), derivation of all 12 Iron Laws, open questions.
- **[Translations](translations/)** — Español, Português, Italiano, עברית (machine-assisted; native review welcomed via PR).

---

## Citing

If you use ASP in published work, an evaluation, or a production deployment, please cite via [CITATION.cff](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CITATION.cff). GitHub's "Cite this repository" button on the repo home reads this file automatically.

The four methodological references are also documented in CITATION.cff and should be cited alongside ASP when discussing the methodology in depth.

---

## License & maintainer

MIT licensed. Maintained by **[Ulisses Flores](https://ulissesflores.com)** — CTO & Chief Researcher at Codex Hash Ltda; MSc AI candidate, American Global Tech University. Itupeva, Brazil.

For consulting, partnership, or research collaboration: see [ulissesflores.com](https://ulissesflores.com).
