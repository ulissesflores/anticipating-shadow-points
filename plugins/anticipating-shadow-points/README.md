<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/ulissesflores/anticipating-shadow-points/main/assets/brand/banner-dark.svg">
  <img src="https://raw.githubusercontent.com/ulissesflores/anticipating-shadow-points/main/assets/brand/banner-light.svg" width="100%" alt="ASP — Anticipating Shadow Points. Plan before you code.">
</picture>

<h3>A pre-mortem for your coding agent, and a measured test of whether it helps.</h3>

[![Version 2.0.0](https://img.shields.io/badge/version-2.0.0-blue.svg)](.claude-plugin/plugin.json)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20276631.svg)](https://doi.org/10.5281/zenodo.20276631)
[![Markdown only](https://img.shields.io/badge/ships-Markdown%20only-lightgrey.svg)](#what-it-does-on-your-machine)

</div>

**Plan before you code.** ASP is a Claude Code plugin for tasks where a wrong first move is expensive: a migration, a deploy, a permissions change, a refactor across many files, a bug whose cause is not yet known. Before any code is written it makes Claude:

1. research the codebase and the prior art;
2. run a **pre-mortem**: "it is a month from now and this failed; list why", checked against the 14 failure modes of the MAST taxonomy (Cemri et al., NeurIPS 2025);
3. write a plan and have it checked by a **separate subagent** that sees only the plan, not the reasoning that produced it;
4. turn the plan into **tasks with acceptance tests** that you approve;
5. carry it out and sign off each deliverable against its evidence.

## Install

From Claude Code:

```text
/plugin marketplace add ulissesflores/anticipating-shadow-points
/plugin install anticipating-shadow-points@anticipating-shadow-points
```

## Use

```text
/asp <describe the task>
/asp --quick <task>      # no independent check, no separate session (cheapest)
/asp --paranoid <task>   # two independent checks and stricter evaluation
/asp --goal <task>       # opt-in: execute in a separate background session
```

The default is `--standard`. Skip ASP for one-line edits, renames and questions. It costs more turns than a plain request, by design.

## What it does on your machine

- **Ships only Markdown.** No hooks, no MCP servers, no scripts, no binaries, no telemetry. Nothing runs unless you type `/asp` or Claude chooses the skill for a task that fits its description.
- **Optional second session, off by default.** Execution runs in your session. Only with `--goal` does ASP start a separate headless Claude Code session (`claude -p`) to work through the approved plan, and before it does, it tells you so and waits for your OK. That session:
  - runs under **your own permission settings**: ASP passes no permission flag, so anything you have not pre-allowed is denied;
  - uses **your plan or API usage**, capped by a budget (`--max-budget-usd`) and a turn limit that it states up front;
  - writes its scratch files to the plugin's data folder (`~/.claude/plugins/data/…`), which is removed when you uninstall the plugin.
- **Reads its exit status the safe way.** `claude -p` returns exit code 0 even when the agent politely declines a task. ASP reads the JSON result and flags a likely decline instead of trusting `$?`. The measurement behind this rule is the companion paper below.

Privacy: [PRIVACY.md](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/PRIVACY.md). ASP collects nothing.

## What is and isn't known

The pre-mortem and the independent check rest on published evidence: prospective hindsight (Mitchell, Russo & Pennington, 1989), MAST (Cemri et al., 2025), and studies showing that models correct their own reasoning poorly without outside feedback (Huang et al., 2024) but fix an error once told where it is (Tyen et al., 2024). **Measured in a pre-registered study (2026-11):** on six real repositories, this protocol did not find more risks than plain Claude Code asked *"Before planning, list the ways this change could go wrong."*, and that one sentence alone found more than a plain request. Use `--quick` for reversible work, and read the [study](https://github.com/ulissesflores/anticipating-shadow-points/tree/main/benchmark/study-2026-11) before relying on the full protocol.

## Learn more

- Repository and replication package: <https://github.com/ulissesflores/anticipating-shadow-points>
- *ASP: an operational pre-mortem skill for LLM coding agents*, whitepaper: <https://doi.org/10.5281/zenodo.24065969>
- *Graceful refusals as unsignalled failures*, technical note on the `claude -p` exit code: <https://doi.org/10.5281/zenodo.24065935>

Both reports come in English, Portuguese, Spanish and Italian.

## Author

**Carlos Ulisses Flores** — Codex Hash Research Laboratory, São Paulo, Brazil.

[![ORCID](https://img.shields.io/badge/ORCID-0000--0002--6034--7765-a6ce39.svg)](https://orcid.org/0000-0002-6034-7765)
[![Website](https://img.shields.io/badge/web-ulissesflores.com-black.svg)](https://ulissesflores.com)
[![Lattes](https://img.shields.io/badge/Lattes-6905246706890561-blue.svg)](http://lattes.cnpq.br/6905246706890561)

## Citation

Cite the plugin and its replication package by the concept DOI, which always opens the newest release: [10.5281/zenodo.20276631](https://doi.org/10.5281/zenodo.20276631). The two reports have their own DOIs: [10.5281/zenodo.24065969](https://doi.org/10.5281/zenodo.24065969) (how ASP works) and [10.5281/zenodo.24065935](https://doi.org/10.5281/zenodo.24065935) (the `claude -p` exit code). BibTeX is in the [repository README](https://github.com/ulissesflores/anticipating-shadow-points#citation).

## License

MIT. See [LICENSE](LICENSE).
