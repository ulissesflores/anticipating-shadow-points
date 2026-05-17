# Personal blog post — `ulissesflores.com`

**Audience**: anyone landing on your personal site — recruiters, prospective collaborators, conference review committees, prospective consulting clients. This is the long-form, brand-consolidating piece. It should read as a research note from a senior practitioner-researcher.

**Length**: 2500–4000 words. Less than the LinkedIn article (which is already long-form) is wasted; more risks losing the reader before the empirical finding.

**Suggested URL slug**: `/research/asp` or `/blog/anticipating-shadow-points` — choose based on how your existing site is organised.

**Suggested cover image**: the 47% → 100% chart with the ASP wordmark. If you have a designer or can spend 30 min in Figma, this is the most valuable visual to produce — it goes on LinkedIn, Twitter, and the blog post simultaneously.

---

## Structure

### 0. Above-the-fold (~80 words)

Hook + value claim + permalink to repo.

```
LLM coding agents now write production code. The dominant failure mode I see in production isn't "wrong code" — it's "right code for the wrong envelope of risk", where the agent misses the obvious failure modes a senior engineer would surface in a pre-mortem.

ASP is a Claude Code skill I built and shipped over the past several days that operationalizes pre-mortem as a runtime discipline. On structured evals, it lifts baseline shadow-point coverage from ~47% to ~100%. This is the research-release writeup.

Code: <repo URL>  ·  Docs: <Pages URL>  ·  Preprint: <arXiv URL>
```

### 1. The problem (~300 words)

A specific scenario where the gap shows up. Use a real engineering task — e.g., the schema migration eval, told as if you'd seen it happen at a previous engagement (without naming any client). The reader should be nodding by the second paragraph.

### 2. What I built (~600 words)

Walk through the 13 phases at a high level, but emphasise the *experience* of using ASP, not the mechanics:
- The intake feels like a brief Q&A with a thoughtful colleague.
- The pre-mortem feels like a structured 30-minute conversation with someone paranoid in the helpful way.
- The validator catches things you nearly missed, including a few you'd argue weren't important — until you re-read them.
- The execution feels like watching an experienced contractor work, with you in the role of the engineer of record.

This section is where the LinkedIn-style framing differs from the academic preprint. The blog should make the reader want to *try* ASP, not just understand it.

### 3. The methodology and prior work (~500 words)

Klein, MAST, Plan-and-Act, Reflexion — same citations as the preprint but in narrative prose. Less "ASP combines X and Y" and more "I started by re-reading Klein's HBR piece, then found the MAST taxonomy, then ...". Tells the story of arriving at the design rather than presenting it as inevitable.

### 4. The empirical battery (~500 words)

Describe the methodology in prose. Reproduce the 47% → 100% bar chart inline. Be honest that n=8 is preliminary. Link to the full `tests/` directory in the repo for anyone who wants to inspect.

### 5. The unique finding: Iron Law 11 (~400 words)

This is the section that lands you in HN, Reddit, and academic-Twitter discussion. Describe the discovery in narrative form:

> *"I'd built the protocol assuming `claude -p /goal` would surface a non-zero exit code on a refused or unrecoverable goal. The 2026-05-17 test battery had a sub-test specifically for this — give the agent an impossible task and check the exit code. The agent refused gracefully, in three paragraphs of well-reasoned prose explaining exactly why the task was impossible. Then the process exited with status 0."*

Quote the agent's refusal verbatim (it's in `tests/claude-p-goal-runner-probe.md`). Show the `jq` parsing pattern as the corrective. This is the section that becomes the headline of the HN post and the most-quoted tweet.

### 6. Limitations (~300 words)

Same as the preprint, in prose. Add one paragraph at the end about *what would change my mind* — i.e., what evidence would convince you that the 47%→100% effect is artefact rather than real. Stating this explicitly signals scientific maturity.

### 7. How to try it (~200 words)

Three install paths. Note the Anthropic plugin directory submission status. Invite community evals.

### 8. Acknowledgments (~150 words)

Human-in-the-loop with Claude Opus 4.7. Link to `docs/ARCHITECTURE.md` Parts 5–6 for the collaboration model. Mention obra/superpowers, agentskills.io, and the Anthropic team behind `/goal`. This section signals you are a member of the community, not just shipping into it.

### 9. What's next (~200 words)

Honest list:
- Blind-adjudication replication (the most-needed follow-up).
- Cross-model transfer (Claude Sonnet, Opus 4.6, open-weight models).
- Domain extensions (frontend, ML pipelines, infrastructure).
- Workshop submission at NeurIPS 2026 LLM agents track or AAAI 2027.
- Native-speaker review of ES, IT, HE translations.

Close with an invitation: "If any of this resonates, here's how to reach me." Email + LinkedIn + GitHub.

---

## SEO notes

- **Title tag**: "Anticipating Shadow Points: A Pre-Mortem Protocol for LLM Agents | Ulisses Flores"
- **Meta description**: "How I built a Claude Code skill that turns 47% shadow-point coverage into 100% — methodology, empirical battery, and an unexpected finding about `claude -p` exit codes."
- **Open Graph image**: the 47% → 100% chart (1200×630 px).
- **Canonical URL**: whichever slug you pick; ensure no duplicate-content issue with the Pages site.

## Cross-link from existing pages

- Add a "Research / Writing" entry on your homepage navigation.
- Link from your `/about` page under "recent work".
- Link from the ulissesflores.com footer.

The blog post is the long-tail SEO target. It will be the highest-search-result hit for "Klein pre-mortem LLM agent" and similar queries six months from now.
