"""Cryptographic provenance for benchmark runs.

The hash chain is structured as a Merkle-style tree:

    manifest.sha256 = sha256(
        env.sha256 || code.sha256 || inputs.sha256 ||
        outputs.sha256 || adjudication.sha256
    )

Each leaf is itself the sha256 of a canonicalised JSON blob enumerating its
children (filename + sha256). This makes tampering detectable at any level:
flipping one byte in a transcript changes outputs.sha256, which changes
manifest.sha256.

A re-runner verifies the manifest by:
  1. Recomputing each leaf from the on-disk artifacts.
  2. Recomputing the manifest hash from the leaves.
  3. Comparing against the manifest_hash field stored alongside the manifest.

The encoding is intentionally simple (sorted JSON, UTF-8, no compression) so
that the verification can be reimplemented in any language with sha256 and
a JSON library.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path


HASH_ALGO = "sha256"


def hash_bytes(data: bytes) -> str:
    """Return the hex sha256 of a byte string."""
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> str:
    """Return the hex sha256 of a file's bytes. Streams to avoid loading large
    transcripts fully into memory."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj: object) -> bytes:
    """Encode obj as canonical JSON: sorted keys, no whitespace, UTF-8.

    This is the only encoding used for hashing structured data. Pretty-printed
    JSON would change hashes under reformat; canonical form is stable.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def hash_json(obj: object) -> str:
    """Hash a Python object via its canonical JSON representation."""
    return hash_bytes(canonical_json(obj))


@dataclass(frozen=True)
class FileHash:
    """One leaf of the hash tree: a relative path and its sha256."""

    relative_path: str
    sha256: str
    size_bytes: int

    @classmethod
    def from_file(cls, root: Path, path: Path) -> "FileHash":
        rel = str(path.relative_to(root))
        return cls(
            relative_path=rel,
            sha256=hash_file(path),
            size_bytes=path.stat().st_size,
        )

    def as_dict(self) -> dict:
        return {
            "relative_path": self.relative_path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass
class HashTreeLeaf:
    """A named group of file hashes (e.g. all inputs, all outputs)."""

    name: str
    files: list[FileHash] = field(default_factory=list)

    def add_file(self, root: Path, path: Path) -> None:
        self.files.append(FileHash.from_file(root, path))

    def leaf_hash(self) -> str:
        """Hash of the canonical JSON enumeration of this leaf's files.

        Files are sorted by relative_path so that filesystem enumeration
        order does not perturb the hash.
        """
        payload = {
            "name": self.name,
            "files": sorted(
                (f.as_dict() for f in self.files),
                key=lambda f: f["relative_path"],
            ),
        }
        return hash_json(payload)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "leaf_hash": self.leaf_hash(),
            "files": sorted(
                (f.as_dict() for f in self.files),
                key=lambda f: f["relative_path"],
            ),
        }


def build_manifest_hash(leaves: Iterable[HashTreeLeaf]) -> str:
    """Combine leaf hashes into a single manifest hash.

    The combination is a hash of a canonical-JSON list of {name, leaf_hash}
    entries, sorted by name. Order independence inside the manifest is a
    feature: callers can append leaves in any order without breaking
    determinism.
    """
    payload = sorted(
        ({"name": leaf.name, "leaf_hash": leaf.leaf_hash()} for leaf in leaves),
        key=lambda d: d["name"],
    )
    return hash_json(payload)


def walk_files(root: Path) -> list[Path]:
    """Sorted recursive enumeration of files under root.

    Sorted order is required for cross-platform determinism: macOS and Linux
    can disagree on `Path.iterdir()` ordering.
    """
    return sorted(p for p in root.rglob("*") if p.is_file())
