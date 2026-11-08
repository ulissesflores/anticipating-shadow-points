---
title: Home
layout: default
nav_order: 1
description: "ASP — Anticipating Shadow Points. A Claude Code plugin that runs a pre-mortem before code is written, plus a replication layer that re-derives every measured number in its two papers under a SHA-256 seal."
permalink: /
---

<div align="center" markdown="1">

# Ship ambitious work without missing the obvious.
{: .fs-9 .text-center }

ASP is a Claude Code skill that surfaces the failure modes a senior engineer would catch in a pre-mortem — *before* any code is written — through a forced MAST-14 pre-mortem, a prompt-isolated independent validator, and a `claude -p /goal` subprocess executor.
{: .fs-5 .fw-300 .text-center }

[Install in 30 seconds →](#get-started){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/ulissesflores/anticipating-shadow-points){: .btn .fs-5 .mb-4 .mb-md-0 .mr-2 }
[What is measured ↓](#proof){: .btn .fs-5 .mb-4 .mb-md-0 }

</div>

---

<a id="proof"></a>

## Evidence — what is measured, and what is not

**Measured (Iron Law 11).** `claude -p` exits 0 when the agent gracefully declines. On 50 refusal-provoking prompts (Claude Code 2.1.200, July 2026), 24 exited 0, all with `stop_reason: end_turn`, and 12 to 20 of them were declines: 24% to 40% of the suite depending on how a decline is counted. Every number computed from the data is re-derived from committed files by `python run_all.py` and sealed under a SHA-256 chain hash. [Paper](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/paper/graceful-refusals.md).

![A recorded July 2026 trial: the agent refuses, exit code is 0, stop_reason is end_turn](assets/demo/exit-code.gif)

**Not yet measured: whether ASP improves plans.** The author observed it without blinding on five tasks in May 2026, and those transcripts were not preserved. An "80% vs 4%" figure in earlier versions came from scoring fixtures the author wrote to test the matcher, not model outputs, and is withdrawn as evidence. The first real benchmark is [pre-specified](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/PREREGISTRATION.md) with expected lists written blind by independent engineers.

![run_all.py re-derives every published number, runs the tests and verifies the SHA-256 seal](assets/demo/replicate.gif)

---

## What ASP does

<table style="width: 100%; border-collapse: collapse;">
<tr>
<td style="width: 50%; vertical-align: top; padding: 1.2em; border: 1px solid #d0d7de;">
<h3 style="margin-top: 0;">🎯 Pre-mortem before code</h3>
<p>"Imagine the failure. Now describe why." Prospective hindsight (Mitchell, Russo & Pennington, 1989), which Klein (2007, HBR) summarises as about 30% better at identifying reasons for a future failure and operationalized as the pre-mortem. ASP runs it on every non-trivial task.</p>
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
<p>Hands execution to a <code>claude -p</code> child that runs under your own permission settings; the skill never widens them. Iron Law 11: never trust <code>$?</code> — parse the JSON.</p>
</td>
</tr>
</table>

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

**Maintainer**: [Carlos Ulisses Flores](https://ulissesflores.com) — CTO & Chief Researcher at Codex Hash Research Laboratory · São Paulo, Brazil · [ORCID `0000-0002-6034-7765`](https://orcid.org/0000-0002-6034-7765) · [Lattes `6905246706890561`](http://lattes.cnpq.br/6905246706890561) · [@ulissesflores](https://github.com/ulissesflores)

**Languages**: 🇬🇧 English · 🇧🇷 [Português](docs/README.pt) · 🇪🇸 [Español](docs/README.es) · 🇮🇹 [Italiano](docs/README.it) · 🇮🇱 [עברית](docs/README.he)

**Deep dive**: [ARCHITECTURE.md](docs/ARCHITECTURE) — 10-part SOTA design document (academic background, architectural journey, empirical discoveries, derivation of all 12 Iron Laws).

**Cite this work**: [CITATION.cff](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CITATION.cff) · **Community**: [Contributing](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CONTRIBUTING.md) · [Code of Conduct](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CODE_OF_CONDUCT.md) · [Security](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/SECURITY.md) · [Changelog](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/CHANGELOG.md)

**License**: code MIT · papers, figures and data CC BY 4.0

</div>
