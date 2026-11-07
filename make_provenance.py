"""Seal code, tests, data and derived results under one SHA-256 chain hash.

``python make_provenance.py``          build ``output/provenance.json`` and
                                       ``output/hash-chain.md``
``python make_provenance.py --verify`` recompute and compare with the
                                       committed seal (exit 1 on mismatch)

The hashing primitives are the benchmark's own (``benchmark/src/asp_benchmark/
hasher.py``): sorted canonical JSON, UTF-8, SHA-256. Each sealed group is a leaf
(the hash of its sorted ``path -> sha256`` list); the chain hash is the hash of
the ordered leaves. Figures, the lockfile and the platform are recorded as
*informational* and are NOT hashed, so the seal survives a change of machine or
of plotting library.
"""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "benchmark" / "src"))

from asp_benchmark.hasher import hash_file, hash_json  # noqa: E402

PROVENANCE = ROOT / "output" / "provenance.json"
CHAIN_MD = ROOT / "output" / "hash-chain.md"

# Ordered: the chain hash depends on this order.
GROUPS: dict[str, list[str]] = {
    "code": [
        "run_all.py",
        "make_provenance.py",
        "analysis/*.py",
        "benchmark/src/asp_benchmark/*.py",
        "tests/iron-law-11/scripts/analyze.py",
    ],
    "tests": ["tests/conftest.py", "tests/test_*.py"],
    "frozen_inputs": [
        "tests/iron-law-11/preregistration.json",
        "tests/iron-law-11/refusal-phrases.txt",
        "tests/iron-law-11/random_seed.txt",
        "tests/iron-law-11/scenarios/*.txt",
        "tests/iron-law-11/runs/published/**/*",
        "benchmark/runs/published/**/*",
        "skills/anticipating-shadow-points/evals/*.md",
    ],
    "data": ["data/**/*", "PREREGISTRATION.md"],
    "results": ["output/results.json"],
}
INFORMATIONAL = ["output/figures/*", "requirements.lock"]


def _files(patterns: list[str]) -> list[Path]:
    """Expand glob patterns relative to the repo root.

    Parameters
    ----------
    patterns : list of str
        Glob patterns.

    Returns
    -------
    list of Path
        Sorted, de-duplicated regular files (``.DS_Store`` and caches excluded).
    """
    found = set()
    for pattern in patterns:
        for path in ROOT.glob(pattern):
            if path.is_file() and path.name != ".DS_Store" and "__pycache__" not in path.parts:
                found.add(path)
    return sorted(found)


def _rel(path: Path) -> str:
    """Return a POSIX path relative to the repo root.

    Parameters
    ----------
    path : Path
        Absolute path inside the repo.

    Returns
    -------
    str
        Relative POSIX path.
    """
    return path.relative_to(ROOT).as_posix()


def build() -> dict:
    """Hash every sealed group and combine the leaves into the chain hash.

    Returns
    -------
    dict
        The provenance document.
    """
    leaves = {}
    for name, patterns in GROUPS.items():
        entries = [{"path": _rel(p), "sha256": hash_file(p)} for p in _files(patterns)]
        leaves[name] = {"files": entries, "leaf_sha256": hash_json(entries)}
    chain = hash_json([[name, leaves[name]["leaf_sha256"]] for name in GROUPS])
    informational = {
        "files": [{"path": _rel(p), "sha256": hash_file(p)} for p in _files(INFORMATIONAL)],
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    return {
        "schema": 1,
        "algorithm": "sha256 over canonical JSON (sorted keys, UTF-8, no whitespace)",
        "chain_hash": chain,
        "leaves": leaves,
        "informational_not_hashed": informational,
    }


def write(doc: dict) -> None:
    """Write ``provenance.json`` and the human-readable ``hash-chain.md``.

    Parameters
    ----------
    doc : dict
        Output of :func:`build`.
    """
    PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    PROVENANCE.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Hash chain",
        "",
        f"**chain_hash** `{doc['chain_hash']}`",
        "",
        "Recompute with `python make_provenance.py --verify`.",
        "",
        "| Leaf | Files | leaf_sha256 |",
        "|---|---|---|",
    ]
    for name in GROUPS:
        leaf = doc["leaves"][name]
        lines.append(f"| {name} | {len(leaf['files'])} | `{leaf['leaf_sha256']}` |")
    lines += [
        "",
        "## Informational (NOT hashed)",
        "",
        "Figures, the lockfile and the platform vary by machine and are listed for audit only.",
        "",
    ]
    lines += [
        f"- `{f['path']}` `{f['sha256'][:16]}…`" for f in doc["informational_not_hashed"]["files"]
    ]
    CHAIN_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify() -> int:
    """Recompute the seal and compare it with the committed one.

    Returns
    -------
    int
        0 if every leaf and the chain hash match, 1 otherwise.
    """
    committed = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    fresh = build()
    bad = [
        name
        for name in GROUPS
        if committed["leaves"].get(name, {}).get("leaf_sha256")
        != fresh["leaves"][name]["leaf_sha256"]
    ]
    if bad or committed["chain_hash"] != fresh["chain_hash"]:
        for name in bad:
            old = {
                f["path"]: f["sha256"] for f in committed["leaves"].get(name, {}).get("files", [])
            }
            new = {f["path"]: f["sha256"] for f in fresh["leaves"][name]["files"]}
            for path in sorted(old.keys() | new.keys()):
                if old.get(path) != new.get(path):
                    print(f"  mismatch [{name}] {path}")
        print(
            f"provenance FAILED: chain {fresh['chain_hash']} != committed {committed['chain_hash']}"
        )
        return 1
    print(f"provenance verified: chain_hash {fresh['chain_hash']}")
    return 0


def main() -> int:
    """Entry point: build by default, compare with ``--verify``.

    Returns
    -------
    int
        Process exit code.
    """
    if "--verify" in sys.argv[1:]:
        return verify()
    doc = build()
    write(doc)
    print(f"provenance written: chain_hash {doc['chain_hash']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
