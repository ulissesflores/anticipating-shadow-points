#!/usr/bin/env python3
"""Build the validation folder validate_canon.py reads, for ONE article, and print the folder.

validate_canon.py (research-lab/metodo/tools) expects <pasta>/docs/paper/paper-final-en.{md,docx,pdf} (the lab layout,
one paper per folder) and <pasta>/repo/ (the public repo). The ASP repo ships TWO papers named <nome>.en.*, so the
mirror is curated: real files for docs/paper/, and symlinks (never copies) from repo/ to the repo metadata plus the
Word-built paper under the basename the validator wants. Only the files the canon names are linked, so the
validator's rglob does not walk .venv/, claude-cache/, runtime/ or .serena/.

Usage: python3 -I paper/tools/canon_mirror.py <nome>      (nome = iron-law-11 | asp-preprint)
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
META = ["README.md", "CITATION.cff", "codemeta.json", ".zenodo.json", "LICENSE", "requirements.txt", "run_all.py"]
PROV = ["configs/stages.json", "scripts/provenance_chain.py", "scripts/verify_chain.py", "scripts/build_run.py"]
BASE = "paper-final-en"


def main() -> int:
    nome = sys.argv[1]
    b = REPO / "build" / nome
    pasta = REPO / "build" / "canon" / nome
    if pasta.exists():
        shutil.rmtree(pasta)  # only the mirror folder under build/canon/<nome>, never anything else
    (pasta / "docs" / "paper").mkdir(parents=True)
    (pasta / "repo" / "docs" / "paper").mkdir(parents=True)
    shutil.copyfile(b / "fonte.md", pasta / "docs/paper" / f"{BASE}.md")          # derived source (refs as '- ' items)
    for ext in ("docx", "pdf"):
        shutil.copyfile(b / f"{nome}.{ext}", pasta / "docs/paper" / f"{BASE}.{ext}")
        (pasta / "repo/docs/paper" / f"{BASE}.{ext}").symlink_to(REPO / "docs/paper" / f"{nome}.en.{ext}")
    for f in META + PROV:
        if (REPO / f).exists():
            d = pasta / "repo" / f
            d.parent.mkdir(parents=True, exist_ok=True)
            d.symlink_to(REPO / f)
    for f in REPO.glob("runs/*/manifest.json"):
        d = pasta / "repo" / f.relative_to(REPO)
        d.parent.mkdir(parents=True, exist_ok=True)
        d.symlink_to(f)
    print(pasta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
