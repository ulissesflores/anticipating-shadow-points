# Twitter / X thread — ASP launch

**Posting time**: Tuesday or Wednesday, 14:00 UTC (10:00 EST / 09:00 BRT). That window catches both the US morning and the European afternoon for tech/AI accounts.

**Length**: 12 tweets. Each numbered. Keep under the 280-char ceiling per tweet. Add the figure to tweet 4.

**Figures to attach** (prepare in advance):
- Tweet 4 attachment: a simple bar chart showing 47% → 100% coverage on the 5 evals (or the RED/GREEN before/after panel from the Pages landing — screenshot is fine).
- Tweet 7 attachment (optional): a single screenshot of the `jq` parsing recipe from `claude-p-goal-runner.md`.

---

## Thread (paste 1 tweet at a time ↓)

### Tweet 1 — hook

```
Most LLM agents miss the obvious. I built a Claude Code skill that turns ~47% shadow-point coverage into ~100% on non-trivial engineering tasks.

Repo: github.com/ulissesflores/anticipating-shadow-points
Pages: ulissesflores.github.io/anticipating-shadow-points

Thread 🧵 on the method + an empirical finding
```

### Tweet 2 — the problem

```
2/ The dominant failure mode of LLM coding agents isn't "wrong code". It's "right code for the wrong envelope of risk".

Free-form pre-mortem clusters on obvious categories (data, integration). Time/timezone, observability, contract drift, op-ex slip through.
```

### Tweet 3 — the method

```
3/ We combine Klein's pre-mortem (HBR 1998) with Berkeley's MAST 14-mode failure taxonomy (arXiv 2503.13657).

MAST is the load-bearing component. It forces enumeration of less-salient failure categories that free-form pre-mortem misses.
```

### Tweet 4 — the number (attach figure)

```
4/ On 5 structured evals — schema migration, multi-file refactor, edge function deploy, RLS policy change, cron scheduling — baseline coverage rose from ~47% to ~100% with ASP.

Same model. Same subagent substrate. Only the protocol changed.

[attach figure]
```

### Tweet 5 — validator discipline

```
5/ Iron Law 2: validator subagent runs in a SEPARATE prompt with only the planner's artifacts.

Why? Huang+24 (ICLR), Tyen+24 (localization), Zheng+23 (LLM-judge self-enhancement bias) — three converging findings that same-context self-critique misses what the worker is most confident about.
```

### Tweet 6 — execution kernel

```
6/ Phase 9 spawns `claude -p /goal` as a subprocess — Anthropic's official worker/evaluator built-in (released 2026-05-12).

Empirically validated on 2026-05-17. Worker iterates; evaluator decides done. No reinvented loops.
```

### Tweet 7 — the empirical finding (attach jq snippet)

```
7/ Found in testing & worth knowing for anyone wrapping `claude -p`:

It returns exit 0 even when the agent gracefully REFUSES the goal.

`claude -p "<goal>" || handle_error` will misroute refusals as successes.

Iron Law 11: parse JSON, never trust $?.

[attach jq pattern]
```

### Tweet 8 — the safe pattern

```
8/ The safe pattern is to require `--output-format json` and parse `is_error`, `terminal_reason`, `stop_reason`:

```
RESULT=$(claude -p ... --output-format json)
IS_ERR=$(echo "$RESULT" | jq -r '.is_error')
STOP=$(echo "$RESULT" | jq -r '.terminal_reason')
```

Iron Law 12 in the deployed skill.
```

### Tweet 9 — reproducibility

```
9/ Full reproducibility shipped: 5 structured evals, 3 RED/GREEN baseline scenarios with subagent IDs, advisor reviews, validator transcripts.

10-part SOTA design doc in docs/ARCHITECTURE.md. LaTeX preprint source under paper/.

MIT licensed.
```

### Tweet 10 — transparency

```
10/ Built with Claude (Anthropic Opus 4.7) under explicit human-in-the-loop direction. Methodology decisions & empirical evaluation by me; drafting / synthesis collaborative.

Collaboration model documented openly in docs/ARCHITECTURE.md Parts 5-6.
```

### Tweet 11 — limitations

```
11/ Honest scope:

- n=8 subagent dispatches across 5 domains (preliminary, not robust evaluation)
- Single-model (Claude Opus 4.7); cross-model transfer unverified
- 3 of 5 translations AI-assisted, awaiting native review
- Validated on Claude Code 2.1.143
```

### Tweet 12 — try it

```
12/ Try it:

```
claude plugin marketplace add ulissesflores/anticipating-shadow-points
claude plugin install anticipating-shadow-points@anticipating-shadow-points
```

Submitted to the Anthropic plugin directory; in review. Feedback + critique welcomed via issues or @ here.
```

---

## Canned responses for replies

Anticipate three categories of reply:

**(a) Methodology critique** ("isn't this just dressed-up X?"):
> Fair question. The contribution isn't any single component — Klein, MAST, Plan-and-Act, Reflexion all exist independently. What's new is the integration into a runtime-enforced protocol with the per-task contract and the empirical Iron Law 11 finding. Happy to discuss specific components if you want to drill in. Methodology is in docs/ARCHITECTURE.md Parts 1-2.

**(b) Reproducibility ask** ("how do I run the evals?"):
> Repo has the full battery at `tests/`. Run `./scripts/verify.sh --pre-install` to check the skill structure, then look at `tests/baseline-pressure-tests.md` for the RED/GREEN methodology. Subagent IDs are recorded for verbatim re-running.

**(c) Cross-tool curiosity** ("does this work on Cursor / Codex / Gemini CLI?"):
> Not tested on those. The methodology (pre-mortem + MAST + validator isolation) is model-and-CLI-independent. The execution kernel (Phase 9 `claude -p /goal` subprocess) is Claude Code-specific. Open-source port to other tools would be welcome contribution.
