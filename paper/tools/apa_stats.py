#!/usr/bin/env python3
"""Write statistics the APA 7 way: no zero before the decimal mark of p, kappa or r; p to three decimals.

Used once to convert the four editions of a paper, and imported by the tests so that the numbers they expect
are written by the same rule (canon v1.6, rules SER-STYLE-001 and SER-STYLE-002).

Usage: python3 paper/tools/apa_stats.py <file.md> [<file.md> ...]     (rewrites the files in place)
"""
from __future__ import annotations

import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path


def p_text(value: float | str, sep: str = ".") -> str:
    """Return a p-value as APA 7 writes it, with its operator.

    Parameters
    ----------
    value : float or str
        The p-value.
    sep : str
        Decimal mark of the edition.

    Returns
    -------
    str
        ``"< .001"`` below one in a thousand, otherwise ``"= .0xx"`` with at most three decimals.
    """
    d = Decimal(str(value).replace(",", "."))
    if d < Decimal("0.001"):
        return f"< {sep}001"
    digits = str(value).replace(",", ".").split(".")[1] if "." in str(value).replace(",", ".") else ""
    q = d if len(digits) <= 3 else d.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    return "= " + sep + str(q).split(".")[1]


def convert(text: str) -> str:
    """Rewrite every p, kappa and bare threshold of a text.

    Parameters
    ----------
    text : str
        Markdown of one edition.

    Returns
    -------
    str
        The text with the statistics rewritten; code spans and addresses are left alone.
    """
    def p_sub(m: re.Match) -> str:
        op, sep, digits = m.group(2), m.group(3), m.group(4)
        if op == "=" or Decimal("0." + digits) < Decimal("0.001"):
            return m.group(1) + " " + p_text("0." + digits, sep)
        return f"{m.group(1)} {op} {sep}{digits}"

    parts = re.split(r"(`[^`\n]*`|https?://\S+)", text)
    for i in range(0, len(parts), 2):
        t = parts[i]
        t = re.sub(r"(?<![A-Za-z])(\*?p\*?)\s*([=<>≤≥])\s*0([.,])(\d+)", p_sub, t)
        t = re.sub(r"(κ\s*(?:=|is|é|es|è)\s*)0([.,]\d+)", r"\1\2", t)
        t = re.sub(r"(\((?:Cohen, 1960)\),? (?:is|é|es|è) )0([.,]\d+)", r"\1\2", t)
        parts[i] = t
    return "".join(parts)


if __name__ == "__main__":
    for name in sys.argv[1:]:
        path = Path(name)
        before = path.read_text(encoding="utf-8")
        after = convert(before)
        path.write_text(after, encoding="utf-8")
        print(name, "changed" if after != before else "unchanged")
