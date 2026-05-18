---
title: Home
layout: default
nav_order: 1
description: "ASP — Anticipating Shadow Points. Lift shadow-point coverage from 47% to 100% on non-trivial Claude Code tasks. Pre-mortem, MAST 14-mode, independent validator, claude -p /goal subprocess kernel."
permalink: /
---

<div align="center" markdown="1">

# Ship ambitious work without missing the obvious.
{: .fs-9 .text-center }

ASP is a Claude Code skill that lifts shadow-point coverage from **47% to 100%** on non-trivial tasks — through forced pre-mortem, independent validator, and `claude -p /goal` subprocess execution.
{: .fs-5 .fw-300 .text-center }

[Install in 30 seconds →](#get-started){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/ulissesflores/anticipating-shadow-points){: .btn .fs-5 .mb-4 .mb-md-0 .mr-2 }
[See the proof ↓](#proof){: .btn .fs-5 .mb-4 .mb-md-0 }

</div>

---

<a id="proof"></a>

## The proof

<table style="width: 100%; border: 0; text-align: center; margin: 2em 0;">
<tr style="border: 0;">
<td style="border: 0; padding: 1em;">
<div style="font-size: 3em; font-weight: 700; color: #2ea44f;">47% → 100%</div>
<div style="font-size: 0.95em; opacity: 0.7;">shadow-point coverage<br>(baseline vs. with ASP)</div>
</td>
<td style="border: 0; padding: 1em;">
<div style="font-size: 3em; font-weight: 700; color: #0969da;">12</div>
<div style="font-size: 0.95em; opacity: 0.7;">non-negotiable Iron Laws<br>enforced at runtime</div>
</td>
<td style="border: 0; padding: 1em;">
<div style="font-size: 3em; font-weight: 700; color: #8250df;">5</div>
<div style="font-size: 0.95em; opacity: 0.7;">structured evals<br>across real domains</div>
</td>
</tr>
</table>

### Same task, two outcomes

Real subagent dispatches from the 2026-05-17 RED/GREEN baseline. Task: *"Add a NOT NULL column `tier` (default 'free') to `user_profiles`. Table has 1M rows in production."*

<table style="width: 100%; border-collapse: collapse;">
<tr>
<td style="width: 50%; vertical-align: top; padding: 1em; border: 1px solid #d0d7de; background: #fff8f8;">
<strong style="color: #cf222e;">❌ Without ASP — baseline agent</strong>
<pre><code>ALTER TABLE user_profiles
  ADD COLUMN tier text
  NOT NULL DEFAULT 'free';

CREATE INDEX CONCURRENTLY
  idx_user_profiles_tier
  ON user_profiles (tier);
</code></pre>
<em>~60% shadow-point coverage.</em> Misses: replica lag, app deploy ordering, monitoring spike, trigger interaction, foreign key cascade.
</td>
<td style="width: 50%; vertical-align: top; padding: 1em; border: 1px solid #d0d7de; background: #f1f8f4;">
<strong style="color: #2ea44f;">✅ With ASP — same agent, same task</strong>
<pre><code>Pre-mortem (30 days out):
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
</code></pre>
<em>100% shadow-point coverage.</em> Each surfaces a mitigation before any SQL runs.
</td>
</tr>
</table>

<div class="text-center" markdown="1">
*Built on proven methodology · [Klein pre-mortem](https://hbr.org/2007/09/performing-a-project-premortem) · [Berkeley MAST 14-mode](https://arxiv.org/abs/2503.13657) · [Plan-and-Act](https://arxiv.org/abs/2503.09572) · Reflexion · empirically validated 2026-05-17*
{: .fs-3 .fw-300 }
</div>

---

## What ASP does

<table style="width: 100%; border-collapse: collapse;">
<tr>
<td style="width: 50%; vertical-align: top; padding: 1.2em; border: 1px solid #d0d7de;">
<h3 style="margin-top: 0;">🎯 Pre-mortem before code</h3>
<p>"Imagine the failure. Now describe why." Prospective hindsight — Mitchell, Russo & Pennington (1989) showed it generates ~30% more reasons than imagining the same event as merely possible; Klein (2007, HBR) operationalized it as the pre-mortem. ASP runs it on every non-trivial task.</p>
</td>
<td style="width: 50%; vertical-align: top; padding: 1.2em; border: 1px solid #d0d7de;">
<h3 style="margin-top: 0;">🔍 MAST 14-mode checklist</h3>
<p>Berkeley's failure taxonomy forces coverage of less-obvious categories — time/timezone, observability, op-ex, contract drift — that free-form pre-mortem clusters away from.</p>
</td>
</tr>
<tr>
<td style="width: 50%; vertical-align: top; padding: 1.2em; border: 1px solid #d0d7de;">
<h3 style="margin-top: 0;">🛡️ Independent validator</h3>
<p>A fresh-prompt subagent audits the plan before execution. Self-critique fails on high-confidence hallucinations; prompt isolation breaks that collusion. Iron Law 2.</p>
</td>
<td style="width: 50%; vertical-align: top; padding: 1.2em; border: 1px solid #d0d7de;">
<h3 style="margin-top: 0;">⚡ <code>claude -p /goal</code> kernel</h3>
<p>Spawns Anthropic's official worker/evaluator kernel as a subprocess. Empirically validated 2026-05-17. Iron Law 11: never trust <code>$?</code> — parse JSON.</p>
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

<a id="get-started"></a>

## Get started

```bash
claude plugin marketplace add ulissesflores/anticipating-shadow-points
claude plugin install anticipating-shadow-points@anticipating-shadow-points
```

Invoke `/anticipating-shadow-points:asp <task>` in any Claude Code session. Two more install paths (dev mode `--plugin-dir`, standalone `install.sh` for bare `/asp`) are in the [GitHub README](https://github.com/ulissesflores/anticipating-shadow-points#quick-start).

**Requirements**: Claude Code 2.1.139+, `bash`, `jq`.

---

## When to reach for ASP

<table style="width: 100%; border-collapse: collapse;">
<tr>
<th style="text-align: left; padding: 0.8em; background: #f1f8f4; border: 1px solid #d0d7de;">✅ Use ASP for</th>
<th style="text-align: left; padding: 0.8em; background: #fff8f8; border: 1px solid #d0d7de;">❌ Skip ASP for</th>
</tr>
<tr>
<td style="vertical-align: top; padding: 0.8em; border: 1px solid #d0d7de;">
Features touching data or shared state<br>
Migrations (schema, dependency, API)<br>
Refactors across many files<br>
Deploys with external dependencies<br>
Architecture decisions<br>
Root-cause debug investigations
</td>
<td style="vertical-align: top; padding: 0.8em; border: 1px solid #d0d7de;">
Typo fixes<br>
Single-line edits<br>
Read-only questions ("what does X do?")<br>
Tasks you can finish in under 5 minutes
</td>
</tr>
</table>

---

<div align="center" markdown="1">

## Ready?

```bash
claude plugin marketplace add ulissesflores/anticipating-shadow-points
claude plugin install anticipating-shadow-points@anticipating-shadow-points
```

[Install now](#get-started){: .btn .btn-primary .fs-5 .mr-2 }
[Star on GitHub ⭐](https://github.com/ulissesflores/anticipating-shadow-points){: .btn .fs-5 }

</div>

---

<div class="text-small" markdown="1" style="opacity: 0.75;">

**Maintainer**: [Ulisses Flores](https://ulissesflores.com) — CTO & Chief Researcher at Codex Hash Ltda · MSc AI candidate · Itupeva, Brazil · [@ulissesflores](https://github.com/ulissesflores)

**Languages**: 🇬🇧 English · 🇪🇸 [Español](docs/README.es) · 🇧🇷 [Português](docs/README.pt) · 🇮🇹 [Italiano](docs/README.it) · 🇮🇱 [עברית](docs/README.he)

**Deep dive**: [ARCHITECTURE.md](docs/ARCHITECTURE) — 10-part SOTA design document (academic background, architectural journey, empirical discoveries, derivation of all 12 Iron Laws).

**Cite this work**: [CITATION.cff](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CITATION.cff) · **Community**: [Contributing](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CONTRIBUTING.md) · [Code of Conduct](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CODE_OF_CONDUCT.md) · [Security](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/SECURITY.md) · [Changelog](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CHANGELOG.md)

**License**: MIT

</div>
