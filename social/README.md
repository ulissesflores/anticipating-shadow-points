# Social distribution templates

Drafts ready for the staged, scientific-style announcement of ASP. Each file is a copy-paste-ready template. Recommended posting sequence:

| Week | Channel | File | Notes |
|---|---|---|---|
| **1** | arXiv preprint | `../paper/asp-preprint.tex` | Foundation; do this first. Without it, the social posts feel like "marketing" rather than "research release". |
| **1** | Zenodo DOI | (no file; do via Zenodo+GitHub integration UI) | Software DOI; 15-min OAuth + tag a release. |
| **2** | LinkedIn long-form article | `LINKEDIN.md` | Best fit for CTO + academic positioning. |
| **2** | Bluesky / Mastodon (academic AI) | `BLUESKY_MASTODON.md` | Lightweight cross-post; fediverse academic AI community. |
| **2** | r/MachineLearning | `REDDIT_ML.md` | Rigorous tag [R]; expect methodological critique. |
| **3** | Twitter / X thread | `TWITTER_THREAD.md` | 12 tweets; post Tue/Wed 14:00 UTC for max engagement. |
| **3** | Hacker News (Show HN) | `HN_SHOW.md` | Tue/Wed 11:00 UTC; prepare canned responses below. |
| **3** | Hugging Face Papers | `HF_PAPERS.md` | Submit arXiv ID; no separate content needed. |
| **4** | Personal blog (`ulissesflores.com`) | `PERSONAL_BLOG.md` | Long-tail; SEO + brand consolidation. |

## Anti-patterns to avoid

- **Posting everywhere on day zero**: looks like a coordinated marketing push, not a research release. Stagger by at least 48 hours between major channels.
- **Self-promo without artefact**: posting before arXiv is live makes the work appear unsubstantiated. arXiv (or at minimum Zenodo DOI) must exist first.
- **Hidden human-AI collaboration**: 2026 community norm is explicit acknowledgment; transparency wins trust.
- **Overstating limitations**: the n=8 subagent battery is "preliminary empirical evidence", not "robust evaluation". Honest framing earns credibility.
- **Ignoring critique**: engage substantively when reviewers raise methodology questions; update the repo and paper.

## Cross-channel consistency

The same three claims should appear, with consistent phrasing, in every channel:

1. **The headline number**: shadow-point coverage rises from approximately **47% to approximately 100%**.
2. **The unique empirical finding**: `claude -p` returns exit 0 even on graceful refusal — Iron Law 11.
3. **The methodological grounding**: Klein pre-mortem + Berkeley MAST 14-mode + Plan-and-Act + Reflexion.

If asked for the single most useful artefact, point at `docs/ARCHITECTURE.md` (the SOTA design document) — it is the canonical long-form explanation.
