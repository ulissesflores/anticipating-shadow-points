"""Check the committed paper editions against ``paper/PAPER-SHA256.txt``.

The PDF and DOCX editions are built by Microsoft Word on macOS
(``paper/tools/build_paper.sh``), so CI cannot rebuild them; it can check that the files in
``docs/paper/`` are the ones whose SHA-256 the build recorded. They sit outside the chain
seal of ``make_provenance.py``.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "docs" / "paper"
LIST = ROOT / "paper" / "PAPER-SHA256.txt"
EDITIONS = {
    f"{name}.{lang}.{ext}"
    for name in ("asp-preprint", "graceful-refusals")
    for lang in ("en", "pt-BR", "es", "it")
    for ext in ("pdf", "docx")
}


def recorded() -> dict[str, str]:
    """Return the file name -> SHA-256 map recorded by the build.

    Returns
    -------
    dict[str, str]
        One entry per line of ``paper/PAPER-SHA256.txt`` (``shasum -a 256`` format).
    """
    pairs = (
        line.split(maxsplit=1)
        for line in LIST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    return {name.strip(): digest for digest, name in pairs}


def test_every_edition_is_committed_and_listed() -> None:
    """Both papers ship in four languages as PDF and DOCX, and each file is listed."""
    assert {p.name for p in PAPERS.glob("*.pdf")} | {
        p.name for p in PAPERS.glob("*.docx")
    } == EDITIONS
    assert set(recorded()) == EDITIONS


def test_committed_editions_match_recorded_hashes() -> None:
    """Each committed edition hashes to the value the build recorded."""
    for name, digest in recorded().items():
        assert hashlib.sha256((PAPERS / name).read_bytes()).hexdigest() == digest, name
