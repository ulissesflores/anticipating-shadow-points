"""ASP Benchmark — reproducible evaluation with cryptographic provenance.

The package is organized so that every step from input → output → adjudication
is hash-chained. The top-level invariants:

  1. Same inputs + same code + same env ⇒ same manifest hash (modulo
     documented LLM non-determinism on the transcript bytes themselves).
  2. Adjudication is deterministic: same transcript bytes ⇒ same score.
  3. Tampering with any byte under a run directory invalidates the
     manifest hash and is detectable by re-running `verify_manifest`.
"""

__version__ = "0.1.0"
