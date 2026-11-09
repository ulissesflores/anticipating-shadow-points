"""Append-only hash ledger for the 2026-11 study.

Each line of ``ledger.jsonl`` records one artifact (its path and SHA-256) and the hash of the
previous line, so changing or removing any earlier entry breaks every later link. The head hash
is what gets timestamped outside the repository (GitHub push, Software Heritage, OpenTimestamps).

Usage::

    python ledger.py add <kind> <file> [<file> ...]
    python ledger.py verify
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "ledger.jsonl"
GENESIS = "0" * 64


def sha256(path: Path) -> str:
    """Return the SHA-256 of a file.

    Parameters
    ----------
    path : Path
        Any file.

    Returns
    -------
    str
        Hex digest.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries() -> list[dict]:
    """Return the ledger lines, oldest first.

    Returns
    -------
    list of dict
        Parsed entries (empty when the ledger does not exist yet).
    """
    if not LEDGER.exists():
        return []
    return [json.loads(ln) for ln in LEDGER.read_text(encoding="utf-8").splitlines() if ln]


def link(entry: dict) -> str:
    """Return the hash of an entry without its own ``hash`` field.

    Parameters
    ----------
    entry : dict
        A ledger entry.

    Returns
    -------
    str
        Hex digest of the canonical JSON.
    """
    body = {k: v for k, v in entry.items() if k != "hash"}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def add(kind: str, paths: list[Path]) -> str:
    """Append one entry per file and return the new head hash.

    Parameters
    ----------
    kind : str
        What the files are (protocol, reference-list, trial, analysis...).
    paths : list of Path
        Files to record, relative to the repository root in the ledger.

    Returns
    -------
    str
        The hash of the last entry.
    """
    old = entries()
    prev = old[-1]["hash"] if old else GENESIS
    root = HERE.parents[1]
    with LEDGER.open("a", encoding="utf-8") as out:
        for path in paths:
            entry = {
                "n": len(old) + 1,
                "kind": kind,
                "path": path.resolve().relative_to(root).as_posix(),
                "sha256": sha256(path),
                "utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "prev": prev,
            }
            entry["hash"] = prev = link(entry)
            out.write(json.dumps(entry, sort_keys=True) + "\n")
            old.append(entry)
    return prev


def verify() -> bool:
    """Check every link and every recorded file hash.

    Returns
    -------
    bool
        True when the chain is intact and every file still has its recorded hash.
    """
    prev, ok, root = GENESIS, True, HERE.parents[1]
    for entry in entries():
        if entry["prev"] != prev or link(entry) != entry["hash"]:
            print("broken link at", entry["n"])
            ok = False
        file = root / entry["path"]
        if not file.exists() or sha256(file) != entry["sha256"]:
            print("changed or missing:", entry["path"])
            ok = False
        prev = entry["hash"]
    print("ledger head", prev, "OK" if ok else "FAILED")
    return ok


if __name__ == "__main__":
    if sys.argv[1:2] == ["add"]:
        print(add(sys.argv[2], [Path(p) for p in sys.argv[3:]]))
    elif sys.argv[1:] == ["verify"]:
        sys.exit(0 if verify() else 1)
    else:
        sys.exit(__doc__)
