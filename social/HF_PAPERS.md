# Hugging Face Papers submission

**Prerequisite**: arXiv ID must be assigned (i.e., the preprint must be live on arXiv with a permanent ID, not just on the repository).

**Submission URL**: https://huggingface.co/papers/submit

**Process** (≤5 min once arXiv is live):

1. Sign in to Hugging Face.
2. Open the submit page.
3. Paste the arXiv abstract URL: `https://arxiv.org/abs/XXXX.XXXXX`.
4. Hugging Face automatically fetches the paper metadata (title, abstract, authors).
5. Add a short tag list. Suggested:
   - `agents`
   - `evaluation`
   - `multi-agent`
   - `pre-mortem`
   - `Claude`
   - `agentic-workflow`
6. Optional: add an authored comment (≤1000 chars) summarising why this is worth the community's attention. Suggested text below.

## Author comment (paste in the "comment" field)

```
This preprint introduces ASP (Anticipating Shadow Points), a 13-phase pre-mortem-first planning protocol for LLM coding agents. The methodology integrates Klein's prospective hindsight (HBR 1998), Berkeley's MAST 14-mode failure taxonomy (arXiv 2503.13657), Plan-and-Act separation (arXiv 2503.09572), and Reflexion-style validators (Shinn et al. 2023) under strict prompt isolation.

The empirical contribution: on a battery of five structured engineering evaluations, baseline shadow-point coverage rises from ~47% to ~100%. MAST 14-mode forced enumeration is identified as the dominant load-bearing component.

The novel finding: `claude -p` returns exit code 0 even when the agent gracefully refuses the requested goal. Iron Laws 11 and 12 codify the safe parsing pattern (parse `is_error`, `terminal_reason`, `stop_reason` from `--output-format json`; never trust `$?`).

Open source, MIT, multilingual docs. Plugin marketplace install plus dev mode plus standalone script.
```

## After submission

- The paper appears in the Hugging Face Papers feed and is searchable.
- People who click your paper see the abstract + the author comment + a link to arXiv.
- Comments from other Hugging Face users will appear on the paper page; respond substantively the same way you would on r/MachineLearning.

## Related Hugging Face surfaces

- **Spaces**: if you build a demo Space (e.g., showing the RED/GREEN comparison interactively), you can link it from the paper. Optional and lower priority than the paper submission itself.
- **Datasets**: if the eval battery becomes a formal dataset (it could — the INPUT + EXPECTED + ACCEPTANCE structure is reusable), you could upload it to the Hugging Face Datasets hub for community contributions. Out of scope for the initial launch.

## Caveat

Hugging Face Papers does not run automatic acceptance review; anyone can submit any arXiv paper. The community signal comes from the comment activity and upvotes on the paper page, not from gate-keeping. Treat this surface as discovery, not endorsement.
