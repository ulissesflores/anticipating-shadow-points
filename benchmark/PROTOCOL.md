# ASP Benchmark — Scientific Protocol

This document defines what the benchmark measures, how it measures it,
and how a reviewer can falsify any claim it produces. It is the load-bearing
specification; the Python code under `src/asp_benchmark/` is one
implementation, and another implementation in any language with `sha256`
and JSON support should produce identical adjudication scores given
identical inputs.

## 1. What is measured

For each evaluation $E$ in the eval set and each condition $c \in \{RED, GREEN\}$:

- A candidate plan $p_{E,c}$ is collected — free-text prose from an LLM
  agent prompted under condition $c$.
- A coverage score $\mathrm{cov}(p_{E,c}, S_E)$ is computed against the
  expected shadow-point set $S_E$ defined ex-ante in the eval's
  markdown file.

The headline metrics are:

- Per-eval RED coverage and GREEN coverage.
- Per-eval delta (GREEN − RED, in percentage points).
- Mean RED, mean GREEN, mean delta across the eval set.

These metrics are the *only* claims the benchmark makes. Any downstream
interpretation (effect size, significance, generalization) is the
caller's responsibility.

## 2. How coverage is computed

Coverage is

$$ \mathrm{cov}(p, S) = \frac{|\{ s \in S : \mathrm{matches}(p, s) = 1 \}|}{|S|} $$

where $\mathrm{matches}(p, s)$ is a binary predicate evaluated by the
layered procedure below. Layer order is significant: the first layer
that fires wins, and the layer index is recorded in the adjudication
JSON for audit.

| Layer | Test | Notes |
|---|---|---|
| 1 | $\mathrm{normalize}(s.\mathrm{name}) \in \mathrm{normalize}(p)$ | exact substring after lower/punctuation normalisation |
| 2 | $\exists \mathrm{syn} \in \mathrm{Syn}(s) : \mathrm{normalize}(\mathrm{syn}) \in \mathrm{normalize}(p)$ | optional per-eval synonym sidecar |
| 3 | $\max_w \mathrm{Jaccard}(\mathrm{tokens}(s.\mathrm{text}), w) \geq T$ | sliding-window Jaccard |
| 4 | no match | recorded with the best Jaccard seen |

Where:

- $\mathrm{normalize}$ lowercases, strips punctuation except hyphens,
  collapses whitespace.
- $\mathrm{tokens}$ tokenises by whitespace after normalisation and
  removes a fixed stopword list (see `adjudicator.py:_STOPWORDS`).
- $w$ ranges over sliding token windows of size `WINDOW_TOKENS=40` at
  stride `WINDOW_STRIDE=10` over the candidate plan.
- $T = $ `JACCARD_THRESHOLD=0.30`.

**All constants are committed to source.** Changing them changes
adjudication scores and is therefore a versioning event for the
benchmark, not a silent tuning knob.

## 3. The provenance hash chain

A run produces a directory `runs/<run-id>/` containing:

```
manifest.json          # commit-worthy proof
env.json               # Python, OS, claude CLI versions
code.json              # sha256 of every .py file under src/asp_benchmark/
inputs/<E>/<c>.prompt.txt
outputs/<E>/<c>.text.txt
outputs/<E>/<c>.response.json
adjudication/<E>/<c>.json
report.md
```

A hash chain is built as follows:

1. Each on-disk file contributes one `FileHash(relative_path, sha256, size_bytes)`.
2. Files are grouped into five leaves: `env`, `code`, `inputs`, `outputs`,
   `adjudication`.
3. Each leaf's `leaf_hash` is the sha256 of its canonical-JSON
   enumeration (file list sorted by `relative_path`).
4. The `manifest_hash` is the sha256 of the canonical-JSON list of
   `{name, leaf_hash}` records, sorted by `name`.

**Tamper detection.** Editing any byte under the run directory changes
the hash of the corresponding leaf, which changes `manifest_hash`. The
`verify` command re-walks the directory, recomputes leaves, and reports
any discrepancy.

**Cross-language reproducibility.** The hash chain depends only on:

- sha256 (RFC 6234)
- canonical JSON (sorted keys, no whitespace, UTF-8)
- the explicit leaf-grouping rules above

Any reviewer with these primitives can reimplement `verify` in another
language and confirm a published `manifest_hash` is genuine.

## 4. Determinism

The following hold by design:

1. **Adjudication is deterministic.** Given identical candidate text and
   identical eval markdown, adjudication produces the same matched /
   unmatched partition and the same coverage score. Pinned by tests in
   `tests/test_adjudicator.py::test_adjudication_is_deterministic`.

2. **Mock-mode runs are deterministic.** A mock run reads canned RED /
   GREEN texts from `tests/fixtures/mock_runs/` and runs the full
   pipeline. Two mock runs differ only in `started_at_utc`/`finished_at_utc`
   (which are excluded from the hash chain in normalized form) and in
   `run_id` (which incorporates the timestamp). The leaf hashes are
   identical across runs; only the manifest's metadata timestamps differ.
   This is the standard CI determinism contract.

3. **Real-mode runs are NOT deterministic.** Claude's response text
   varies turn-to-turn; this is a property of LLMs, not a bug. The
   benchmark records the exact bytes returned so the *evidence* is
   durable; the score is reproducible only across re-adjudications of
   the same recorded text, not across re-dispatches.

## 5. What this benchmark does NOT prove

- It does not prove that ASP transfers to other models or other eval
  sets. That requires re-running the benchmark on those models and
  eval sets.
- It does not prove the expected shadow-point lists are themselves
  unbiased. The lists are authored by the ASP author; blind
  re-authoring by independent reviewers is the strongest follow-up.
- It does not prove the adjudication thresholds are universally
  appropriate. Different domains may require different
  `JACCARD_THRESHOLD` values; changes are auditable in `code.json`.
- It does not certify the *quality* of a plan — only whether it
  *covers* the expected shadow points. A plan with 100% coverage may
  still be wrong on the merits.

## 6. Reproducing a published run

A published run is one whose `manifest.json` and (optionally) `report.md`
are committed to `runs/published/<run-id>/`. To reproduce:

```bash
git clone <repo>
cd benchmark
python -m asp_benchmark verify <run-id> --runs runs/published
```

If `verify` reports OK, the published manifest_hash matches the
recomputed hash, which means every byte under the published run is the
byte the author claimed.

## 7. Versioning

- **Eval markdown changes** require a new run. The new run will have a
  different `inputs` leaf hash.
- **Adjudication code changes** require a new run. The new run will have
  a different `code` leaf hash.
- **Threshold changes** are adjudication code changes — they are
  intentionally tracked via `code.json`.
- **Mock fixture changes** are inputs to the *test suite*, not to the
  scientific claim; they affect determinism of CI runs but do not affect
  real-mode runs against `claude -p`.

## 8. Limitations honestly documented

- The Jaccard sliding-window approach is a deterministic
  approximation of paraphrase detection. It under-recalls true
  paraphrases that use entirely different vocabulary; it over-recalls
  near-coincidental token overlaps in long candidate texts. The
  per-eval synonym sidecar partially compensates but does not
  eliminate the underlying issue.
- The mock fixtures embedded in the benchmark are constructed to
  exercise the *adjudicator's* layered match (exact / synonym /
  Jaccard / unmatched). They are NOT representative of true LLM
  outputs from `claude -p`; only real-mode runs produce evidence
  about ASP's effect on real LLM behavior.
- Adjudication is fundamentally a string-matching procedure. A model
  that paraphrases an expected point in semantically equivalent but
  lexically disjoint language may not be matched. The strongest
  follow-up is an embedding-based adjudicator with a pinned model
  version; this is on the future-work track and would change the
  benchmark's deterministic contract.
