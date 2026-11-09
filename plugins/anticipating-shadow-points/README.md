# Anticipating Shadow Points (ASP)

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
/asp --no-goal <task>    # plan with ASP, then execute step by step yourself
```

The default is `--standard`. Skip ASP for one-line edits, renames and questions. It costs more turns than a plain request, by design.

## What it does on your machine

- **Ships only Markdown.** No hooks, no MCP servers, no scripts, no binaries, no telemetry. Nothing runs unless you type `/asp` or Claude chooses the skill for a task that fits its description.
- **Optional second session.** In execution, ASP can start a separate headless Claude Code session (`claude -p`) to work through the approved plan. Before it does, it tells you so and waits for your OK. That session:
  - runs under **your own permission settings**: ASP passes no permission flag, so anything you have not pre-allowed is denied;
  - uses **your plan or API usage**, capped by a budget (`--max-budget-usd`) and a turn limit that it states up front;
  - writes its scratch files to the plugin's data folder (`~/.claude/plugins/data/…`), which is removed when you uninstall the plugin.
- **Reads its exit status the safe way.** `claude -p` returns exit code 0 even when the agent politely declines a task. ASP reads the JSON result and flags a likely decline instead of trusting `$?`. The measurement behind this rule is the companion paper below.

Privacy: [PRIVACY.md](https://github.com/ulissesflores/anticipating-shadow-points/blob/main/PRIVACY.md). ASP collects nothing.

## What is and isn't known

The pre-mortem and the independent check rest on published evidence: prospective hindsight (Mitchell, Russo & Pennington, 1989), MAST (Cemri et al., 2025), and studies showing that models correct their own reasoning poorly without outside feedback (Huang et al., 2024) but fix an error once told where it is (Tyen et al., 2024). **Whether ASP itself produces better plans has not been measured yet.** A benchmark is specified in advance in the repository's `PREREGISTRATION.md`.

## Learn more

- Repository, replication package and DOI: <https://github.com/ulissesflores/anticipating-shadow-points>
- *ASP: an operational pre-mortem skill for LLM coding agents* (technical report)
- *Graceful refusals as unsignalled failures* (technical report on the `claude -p` exit code)

Both reports are in the repository's `paper/` folder, with PDF editions in English, Portuguese, Spanish and Italian.

## License

MIT. See [LICENSE](LICENSE). Author: Carlos Ulisses Flores ([ORCID 0000-0002-6034-7765](https://orcid.org/0000-0002-6034-7765)).
