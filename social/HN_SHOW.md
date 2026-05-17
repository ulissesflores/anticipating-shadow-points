# Hacker News — Show HN submission

**Posting time**: Tuesday or Wednesday, 11:00 UTC (07:00 EST / 06:00 EDT in summer / 04:00 PST). That hits the start of US east-coast workday, peak HN engagement.

**Submission URL**: https://news.ycombinator.com/submit

**Type**: "Show HN" (use the title prefix exactly as shown below).

---

## Title (≤80 chars)

```
Show HN: ASP – Anticipating Shadow Points, a Claude Code skill for pre-mortem
```

(75 chars, under the soft ceiling. Drops the colon and slash for clean parsing.)

## URL field

```
https://github.com/ulissesflores/anticipating-shadow-points
```

(HN convention: the repo URL, not the docs site. Engaged readers will click through to Pages from the repo README anyway.)

## Text body (≤500 chars recommended; this is ~480)

```
I built a Claude Code skill that combines Klein's pre-mortem with Berkeley's MAST 14-mode failure taxonomy. On 5 structured engineering evals (schema migrations, multi-file refactors, edge-function deploys, RLS policy changes, cron scheduling), baseline shadow-point coverage rose from ~47% to ~100%. Same model, same subagent substrate, only the protocol changed.

Most interesting finding for HN readers wrapping `claude -p`: it returns exit code 0 even when the agent gracefully refuses the goal. A naive `claude -p ... || handle_error` will silently misroute refusals as successes. The safe pattern requires `--output-format json` and parsing `is_error`, `terminal_reason`, `stop_reason`. Iron Law 11 in the deployed skill; canonical recipe in `skills/anticipating-shadow-points/claude-p-goal-runner.md`.

Open source, MIT, multilingual docs (EN/ES/PT/IT/HE). LaTeX preprint source in `paper/`. Full RED/GREEN test battery in `tests/`. Submitted to the official Anthropic plugin directory; in review.

Built with Claude Opus 4.7 under explicit human-in-the-loop direction; collaboration model documented in `docs/ARCHITECTURE.md`.

Critique welcomed.
```

---

## Canned responses

HN comments tend to fall into a few patterns. Prepare these so you can reply within the first 60 minutes (engagement-critical window).

### "Isn't this just X with extra steps?"

> Honest reading. The components individually (Klein, MAST, Plan-and-Act, Reflexion) all exist in prior work. What's new is the integration into a runtime-enforced 13-phase protocol with the per-step ACCEPTANCE/FALSIFICATION schema, and the empirical Iron Law 11 finding (claude -p exit-code semantics on graceful refusal). If you think the integration is trivial, the empirical battery is in `tests/` — happy to discuss what's load-bearing vs what's decorative.

### "How is this measured / what's the eval methodology?"

> Five structured evals in `skills/anticipating-shadow-points/evals/`, each with an INPUT (task statement), an EXPECTED list of ≥8 shadow points a senior engineer would surface, and an ACCEPTANCE threshold of ≥80% coverage. RED condition: subagent dispatched without the skill loaded, told to respond as a senior engineer. GREEN condition: same subagent type, same input phrasing, with ASP discipline injected. n=8 dispatches total. Adjudication was paraphrase-tolerant but not blind — the same researcher who designed the protocol authored the expected lists. Flagged as a limitation in the LaTeX preprint.

### "n=8 is tiny"

> Agreed. The numbers demonstrate the existence and approximate magnitude of the effect on the chosen domains; they are not powered to estimate confidence intervals. The preprint flags this as a top-of-list limitation. Community-contributed evals from additional domains are explicitly invited via the issue template.

### "Why is everything Klein/MAST jargon?"

> The repo's user-facing copy (Pages landing, README) deliberately avoids the jargon. The academic citations are in `docs/ARCHITECTURE.md` (methodology) and the LaTeX preprint (`paper/asp-preprint.tex`). The README/Pages talk about "RLS policy gaps", "replica lag", "rate-limit issues" — concrete dev pain.

### "AI wrote this?"

> Explicit collaboration with Claude Opus 4.7 under human-in-the-loop direction. Methodology decisions and empirical evaluation were performed by me; drafting and synthesis were collaborative. Collaboration model documented openly in `docs/ARCHITECTURE.md` Parts 5–6. The Iron Law 11 finding came from a test battery I designed and ran on 2026-05-17.

### "Cross-CLI?"

> Not tested on Cursor / Codex / Gemini CLI. The pre-mortem + MAST + validator-isolation methodology is model-and-CLI-independent in principle. The execution kernel (Phase 9 `claude -p /goal` subprocess) is Claude Code-specific. Open-source port to other tools would be a welcome contribution; the methodology core is in `methodology.md` and `mast-checklist.md`.

### "How is this distributed?"

> Three install paths: plugin marketplace (recommended; one-step via `claude plugin marketplace add`); dev mode `--plugin-dir`; standalone `./scripts/install.sh` for bare `/asp` invocation without plugin namespacing. The repo also self-hosts a `.claude-plugin/marketplace.json` so it can be added as a marketplace directly.

---

## Anti-pattern to avoid in HN replies

Do **not** respond defensively to harsh critique. The HN voting culture rewards substantive engagement with criticism, not deflection. If a comment finds a real flaw, acknowledge it, fix it in the repo within 24-48h, and reference the fix in a follow-up reply. That pattern earns more karma and more long-term trust than defending the original.
