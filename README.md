# ASP — Anticipating Shadow Points

[![Version](https://img.shields.io/github/v/release/ulissesflores/anticipating-shadow-points?sort=semver&color=blue)](https://github.com/ulissesflores/anticipating-shadow-points/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code 2.1.139+](https://img.shields.io/badge/Claude%20Code-2.1.139%2B-blue.svg)](https://code.claude.com)
[![Docs](https://img.shields.io/badge/docs-online-blue.svg)](https://ulissesflores.github.io/anticipating-shadow-points/)
[![Citation](https://img.shields.io/badge/cite-CITATION.cff-purple.svg)](CITATION.cff)
[![Code of Conduct](https://img.shields.io/badge/contributor%20covenant-2.1-green.svg)](CODE_OF_CONDUCT.md)
[![Plugin Marketplace](https://img.shields.io/badge/plugin-marketplace--ready-brightgreen.svg)](#install)

## Ship ambitious work without missing the obvious.

ASP is a Claude Code skill that lifts shadow-point coverage from **47% to 100%** on non-trivial tasks — through forced pre-mortem, independent validator, and `claude -p /goal` subprocess execution.

🇬🇧 English (this file) · [🇪🇸 Español](docs/README.es.md) · [🇧🇷 Português](docs/README.pt.md) · [🇮🇹 Italiano](docs/README.it.md) · [🇮🇱 עברית](docs/README.he.md)

---

## The proof

<table>
<tr>
<td align="center" width="33%">
<h1>47% → 100%</h1>
shadow-point coverage<br>(baseline vs. with ASP)
</td>
<td align="center" width="33%">
<h1>12</h1>
non-negotiable Iron Laws<br>enforced at runtime
</td>
<td align="center" width="33%">
<h1>5</h1>
structured evals<br>across real domains
</td>
</tr>
</table>

### Same task, two outcomes

Real subagent dispatches from the 2026-05-17 RED/GREEN baseline. Task: *"Add a NOT NULL column `tier` (default 'free') to `user_profiles`. Table has 1M rows in production."*

<table>
<tr>
<td width="50%" valign="top">

**❌ Without ASP — baseline agent**

```sql
ALTER TABLE user_profiles
  ADD COLUMN tier text
  NOT NULL DEFAULT 'free';

CREATE INDEX CONCURRENTLY
  idx_user_profiles_tier
  ON user_profiles (tier);
```

*~60% coverage.* Misses: replica lag, app deploy ordering, monitoring spike, trigger interaction, foreign key cascade.

</td>
<td width="50%" valign="top">

**✅ With ASP — same agent, same task**

```text
Pre-mortem (30 days out):
 1. Full table rewrite locks
 2. RLS policy not updated
 3. Stale TS client types
 4. Service-role bypass risk
 5. Replica lag during DDL
 6. App deploy ordering
 7. Monitoring spike
 8. Backup window collision
 9. Index INVALID state
10. WAL/disk pressure
11. CDC realtime flood
12. Rollback impossible
13. CPU credit exhaustion
14. Audit trail missing
15. Time-zone in cron logic
```

*100% coverage.* Each surfaces a mitigation before any SQL runs.

</td>
</tr>
</table>

*Built on proven methodology · [Klein pre-mortem](https://hbr.org/2007/09/performing-a-project-premortem) · [Berkeley MAST 14-mode](https://arxiv.org/abs/2503.13657) · [Plan-and-Act](https://arxiv.org/abs/2503.09572) · Reflexion · empirically validated 2026-05-17*

---

## What ASP does

<table>
<tr>
<td width="50%" valign="top">

### 🎯 Pre-mortem before code

"Imagine the failure. Now describe why." Prospective hindsight — Mitchell, Russo & Pennington (1989) showed it generates ~30% more reasons than imagining the same event as merely possible; Klein (2007, HBR) operationalized it as the pre-mortem. ASP runs it on every non-trivial task.

</td>
<td width="50%" valign="top">

### 🔍 MAST 14-mode checklist

Berkeley's failure taxonomy forces coverage of less-obvious categories — time/timezone, observability, op-ex, contract drift — that free-form pre-mortem clusters away from.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🛡️ Independent validator

A fresh-prompt subagent audits the plan before execution. Self-critique fails on high-confidence hallucinations; prompt isolation breaks that collusion. **Iron Law 2**.

</td>
<td width="50%" valign="top">

### ⚡ `claude -p /goal` kernel

Spawns Anthropic's official worker/evaluator kernel as a subprocess. Empirically validated 2026-05-17. **Iron Law 11**: never trust `$?` — parse JSON.

</td>
</tr>
</table>

---

## See it run

```text
$ /asp Add a NOT NULL column `tier` to user_profiles. 1M rows.

Phase 1 — Parallel research (codebase + web + recall.py)          ✓
Phase 2 — Shadow-point detection (Klein + MAST 14-mode)            ✓ 14 found
Phase 4 — Macro plan + Deliverables Register (D01..D08)            ✓
Phase 5 — Independent validator (separate-prompt subagent)         APPROVE
Phase 7 — Awaiting user approval of charter + plan + deliverables  ✓
Phase 8 — Micro-TODO contract emitted: 23 tasks (PRE/ACT/POST/ACC/FAL)
Phase 9 — claude -p /goal autonomous execution                     → running

Goal Spec: All 23 tasks completed with ACCEPTANCE-TEST evidence;
           all 8 deliverables marked `aceito`; 12 Iron Laws respected.
Hard stops: turn > 80 · elapsed > 30min · 3 consecutive falsifications.
```

Every step is auditable. Every task has a verifiable acceptance test. Nothing ships without fresh evidence.

---

## Install

### Path A — Plugin marketplace (recommended, Claude Code 2.1+)

```bash
claude plugin marketplace add ulissesflores/anticipating-shadow-points
claude plugin install anticipating-shadow-points@anticipating-shadow-points
```

Invoke: `/anticipating-shadow-points:asp <task>` in any Claude Code session.

<details>
<summary><b>Other install paths</b> — dev mode and standalone script</summary>

### Path B — Local plugin dev mode (`--plugin-dir`)

For testing/development without installing permanently:

```bash
git clone https://github.com/ulissesflores/anticipating-shadow-points.git ~/Developer/ASP
claude --plugin-dir ~/Developer/ASP
```

Loaded only for that session. Invoke: `/anticipating-shadow-points:asp <task>`.

### Path C — Standalone `install.sh` (legacy, full control)

For users who want bare `/asp` invocation (no plugin namespace) or want to inspect/modify before install:

```bash
git clone https://github.com/ulissesflores/anticipating-shadow-points.git ~/Developer/ASP
cd ~/Developer/ASP
./scripts/verify.sh --pre-install
./scripts/install.sh
```

Invoke: `/asp <task>` (no namespace). Uninstall: `./scripts/uninstall.sh`.

</details>

**Requirements**: Claude Code 2.1.139+ · `bash` · `jq` · *(optional)* `~/.agent/` agentic-stack for `recall.py` lessons retrieval (silently skipped if absent).

---

## When to reach for ASP

<table>
<tr>
<th align="left" width="50%">✅ Use ASP for</th>
<th align="left" width="50%">❌ Skip ASP for</th>
</tr>
<tr>
<td valign="top">

- Features touching data or shared state
- Migrations (schema, dependency, API)
- Refactors across many files
- Deploys with external dependencies
- Architecture decisions
- Root-cause debug investigations

</td>
<td valign="top">

- Typo fixes
- Single-line edits
- Read-only questions ("what does X do?")
- Tasks you can finish in under 5 minutes

</td>
</tr>
</table>

---

## Troubleshooting

<details>
<summary><b><code>claude plugin install</code> fails with SSH permission denied</b></summary>

If you see `git@github.com: Permission denied (publickey)` during `claude plugin install`, your git is configured to use SSH but you don't have an SSH key registered with GitHub. The `marketplace add` step has automatic HTTPS fallback, but `install` does not (as of Claude Code 2.1.143).

One-time workaround:

```bash
git config --global url."https://github.com/".insteadOf "git@github.com:"
```

Then retry `claude plugin install`.

</details>

<details>
<summary><b><code>/asp</code> works but <code>/anticipating-shadow-points:asp</code> doesn't (or vice versa)</b></summary>

The two invocations come from different install paths and don't conflict:

- `/asp` works after Path C (`install.sh`) — installs without plugin namespace.
- `/anticipating-shadow-points:asp` works after Path A or Path B — plugin-namespaced.

Both can coexist.

</details>

<details>
<summary><b>Plugin name shows up twice (<code>name@marketplace</code>)</b></summary>

`anticipating-shadow-points@anticipating-shadow-points` is correct — it's `<plugin-name>@<marketplace-name>`, both happen to be the same string because the repo self-hosts its marketplace. The doubled-up appearance is visual only.

</details>

---

## Whitepapers

Both whitepapers are published under **Codex Hash Research Laboratory Whitepaper Series · 2026** with permanent Zenodo concept DOI [10.5281/zenodo.20276631](https://doi.org/10.5281/zenodo.20276631) — always resolves to the latest version.

| # | Title | PDF | Markdown source |
|---|---|---|---|
| 1 | *ASP: An Operational Pre-Mortem Skill for LLM Coding Agents — An Experience Report* | [`paper/asp-preprint.pdf`](paper/asp-preprint.pdf) | [`paper/asp-preprint.md`](paper/asp-preprint.md) |
| 2 | *Graceful Refusals as Silent Successes: A Pre-Registered Protocol for Characterising `claude -p` Exit-Code Semantics* | [`paper/iron-law-11.pdf`](paper/iron-law-11.pdf) | [`paper/iron-law-11.md`](paper/iron-law-11.md) |

The Markdown sources are canonical; the PDFs are the published artefacts. Both are also attached to the [GitHub Release v1.0.0](https://github.com/ulissesflores/anticipating-shadow-points/releases/tag/v1.0.0) and archived under the Zenodo DOI for permanent citation. To rebuild the PDFs from source, see [CONTRIBUTING.md § Rebuilding the whitepaper PDFs](CONTRIBUTING.md#rebuilding-the-whitepaper-pdfs).

---

## Deeper reading

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — 10-part SOTA design document: academic background, v1→v5 architectural journey, empirical discoveries (including Iron Law 11 finding), derivation of all 12 Iron Laws, open questions.
- **[5 structured evals](skills/anticipating-shadow-points/evals/)** — domain-specific shadow-point tests covering Supabase migration, edge function deploy, util refactor, RLS policy change, cron skill conflict.
- **[12 Iron Laws](skills/anticipating-shadow-points/SKILL.md)** — non-negotiable runtime discipline.

---

## Community

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — how to contribute (code, docs, evals, translations).
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — Contributor Covenant 2.1.
- **[SECURITY.md](SECURITY.md)** — vulnerability disclosure policy.
- **[CHANGELOG.md](CHANGELOG.md)** — release history.
- **[AGENTS.md](AGENTS.md)** — rules for AI agents editing this repository.

Native-speaker review of ES/IT/HE translations welcomed via PR.

---

## Author

**[Ulisses Flores](https://ulissesflores.com)** — CTO & Chief Researcher at Codex Hash Research Laboratory · MSc AI candidate, American Global Tech University · São Paulo, Brazil · [@ulissesflores on GitHub](https://github.com/ulissesflores)

Domain focus: Quantitative Finance & Web3 · Hardware & IoT · AI & Data Science. The multilingual docs reflect the maintainer's working languages — Portuguese (native), English/Spanish (fluent), Italian (conversational), Hebrew (academic reading).

Research synthesis, initial drafting, and verification scripts produced in collaboration with Claude (Anthropic, Opus 4.7) under explicit human-in-the-loop direction. See [AUTHORS](AUTHORS) and [ARCHITECTURE.md](docs/ARCHITECTURE.md) Parts 5–6 for the contribution model.

---

## Cite this work

If you use ASP in published work, an evaluation, or a production deployment, please cite via [CITATION.cff](CITATION.cff) — GitHub's "Cite this repository" button uses this file automatically. The four methodological references (Klein, MAST, Plan-and-Act, Reflexion) are listed there and should be cited alongside ASP when discussing the methodology.

---

## License

MIT — see [LICENSE](LICENSE). Acknowledgements: ASP integrates patterns from [obra/superpowers](https://github.com/obra/superpowers) and aligns with the [agentskills.io](https://agentskills.io) open standard.
