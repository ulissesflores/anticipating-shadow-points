# ASP Papers — Two-Document Track

This directory holds two independent, cross-referencing documents.

## The two papers

### Paper 1 — Experience report on the system

**`asp-preprint.md`** — *ASP: An Operational Pre-Mortem Skill for LLM
Coding Agents — An Experience Report.*

A system-description / experience-report paper. ~5,000 words. Documents
ASP as a 13-phase Claude Code skill, with its 12 operational constraints
("Iron Laws"), its three-role separation (planner / validator / worker),
its deployment as an open-source plugin, and preliminary observations
from five engineering evaluations (n=8 subagent dispatches,
author-adjudicated, single model).

The tone is honest about scale. The empirical claim (≈47% → ≈100%
shadow-point coverage) is reported as a preliminary observation, not as
a benchmark result. The deterministic adjudicator shipped with the
companion `benchmark/` package allows any reviewer to re-adjudicate the
recorded transcripts without trusting the author.

**Target venues**: NeurIPS LLM-agents workshop, ICLR agents workshop,
AAAI agents track, EMNLP systems demonstration track.

### Paper 2 — Pre-registered protocol on the empirical finding

**`iron-law-11.md`** — *Graceful Refusals as Silent Successes: A
Pre-Registered Protocol for Characterising `claude -p` Exit-Code
Semantics.*

A focused tooling paper, pre-registered before data collection.
~3,300 words at registration; will extend to ~5,000 once the empirical
addendum (N=50 confusion matrix) is appended. Documents an
observation made during Paper 1's evaluation battery (the `claude -p`
non-interactive runner returns exit code 0 even when the agent
gracefully refuses the goal), specifies a rigorous N=50 protocol to
characterise the behaviour across four refusal categories, commits the
analysis plan (precision, recall, F1, exact-binomial 95% CI), and
locks falsification criteria before data collection.

The empirical fill-in is honest follow-up work that can be performed
in ~2-4 hours of careful test design plus ~$2-5 of inference. The
pre-registration is what is publishable now; the addendum publishes
when the data are in.

**Target venues**: NeurIPS LLM-tooling workshop, EMNLP system
demonstrations, arXiv as a tooling note, or as a short paper at the
SoLaR (Safety, Logic and Reliability) workshop.

## How they cross-reference

| Paper 1 references Paper 2 | Paper 2 references Paper 1 |
|---|---|
| §1 contributions — the Iron Law 11 finding is reported in companion paper | §1 introduction — the observation arose during Paper 1's evaluation battery |
| §3.3 Table 2 — Iron Law 11 derivation cites Flores (2026b) | §1.2 motivation — extracts a single observation worth independent characterisation |
| §5.3 — short summary, full characterisation in companion paper | §8 acknowledgments — original observation context |
| §6 lessons learned — the design implication motivating Iron Laws 11/12 | — |

The pattern is intentional: one paper documents the *system*, the
other paper documents an *empirical finding* the system surfaced. The
findings paper is publishable independently of the system paper.

## Why this two-paper structure

A single 6,000-word preprint trying to be both a system description
*and* a benchmark paper is structurally dishonest at the current
empirical scale: too much related work for the size of the
empirics, and the standout novel finding (the exit-code behaviour)
gets buried inside a section that also has to discuss MAST and
pre-mortem methodology.

Splitting solves both problems. Paper 1 becomes an honest experience
report at appropriate length. Paper 2 becomes a focused, independently
publishable tooling note that can be expanded with empirical data
when the run completes.

The pre-registration on Paper 2 is what makes the split scientifically
defensible: the protocol is publishable now precisely because we
commit the analysis plan before observing the data.

## Files in this directory

| File | Purpose | Status |
|---|---|---|
| `asp-preprint.md` | **Paper 1** — experience report (canonical source) | ✓ current |
| `iron-law-11.md` | **Paper 2** — pre-registered protocol (canonical source) | ✓ committed; addendum pending |
| `asp-preprint.tex` | LaTeX of Paper 1 | ⚠️ outdated; pending re-sync from MD |
| `references.bib` | BibTeX bibliography (used by .tex) | ⚠️ outdated; pending sync |
| `README.md` | This file | ✓ current |

## Building PDFs (for offline review)

arXiv now accepts Markdown submissions for `cs.AI`; the recommended
path is to submit the MD directly. For offline PDF generation:

```bash
# Paper 1
pandoc asp-preprint.md \
  -o asp-preprint.pdf \
  --pdf-engine=xelatex

# Paper 2
pandoc iron-law-11.md \
  -o iron-law-11.pdf \
  --pdf-engine=xelatex
```

## Licensing

Paper text is **CC BY 4.0** (Creative Commons Attribution 4.0
International). When reusing methodology figures or significant
passages, please cite:

> Flores, U. (2026a). *ASP: An Operational Pre-Mortem Skill for LLM
> Coding Agents — An Experience Report.* Independent research preprint.
> https://github.com/ulissesflores/anticipating-shadow-points

> Flores, U. (2026b). *Graceful Refusals as Silent Successes: A
> Pre-Registered Protocol for Characterising `claude -p` Exit-Code
> Semantics.* Independent research preprint.
> https://github.com/ulissesflores/anticipating-shadow-points

The companion software (ASP skill, `benchmark/` package) is MIT.
