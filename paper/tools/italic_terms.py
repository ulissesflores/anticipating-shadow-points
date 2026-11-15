#!/usr/bin/env python3
"""Put the listed foreign terms of a translated edition in italics (canon v1.6, rule SER-STYLE-003).

The term list comes from the canon's language layer. Code spans, addresses, link targets, literal quotations,
what is already in italics and the reference list are left alone, as the rule itself leaves them.

Usage: python3 paper/tools/italic_terms.py <lang> <file.md>     (rewrites the file in place; safe to run twice)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CANON = Path("/Users/ulissesflores/Developer/research-lab/metodo/templates/codex-hash-canon.json")
BOLD = "\x00"


def italicise(text: str, lang_cfg: dict) -> tuple[str, int]:
    """Return the text with every bare listed term wrapped in asterisks, and how many were wrapped."""
    terms = sorted(lang_cfg["foreign_terms_italic"], key=len, reverse=True)
    term = re.compile(r"(?<![\w*-])(" + "|".join(map(re.escape, terms)) + r")(?![\w*-])", re.I)
    keep = re.compile(
        r"(```.*?```|`[^`\n]*`|\]\([^)]*\)|https?://\S+|\"[^\"\n]*\"|“[^”\n]*”|\*[^*\n]+\*)", re.S
    )
    refs = lang_cfg["references_section_md"]
    head, sep, tail = text.partition(refs + "\n")
    nxt = re.search(r"^## ", tail, flags=re.M)
    skipped, rest = (tail[: nxt.start()], tail[nxt.start():]) if (sep and nxt) else (tail, "")
    n = 0

    def work(chunk: str) -> str:
        nonlocal n
        parts = keep.split(chunk.replace("**", BOLD))
        for i in range(0, len(parts), 2):
            parts[i], k = term.subn(r"*\1*", parts[i])
            n += k
        return "".join(parts).replace(BOLD, "**")

    return work(head) + sep + skipped + work(rest), n


if __name__ == "__main__":
    lang, name = sys.argv[1], sys.argv[2]
    cfg = json.loads(CANON.read_text(encoding="utf-8"))["i18n"]["langs"][lang]
    path = Path(name)
    new, count = italicise(path.read_text(encoding="utf-8"), cfg)
    path.write_text(new, encoding="utf-8")
    print(f"{name}: {count} term(s) put in italics")
