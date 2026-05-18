# LinkedIn long-form article — ASP launch

**Suggested title**: *Anticipating Shadow Points: A pre-mortem protocol for LLM agents (and an empirical finding worth knowing)*

**Suggested cover image**: the RED → GREEN coverage bar chart (47% → 100%). Generate one in your tool of choice or use the table from the Pages landing.

**Hashtags** (4–6, end of post): `#ClaudeCode` `#LLMAgents` `#AgenticAI` `#PreMortem` `#OpenSource` `#AIResearch`

---

## Body (paste from here ↓)

Most LLM agents writing production code do not fail by producing *wrong* code. They fail by producing *right* code for the *wrong* envelope of risk — code that compiles, passes its narrow tests, and ships, but is missing the steps a senior engineer with domain context would have surfaced in a structured pre-mortem.

I have spent the last several days building and validating **Anticipating Shadow Points (ASP)** — a Claude Code skill that operationalizes pre-mortem as a runtime discipline. This article is the research-release writeup.

### The headline number

On a battery of five structured engineering evaluations (production schema migration, multi-file utility refactor, edge-function deploy with external rate limit, row-level-security policy change, recurring background job scheduling), baseline shadow-point coverage rose from approximately **47%** without ASP to approximately **100%** with ASP loaded. Same model, same subagent substrate, same input phrasing — the only difference was the protocol being applied.

The full RED/GREEN test artefacts are in the repository, with subagent identifiers for side-by-side comparison.

### The methodology, in plain English

ASP combines four ideas, each with its own published lineage, into a single runtime protocol:

1. **Pre-mortem — Mitchell, Russo, Pennington (1989) and Klein (2007)**. Before any code is written, the agent is forced to imagine the project has failed and enumerate concrete causes. Mitchell, Russo, and Pennington (1989, *Journal of Behavioral Decision Making* 2(1), 25–38) empirically demonstrated that imagining a future event as already-occurred (certainty) generates approximately 30% more reasons than imagining the same event as merely possible. Klein (2007, *Harvard Business Review*) operationalized the finding as the project-team "pre-mortem". ASP runs this as Phase 2 step 1.

2. **Berkeley's MAST 14-mode failure taxonomy** (arXiv 2503.13657, 2025). Free-form pre-mortem suffers strong availability bias — respondents cluster on obvious categories (data, integration) and miss less-salient ones (time/timezone, observability, contract drift, operational excellence). MAST forces per-mode interrogation. In our REFACTOR-phase analysis this is the dominant load-bearing component: removing the MAST checklist drops coverage from ~100% back toward ~50%.

3. **Plan-and-Act separation** (arXiv 2503.09572, 2025). The planning agent is structurally separated from the executing agent. Different cognitive modes, different prompts, different reasoning chains.

4. **Validator with prompt isolation, grounded in three converging primary sources**. (a) Huang et al. (2024, ICLR) show LLMs cannot self-correct reasoning intrinsically; performance sometimes degrades. (b) Tyen et al. (2024) show LLMs cannot *localize* their own reasoning errors but *can* correct given location externally — localization is the bottleneck. (c) Zheng et al. (2023, NeurIPS D&B, LLM-as-a-Judge) document a *self-enhancement bias* where strong-LLM judges over-favor same-family-model outputs. The validator subagent therefore receives only the planner's emitted artefacts (charter, macro plan, deliverables register, shadow-point list) — never the planner's reasoning trail. Codified as Iron Law 2: NO PLAN APPROVAL WITHOUT INDEPENDENT VALIDATOR PASS in a separate prompt.

The protocol is structured as 13 phases (Q&A, parallel research, shadow-point detection, charter, macro plan, validator, internal loop with cap=3, user approval, contractual micro-TODO emission, autonomous execution, per-deliverable sign-off, execution report, optional public release). Twelve Iron Laws are enforced at runtime.

### An empirical finding worth knowing

During the design-validation battery on 2026-05-17, I discovered something about Claude Code 2.1.139's new `/goal` slash command that is not flagged in the release notes and that anyone wrapping `claude -p` in a shell pipeline should be aware of:

**`claude -p` returns exit code 0 even when the agent gracefully refuses the requested goal.**

The test input was an explicitly impossible goal ("implement, test, and deploy a complete PCI-DSS-compliant system in one turn without using tools"). The agent responded by gracefully refusing with a three-paragraph explanation. The process exited with status code 0. Inspection of the JSON output revealed `is_error: false`, `terminal_reason: end_turn` — i.e. the harness reports a successful conversation end despite the agent semantically refusing the goal.

A naive wrapper of the form `claude -p "<goal>" || handle_error` will silently misroute graceful refusals as successes in production. We codified the safe parsing pattern as Iron Laws 11 and 12 in the deployed skill, and the canonical recipe is shipped in `skills/anticipating-shadow-points/claude-p-goal-runner.md`.

This finding is the only one I would call distinctly novel from the work. Everyone wrapping a slash-command-aware LLM CLI in a shell pipeline will hit it eventually; documenting it publicly is small but real value.

### Limitations and honest scope

The empirical battery dispatched eight subagents across five evaluation domains. This is sufficient to demonstrate the existence and magnitude of the coverage effect, but is not powered for confidence-interval estimation. Both RED and GREEN conditions used the same underlying model; cross-model transfer of the discipline is hypothesised but unverified. Adjudication of expected shadow-point lists was performed by the same researcher who designed the protocol — not blind. The documentation is shipped in five languages (English native; Spanish, Portuguese, Italian, Hebrew) and three of the four translations are AI-assisted and await native-speaker review. Specific findings on `claude -p` exit-code semantics (Iron Law 11) were validated on Claude Code 2.1.143; future versions may change the behaviour.

### Distribution and reproducibility

ASP is open source under the MIT licence with three install paths:

- **Plugin marketplace** (recommended): `claude plugin marketplace add ulissesflores/anticipating-shadow-points && claude plugin install anticipating-shadow-points@anticipating-shadow-points`
- **Dev mode**: `claude --plugin-dir ./`
- **Standalone**: `./scripts/install.sh`

The plugin is currently in review for the official Anthropic plugin directory. The full empirical battery, RED/GREEN baselines, validator transcripts, advisor reviews, and the 10-part SOTA design document `docs/ARCHITECTURE.md` are shipped in the repository for reproducibility. A `CITATION.cff` file makes the work formally citable; an arXiv preprint with the methodology is forthcoming (the LaTeX source is also in the repository, under `paper/`).

### Acknowledgments

This research was conducted in explicit human-in-the-loop collaboration with Claude (Anthropic, Opus 4.7), used as an ideation, drafting, and verification partner. Methodology decisions, empirical design, and finalization were performed by me as the human author. I've documented the collaboration model openly in `docs/ARCHITECTURE.md` Parts 5–6 — both because it's the right thing to do and because the 2026 norm in AI/CS research is explicit transparency on AI tooling.

I welcome substantive critique, alternative methodology suggestions, and especially community-contributed evaluations from domains beyond the five we shipped. Open an issue or PR on the repository.

**Repository**: https://github.com/ulissesflores/anticipating-shadow-points
**Documentation**: https://ulissesflores.github.io/anticipating-shadow-points/
**Architecture doc** (10 parts): https://github.com/ulissesflores/anticipating-shadow-points/blob/main/docs/ARCHITECTURE.md
**arXiv preprint** (LaTeX source): https://github.com/ulissesflores/anticipating-shadow-points/tree/main/paper

— Ulisses Flores
CTO & Chief Researcher, Codex Hash Ltda
MSc AI candidate, American Global Tech University
Itupeva, Brazil
