"""The README and its four translations keep one structure, and no relative link is broken."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITIONS = ["README.md", "README.pt-BR.md", "README.es.md", "README.it.md", "README.he.md"]
PLUGIN_README = ROOT / "plugins" / "anticipating-shadow-points" / "README.md"
LINK = re.compile(r"(?:\]\(|src=\")([^)\"\s]+)")


def _heading_levels(path: Path) -> list[int]:
    """Return the level of every Markdown heading outside code blocks.

    Parameters
    ----------
    path : Path
        A Markdown file.

    Returns
    -------
    list of int
        One entry per heading, in order (2 for ``##``, 3 for ``###``...).
    """
    levels, fenced = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and (m := re.match(r"^(#{2,6}) ", line)):
            levels.append(len(m.group(1)))
    return levels


def _relative_targets(path: Path) -> list[str]:
    """Return every relative link or image target in a Markdown file.

    Parameters
    ----------
    path : Path
        A Markdown file.

    Returns
    -------
    list of str
        Targets without their ``#anchor`` part; URLs and pure anchors are left out.
    """
    targets = []
    for raw in LINK.findall(path.read_text(encoding="utf-8")):
        target = raw.split("#", 1)[0]
        if target and not re.match(r"^[a-z]+:", target):
            targets.append(target)
    return targets


def test_editions_share_one_structure():
    """All five editions have the same sequence of heading levels."""
    reference = _heading_levels(ROOT / EDITIONS[0])
    for name in EDITIONS[1:]:
        assert _heading_levels(ROOT / name) == reference, name


def test_every_edition_links_all_the_others():
    """Each edition carries the language selector to the other four."""
    for name in EDITIONS:
        text = (ROOT / name).read_text(encoding="utf-8")
        for other in EDITIONS:
            if other != name:
                assert f"]({other})" in text, (name, other)


def test_relative_links_resolve():
    """Every relative link in the READMEs points at a file or folder that exists."""
    broken = [
        (path.name, target)
        for path in [*(ROOT / name for name in EDITIONS), PLUGIN_README]
        for target in _relative_targets(path)
        if not (path.parent / target).exists()
    ]
    assert broken == []
