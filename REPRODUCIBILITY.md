# Reproducibility

This repository makes two different promises. They are kept apart on purpose, because mixing them is how research repos overstate what a reader can check.

| Seal | What it covers | Can you re-run it? | How you check it |
|---|---|---|---|
| **Seal 1: reproducible derivation** | Every measured number the papers cite, every figure, every test | Yes, offline, in seconds | `python run_all.py` |
| **Seal 2: frozen evidence** | The `claude -p` transcripts and the benchmark fixtures the numbers are derived from | No. The target is a non-deterministic, server-side model that has since changed | `python make_provenance.py --verify` proves the bytes are the ones the numbers came from |

Seal 1 says "given these transcripts, the numbers follow". Seal 2 says "these are the transcripts, unaltered since they were sealed". Neither says that running the same prompts today would give the same transcripts. It would not, and the papers say so.

## Track 1: verify in under a minute (no model calls)

```bash
git clone https://github.com/ulissesflores/anticipating-shadow-points
cd anticipating-shadow-points
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python run_all.py
```

Expected tail:

```text
== tests: -m pytest -q tests
........................                                                 [100%]
== verify: make_provenance.py --verify
provenance verified: chain_hash <64 hex characters, equal to output/hash-chain.md>
run_all OK: results reproduced, tests passed, provenance verified
```

`run_all.py` runs five steps and stops at the first failure:

1. `analysis/results.py` derives `output/results.json` from the frozen inputs.
2. `analysis/make_figures.py` renders `output/figures/` from that file.
3. `pytest` asserts every measured number the papers cite (`tests/test_paper_numbers.py`) and that the derivation is deterministic and matches the committed output (`tests/test_determinism.py`).
4. `make_provenance.py` rebuilds the seal.
5. `make_provenance.py --verify` recomputes it and compares it with the committed one.

`--verify` on its own (step 5) is the cheapest integrity check and is what CI runs first.

## What the seal hashes

One SHA-256 `chain_hash` over five ordered leaves. Each leaf is the hash of its sorted `path -> sha256` list, encoded as canonical JSON (sorted keys, UTF-8, no whitespace). The primitives are the benchmark's own (`benchmark/src/asp_benchmark/hasher.py`), so there is one hashing implementation in the repo, not two.

| Leaf | Contents |
|---|---|
| `code` | `run_all.py`, `make_provenance.py`, `analysis/*.py`, `benchmark/src/asp_benchmark/*.py`, the locked `tests/iron-law-11/scripts/analyze.py` |
| `tests` | `tests/conftest.py`, `tests/test_*.py` |
| `frozen_inputs` | the May 2026 `claude -p` run, the mock benchmark run (author-written fixtures), the 50 locked scenarios, the locked refusal-phrase list and seed, the five evaluation specs |
| `data` | `data/**` (the redacted July 2026 extract, its labels and codebook) |
| `results` | `output/results.json` |

**Informational, NOT hashed:** `output/figures/*`, `requirements.lock`, the Python version and the platform. Rasterised figures differ across platforms and matplotlib versions; hashing them would make the seal fail on a reader's machine for reasons unrelated to the science. They are listed with their hashes in `output/hash-chain.md` for audit.

## Track 2: re-collect (costs model calls, will not match)

The collection scripts are kept so the method is inspectable and a new snapshot can be taken:

| Experiment | Script | Note |
|---|---|---|
| `claude -p` exit codes (May 2026) | `tests/iron-law-11/scripts/run-protocol.sh` | 50 prompts, `--max-turns 1`, about USD 5 at API prices |
| RED/GREEN benchmark | `python -m asp_benchmark run --mode real` in `benchmark/` | Never run for a published number; the published run is `--mode mock` over author-written fixtures |

A new run produces a new dated snapshot. Report it next to the old one; never replace the old one. New experiments follow [`PREREGISTRATION.md`](PREREGISTRATION.md): the protocol is frozen and publicly timestamped before the first trial.

## What cannot be re-run, and why

- **The model is not pinned.** `claude -p` resolves a model server-side; the same CLI version can answer with a different model later, and the July 2026 run shows the session model handing safety prompts to another model mid-suite (Fable 5 to Opus 4.8). The transcripts are the evidence; the model that produced them is not available to re-query.
- **The July 2026 raw envelopes are private.** The CLI's `system/init` event records machine-local state (working directory, memory paths, installed plugins and MCP servers). The public file `data/spike-2026-07-08/trials.jsonl` keeps the fields the analysis uses, replaces one e-mail address and one local path with markers, and records the SHA-256 of each raw file so the extract can be tied to the originals on request.
- **The July 2026 prompts were not captured in the envelope.** Trials carry the same scenario ids as the locked suite in `tests/iron-law-11/scenarios/`; the text sent is inferred from the id, not recorded.
- **The benchmark has no model evidence.** Its one published run is a mock run: the RED and GREEN texts are fixtures written to exercise the matcher (`benchmark/PROTOCOL.md`, section 8). The author's May 2026 reading of real subagent plans survives only as a summary in `tests/evals-summary.md`; those transcripts were not preserved.
- **The frozen May 2026 runs keep machine-local paths.** `tests/iron-law-11/runs/published/` and `benchmark/runs/published/` were published unredacted in v1.0.x and are sealed: their envelopes carry the author's home-folder path, the plugin cache path and the list of installed skills. They are left byte-identical, because editing them would break the seal and the published DOI copies; only the July 2026 data, published for the first time in v2.0.0, is redacted.
- **Environment contamination.** The July 2026 run executed inside the author's own Claude Code setup, with his global instructions loaded; two replies refer to that setup. The May 2026 run executed in the repository's test folder with the plugin installed. Neither is a clean-room environment.

## Determinism

The derivation reads files only: no network, no clock, no random numbers. `tests/test_determinism.py` derives the results twice in one process and compares them with the committed `output/results.json`.
