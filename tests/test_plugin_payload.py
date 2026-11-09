"""What a plugin install copies: only the plugin folder, and only inert files.

The Anthropic directory installs ``plugins/anticipating-shadow-points/`` and reviews everything in
it. These tests keep that folder free of scripts, binaries and paths that only exist on the
author's machine, and keep the self-hosted marketplace pointing at it.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "anticipating-shadow-points"
FROZEN_EVALS = PLUGIN / "skills" / "anticipating-shadow-points" / "evals"
INERT = {".md", ".json", ".svg"}


def _payload() -> list[Path]:
    """List every file an install of the plugin copies: the ones git tracks in its folder.

    Untracked local files (``.DS_Store`` from Finder, editor backups) never reach an install, so
    they are left out; without git the folder is read from disk.

    Returns
    -------
    list of Path
        Files under the plugin folder, sorted.
    """
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z", "--", str(PLUGIN.relative_to(ROOT))],
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout.decode()
        files = [ROOT / name for name in out.split("\0") if name]
    except (OSError, subprocess.CalledProcessError):
        files = [p for p in PLUGIN.rglob("*") if p.is_file()]
    return sorted(files)


def test_payload_is_inert():
    """The plugin ships Markdown, JSON, one SVG icon and the licence: nothing executable."""
    odd = [
        p.relative_to(PLUGIN).as_posix()
        for p in _payload()
        if p.suffix not in INERT and p.name != "LICENSE"
    ]
    assert odd == []
    assert not (PLUGIN / "hooks").exists()
    assert not (PLUGIN / ".mcp.json").exists()
    assert not (PLUGIN / "bin").exists()


def test_no_author_machine_paths_or_permission_bypass():
    """No path from the author's machine and no permission-bypass flag in the shipped text."""
    banned = ("/Users/", "Developer/ASP/runtime", "bypassPermissions", "dangerously-skip")
    hits = [
        (p.relative_to(PLUGIN).as_posix(), word)
        for p in _payload()
        if p.parent != FROZEN_EVALS  # evals are frozen benchmark inputs, sealed byte for byte
        for word in banned
        if word in p.read_text(encoding="utf-8", errors="replace")
    ]
    assert hits == []


def test_manifest_has_listing_fields():
    """The directory listing reads its icon and links from plugin.json."""
    manifest = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    for key in ("icon", "documentationUrl", "supportUrl", "privacyPolicyUrl", "description"):
        assert manifest.get(key), key
    assert (PLUGIN / manifest["icon"]).is_file()
    assert (PLUGIN / "README.md").is_file() and (PLUGIN / "LICENSE").is_file()


def test_marketplace_points_at_plugin_folder():
    """The self-hosted marketplace installs the plugin folder, not the research repository."""
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    sources = [entry["source"] for entry in market["plugins"]]
    assert sources == ["./plugins/anticipating-shadow-points"]
    assert not (ROOT / ".claude-plugin" / "plugin.json").exists()


def test_icon_copies_match():
    """The README icon and the plugin icon are the same file."""
    root_icon = (ROOT / "assets" / "icon.svg").read_bytes()
    assert (PLUGIN / "assets" / "icon.svg").read_bytes() == root_icon
