# Published runs

Runs committed to this directory are intended as **public evidence**.
Each is a complete reproducible artefact: input prompts, candidate
outputs, adjudication, environment fingerprint, code inventory, and a
manifest hash that ties them together.

## How to verify a published run

From the `benchmark/` directory:

```bash
asp-benchmark verify <run-id> --runs runs/published
```

The command re-walks the run directory, recomputes every leaf hash, and
compares against the manifest. Any byte changed anywhere under the run
directory invalidates the manifest hash.

## What "published" means

- The manifest_hash in `manifest.json` is the single fingerprint of the
  run; the rest of the directory is the evidence it covers.
- Mock-mode runs are deterministic on content: rerunning mock mode with
  identical fixtures and identical code produces an identical
  manifest_hash. The `run_id` differs because it embeds a timestamp.
- Real-mode runs are NOT deterministic on content (claude responses
  vary). The manifest still ties together that specific run's exact
  bytes; the adjudication on those bytes is reproducible across
  re-adjudications by anyone, in any language.

## How to contest a claim

Read the eval markdown (the expected list), read the candidate plan in
`outputs/<E>/<condition>.text.txt`, and re-run adjudication. If your
adjudication disagrees with the published one, either you spotted a
matcher bug or the matcher's deterministic procedure produces a result
you find scientifically unsatisfying — both are valid grounds to open
a PR against `src/asp_benchmark/adjudicator.py`.
