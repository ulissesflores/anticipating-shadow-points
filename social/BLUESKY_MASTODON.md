# Bluesky / Mastodon — academic AI fediverse

These platforms are increasingly important for the academic AI/ML community in 2026, especially as Twitter/X engagement for serious research has shifted. Different audiences than Twitter; less viral, more rigorous, longer-lasting threads.

## Bluesky

**Recommended audience**: AI/ML researchers, agentic-AI builders, open-source maintainers. Many academic accounts have migrated here.

**Suggested approach**: shorter than the Twitter/X thread (the academic AI Bluesky community values concision). 5–6 posts is plenty. Adapt the Twitter thread:

### Bluesky thread (5 posts)

```
1/ Built a Claude Code skill that turns ~47% shadow-point coverage into ~100% on non-trivial engineering tasks.

Method: Klein 1998 pre-mortem + Berkeley MAST 14-mode failure taxonomy + validator subagent under strict prompt isolation + claude -p /goal subprocess.

Repo: github.com/ulissesflores/anticipating-shadow-points
```

```
2/ Most interesting empirical finding for anyone wrapping `claude -p`:

It returns exit code 0 even on graceful agent refusal. `claude -p "<goal>" || handle_error` will misroute refusals as successes.

Codified as Iron Law 11: parse JSON, never trust $?.
```

```
3/ The load-bearing component is MAST 14-mode forced enumeration.

Free-form pre-mortem clusters on obvious categories (data, integration). MAST forces enumeration over time/tz, observability, op-ex, contract drift — categories that get missed without it.

Ablating MAST drops coverage back toward 50%.
```

```
4/ Honest limitations:

- n=8 subagent dispatches across 5 domains (preliminary, not robust)
- Same-model condition (Claude Opus 4.7); cross-model unverified
- Adjudication paraphrase-tolerant but not blind
- 3 of 5 doc translations AI-assisted, pending native review

LaTeX preprint source under paper/.
```

```
5/ Three install paths: plugin marketplace, dev mode (--plugin-dir), standalone install.sh. MIT licensed. Submitted to the Anthropic plugin directory.

Built with Claude Opus 4.7 under explicit human-in-the-loop direction. Collaboration model documented openly.

Critique + community evals welcome.
```

## Mastodon

**Suggested servers**:
- `@fosstodon.org` — open source community
- `@hci.social` — HCI / AI researchers
- `@scholar.social` — academic-only server, requires application but high-quality engagement
- `@sigmoid.social` — ML/AI researchers (many academic accounts)

**Crosspost from Bluesky** is fine; the audiences overlap somewhat but Mastodon has a separate community of older fediverse-native academic AI users.

**Tone**: identical to Bluesky. Mastodon tolerates slightly longer posts (500-char default vs 300-char Bluesky), but break the thread similarly for readability.

**Hashtags** (use sparingly on fediverse; 2-3 max):
- `#LLMAgents`
- `#OpenSource`
- `#ClaudeCode` (smaller community here)

## Cross-posting tools

If you want one-write/multi-platform, options:
- **Buffer** — supports both Bluesky and Mastodon now.
- **Typefully** — Twitter-first but adds Bluesky.
- **Manual cross-post** — recommended for the launch; each platform's community deserves a slightly customised tone.

For the launch I recommend manual cross-post — you can adjust the framing for each platform's culture, and the engagement-per-post is higher when the writing feels native.

## Engagement expectations

Bluesky and Mastodon engagement counts are smaller than Twitter, but **quality is higher and persistence is longer**. A good Bluesky thread can be re-shared for weeks; a good Mastodon post stays in scholar.social searches indefinitely. Don't measure success by hour-1 engagement; check back at week-2 and week-4 for cumulative reach.
