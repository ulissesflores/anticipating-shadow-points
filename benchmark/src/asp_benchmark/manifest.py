"""Build, write, and verify a run manifest.

A run is laid out on disk as:

    runs/<run_id>/
      manifest.json          # the only commit-worthy artifact for proof
      env.json               # captured EnvFingerprint
      code.json              # hashes of every benchmark/src/ source file
      inputs/<eval_id>/<condition>.prompt.txt
      outputs/<eval_id>/<condition>.text.txt
      outputs/<eval_id>/<condition>.response.json
      adjudication/<eval_id>/<condition>.json
      report.md

`run_id` is a deterministic short hash derived from the env fingerprint
plus the run start timestamp (the timestamp guarantees uniqueness across
back-to-back runs; the env hash makes the prefix meaningful).

After everything is written, `build_manifest` walks the run directory,
hashes each file, groups them by leaf (env / code / inputs / outputs /
adjudication), computes leaf hashes, and combines them into the
manifest hash. The manifest.json itself is then written and contains the
manifest hash so a re-runner can verify by recomputing.

`verify_manifest(run_dir)` re-walks the directory and returns a list of
discrepancies, empty list if intact.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .adjudicator import Coverage
from .env_fingerprint import EnvFingerprint
from .eval_parser import EvalSpec
from .hasher import (
    HashTreeLeaf,
    build_manifest_hash,
    canonical_json,
    hash_bytes,
    hash_file,
    walk_files,
)
from .runner import Candidate


MANIFEST_FILENAME = "manifest.json"
MANIFEST_VERSION = 1


@dataclass
class RunLayout:
    """All the absolute paths used during a run, computed once."""

    run_dir: Path
    inputs_dir: Path
    outputs_dir: Path
    adjudication_dir: Path

    @classmethod
    def for_run(cls, runs_root: Path, run_id: str) -> "RunLayout":
        run_dir = runs_root / run_id
        return cls(
            run_dir=run_dir,
            inputs_dir=run_dir / "inputs",
            outputs_dir=run_dir / "outputs",
            adjudication_dir=run_dir / "adjudication",
        )

    def ensure(self) -> None:
        for d in (self.run_dir, self.inputs_dir, self.outputs_dir, self.adjudication_dir):
            d.mkdir(parents=True, exist_ok=True)


def make_run_id(env: EnvFingerprint, started_at: datetime) -> str:
    """Short, sortable, env-tagged run id.

    Shape: 2026-05-17T18-30-00Z-<8-hex>
    The hex suffix is derived from env so two machines with same wall-clock
    don't collide.
    """
    ts = started_at.strftime("%Y-%m-%dT%H-%M-%SZ")
    env_hash = hash_bytes(canonical_json(env.as_dict()))[:8]
    return f"{ts}-{env_hash}"


def write_inputs(
    layout: RunLayout,
    candidates: list[Candidate],
    prompts_text: dict[tuple[str, str], str],
) -> None:
    """Persist the exact prompt bytes that were sent. The dict is keyed by
    (eval_id, condition). Storing the prompt separately from the candidate
    response is what lets a re-runner diff prompts when reproducing."""
    for cand in candidates:
        eval_dir = layout.inputs_dir / cand.eval_id
        eval_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = eval_dir / f"{cand.condition}.prompt.txt"
        prompt_path.write_text(
            prompts_text[(cand.eval_id, cand.condition)],
            encoding="utf-8",
        )


def write_outputs(layout: RunLayout, candidates: list[Candidate]) -> None:
    """Persist every candidate's response text and raw JSON envelope."""
    for cand in candidates:
        eval_dir = layout.outputs_dir / cand.eval_id
        eval_dir.mkdir(parents=True, exist_ok=True)
        (eval_dir / f"{cand.condition}.text.txt").write_text(
            cand.text, encoding="utf-8"
        )
        (eval_dir / f"{cand.condition}.response.json").write_bytes(
            canonical_json(cand.raw_response)
        )


def write_adjudication(layout: RunLayout, coverages: list[Coverage]) -> None:
    """Persist one adjudication JSON per (eval, condition)."""
    for cov in coverages:
        eval_dir = layout.adjudication_dir / cov.eval_id
        eval_dir.mkdir(parents=True, exist_ok=True)
        (eval_dir / f"{cov.candidate_label}.json").write_bytes(
            canonical_json(cov.as_dict())
        )


def write_env(layout: RunLayout, env: EnvFingerprint) -> None:
    (layout.run_dir / "env.json").write_bytes(canonical_json(env.as_dict()))


def write_code_inventory(layout: RunLayout, code_root: Path) -> None:
    """Hash every .py file under benchmark/src/ and write code.json.

    This makes the code-version a first-class part of provenance: if
    anyone changes a source file between runs, code.json changes, the
    code leaf hash changes, the manifest hash changes, and the diff is
    visible by re-running verify.
    """
    files = []
    for path in walk_files(code_root):
        if not path.name.endswith(".py"):
            continue
        files.append({
            "relative_path": str(path.relative_to(code_root)),
            "sha256": hash_file(path),
            "size_bytes": path.stat().st_size,
        })
    payload = {
        "code_root": str(code_root.relative_to(code_root.parent)),
        "files": sorted(files, key=lambda f: f["relative_path"]),
    }
    (layout.run_dir / "code.json").write_bytes(canonical_json(payload))


def build_manifest(
    layout: RunLayout,
    *,
    started_at: datetime,
    finished_at: datetime,
    mode: str,
    model: str,
    eval_count: int,
    candidate_count: int,
) -> dict:
    """Walk the run directory, build the hash tree, write manifest.json,
    return the manifest dict (for log/UI consumption)."""
    leaves = [
        HashTreeLeaf(name="env"),
        HashTreeLeaf(name="code"),
        HashTreeLeaf(name="inputs"),
        HashTreeLeaf(name="outputs"),
        HashTreeLeaf(name="adjudication"),
    ]
    leaf_by_name = {leaf.name: leaf for leaf in leaves}

    # Map each on-disk file to its appropriate leaf.
    for path in walk_files(layout.run_dir):
        rel = path.relative_to(layout.run_dir)
        first = rel.parts[0] if rel.parts else ""
        # The manifest itself must not be hashed into the leaves; that
        # would be circular. We also skip the run-summary report.
        if rel.name in {MANIFEST_FILENAME, "report.md"}:
            continue
        if first == "env.json":
            leaf_by_name["env"].add_file(layout.run_dir, path)
        elif first == "code.json":
            leaf_by_name["code"].add_file(layout.run_dir, path)
        elif first == "inputs":
            leaf_by_name["inputs"].add_file(layout.run_dir, path)
        elif first == "outputs":
            leaf_by_name["outputs"].add_file(layout.run_dir, path)
        elif first == "adjudication":
            leaf_by_name["adjudication"].add_file(layout.run_dir, path)
        # Anything else under run_dir is unexpected and ignored on
        # purpose — adding it silently to a leaf would hide drift.

    manifest_hash = build_manifest_hash(leaves)

    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "manifest_hash_algo": "sha256",
        "manifest_hash": manifest_hash,
        "run_id": layout.run_dir.name,
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat(),
        "mode": mode,                  # "real" | "mock"
        "model": model,                # caller-recorded label
        "eval_count": eval_count,
        "candidate_count": candidate_count,
        "leaves": [leaf.as_dict() for leaf in leaves],
    }
    (layout.run_dir / MANIFEST_FILENAME).write_bytes(canonical_json(manifest))
    return manifest


def verify_manifest(run_dir: Path) -> list[str]:
    """Re-walk `run_dir`, recompute the manifest hash, and report
    discrepancies. Empty list means intact."""
    discrepancies: list[str] = []
    manifest_path = run_dir / MANIFEST_FILENAME
    if not manifest_path.exists():
        return [f"missing manifest.json at {run_dir}"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Recompute leaves from disk.
    leaves = [
        HashTreeLeaf(name="env"),
        HashTreeLeaf(name="code"),
        HashTreeLeaf(name="inputs"),
        HashTreeLeaf(name="outputs"),
        HashTreeLeaf(name="adjudication"),
    ]
    leaf_by_name = {leaf.name: leaf for leaf in leaves}

    for path in walk_files(run_dir):
        rel = path.relative_to(run_dir)
        first = rel.parts[0] if rel.parts else ""
        if rel.name in {MANIFEST_FILENAME, "report.md"}:
            continue
        if first == "env.json":
            leaf_by_name["env"].add_file(run_dir, path)
        elif first == "code.json":
            leaf_by_name["code"].add_file(run_dir, path)
        elif first in {"inputs", "outputs", "adjudication"}:
            leaf_by_name[first].add_file(run_dir, path)

    recomputed = build_manifest_hash(leaves)
    if recomputed != manifest["manifest_hash"]:
        discrepancies.append(
            f"manifest_hash mismatch: stored={manifest['manifest_hash']} "
            f"recomputed={recomputed}"
        )

    # Cross-check each leaf hash too — narrows where the tamper was.
    stored_leaves = {leaf["name"]: leaf["leaf_hash"] for leaf in manifest["leaves"]}
    for leaf in leaves:
        if leaf.leaf_hash() != stored_leaves.get(leaf.name):
            discrepancies.append(
                f"leaf '{leaf.name}' hash mismatch: stored="
                f"{stored_leaves.get(leaf.name)} recomputed={leaf.leaf_hash()}"
            )
    return discrepancies


def utcnow() -> datetime:
    """Centralized "now" so tests can monkeypatch if needed."""
    return datetime.now(timezone.utc).replace(microsecond=0)
