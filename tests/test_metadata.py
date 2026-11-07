"""Release metadata agrees across every file that declares a version."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _versions() -> dict[str, str]:
    """Collect the version string declared by each metadata file."""
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    return {
        "pyproject.toml": tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
            "project"
        ]["version"],
        "CITATION.cff": re.search(r"^version:\s*(\S+)", cff, re.M).group(1),
        "codemeta.json": json.loads((ROOT / "codemeta.json").read_text(encoding="utf-8"))[
            "version"
        ],
        ".zenodo.json": json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))["version"],
        "plugin.json": json.loads(
            (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )["version"],
    }


def test_versions_agree():
    """Every metadata file declares the same version."""
    versions = _versions()
    assert len(set(versions.values())) == 1, versions


def test_author_orcid_everywhere():
    """The author's ORCID appears in all three scientific metadata files."""
    orcid = "0000-0002-6034-7765"
    for name in ("CITATION.cff", "codemeta.json", ".zenodo.json"):
        assert orcid in (ROOT / name).read_text(encoding="utf-8"), name
