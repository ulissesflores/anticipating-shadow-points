# r/MachineLearning submission

**Subreddit**: [r/MachineLearning](https://www.reddit.com/r/MachineLearning/)

**Required tag**: `[R]` (Research) — appropriate because there is an empirical contribution and an academic preprint. Use `[P]` (Project) if you want lighter scrutiny, but the rigour level of the post should still match `[R]` standards.

**Posting time**: Tuesday or Wednesday morning UTC. Avoid weekends (lower engagement) and Mondays (overloaded). r/ML is global; 13:00 UTC is reasonable.

**Cross-post to**: r/ClaudeAI (welcome but lower rigour bar), r/programming (only if framing the dev-tool angle).

---

## Title

```
[R] Anticipating Shadow Points: a pre-mortem protocol for LLM agents (47% → 100% coverage, with a claude -p exit-code finding)
```

(141 chars; r/ML title soft limit is 300, but shorter titles convert better.)

## Submission body

```
**Paper (preprint, LaTeX source in repo)**: https://github.com/ulissesflores/anticipating-shadow-points/blob/main/paper/asp-preprint.tex
**Code (MIT)**: https://github.com/ulissesflores/anticipating-shadow-points
**Architecture doc (10 parts)**: https://github.com/ulissesflores/anticipating-shadow-points/blob/main/docs/ARCHITECTURE.md

**TL;DR**

We present ASP, a 13-phase planning protocol for LLM coding agents that operationalizes Klein's pre-mortem (HBR 1998) with the Berkeley MAST 14-mode failure taxonomy (arXiv 2503.13657), Plan-and-Act separation (arXiv 2503.09572), and Reflexion-style validator subagents (Shinn et al. 2023) under strict prompt isolation. On a battery of five structured engineering evaluations (database migration, multi-file refactor, edge-function deploy, RLS policy change, cron scheduling), baseline shadow-point coverage rises from approximately 47% to approximately 100%. The dominant load-bearing component is MAST 14-mode forced enumeration, which closes the gap on less-obvious failure categories (time/timezone, observability, operational excellence, contract drift) that free-form pre-mortem clusters away from.

**Notable finding (Section 5 of the preprint)**

`claude -p` returns exit code 0 even when the agent gracefully refuses the requested goal. Inspection of the JSON output reveals `is_error: false`, `terminal_reason: end_turn` — the harness reports a successful conversation end despite the agent semantically refusing the goal. A naive shell wrapper of the form `claude -p "<goal>" || handle_error` will misroute refusals as successes in production. We codify the safe parsing pattern (require `--output-format json`, parse `is_error` + `terminal_reason` + `stop_reason`) as Iron Laws 11 and 12 in the deployed skill.

This is the only finding I would call distinctly novel — and it has been empirically validated on Claude Code 2.1.143. Anyone wrapping `claude -p` in a pipeline should know about it.

**Methodology**

Twelve "Iron Laws" enforced at runtime as non-negotiable invariants, each mapped to a published source or empirical finding (Table 2 in the preprint). The micro-TODO contract emitted at Phase 8 carries PRE/ACT/POST/ACCEPTANCE/FALSIFICATION fields per step, making the task list audit-able.

**Honest limitations**

- n=8 subagent dispatches across 5 evaluation domains. Sufficient to demonstrate the magnitude of the effect; not powered for confidence intervals.
- Same-model (Claude Opus 4.7) across RED and GREEN conditions. Cross-model transfer is hypothesised but unverified.
- Adjudication is paraphrase-tolerant but not blind.
- The `claude -p` exit-code finding is specific to version 2.1.143; future versions may change behaviour.
- 3 of 5 documentation translations are AI-assisted, pending native-speaker review.

**Reproducibility**

Full RED/GREEN test battery, validator transcripts, advisor reviews, and probe documentation are shipped in `tests/`. Three install paths (plugin marketplace, `--plugin-dir` dev mode, standalone `install.sh`).

**Transparency**

The research was conducted in explicit human-in-the-loop collaboration with Claude (Anthropic Opus 4.7), used as an ideation, drafting, and verification partner. Methodology decisions and empirical evaluation were performed by me. The collaboration model is documented openly in `docs/ARCHITECTURE.md` Parts 5–6.

---

Open to methodological critique, blind-adjudication replication, cross-model transfer evaluation, and community-contributed evals from domains beyond the five we shipped. PRs and substantive issues welcome.
```

---

## Anticipated critique vectors

r/ML readers will engage on these axes; have answers ready.

### "n=8 is preliminary, calling this empirical is generous"

Agreed. Stated as the top limitation. The numbers demonstrate the existence and approximate magnitude of the effect on the chosen domains; they do not robustly establish generalizability. The post frames this as `[R]` because there *is* an empirical methodology and a finding, not because the evaluation is comprehensive. A follow-up evaluation with independent adjudicators and larger n is on the future-work list.

### "The improvement is from prompt engineering, not from methodology"

Plausible reading. The GREEN condition injects pre-mortem instructions and a MAST checklist; the RED condition does not. One could argue any structured prompting would lift coverage. The interesting question is *which* structured prompting works and how much. Our REFACTOR-phase analysis identifies MAST 14-mode forced enumeration as load-bearing; ablating MAST drops coverage back toward ~50%. This is testable by anyone with the repository.

### "Is the 100% number paraphrase-tolerance artefact?"

The adjudication accepts paraphrase and synonym matches (e.g., "row-level security" == "RLS policy"). Without paraphrase tolerance, coverage of explicit terminology would be lower — but the test is about whether the agent surfaces the *concept*, not whether it produces a specific phrase. We document the adjudication standard explicitly in the eval files.

### "Why not standard agent benchmarks (SWE-bench, etc.)?"

ASP measures pre-mortem coverage, not code correctness. SWE-bench and similar benchmarks measure whether the agent produces patch code that passes hidden tests — they don't measure whether the agent surfaces the failure modes that would arise during deployment. ASP and SWE-bench are orthogonal; combining them in future work would be valuable.

### "How is this different from chain-of-thought?"

CoT is unstructured reasoning. ASP forces enumeration over a fixed taxonomy (MAST 14-mode) and structures the output into a contractual task list with acceptance tests. The difference is empirical (the coverage delta) and operational (the runtime contract is audit-able post-hoc, CoT is not).
