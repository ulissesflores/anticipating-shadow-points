#!/usr/bin/env python3
"""Report how far down each rendered page is filled, to catch near-blank pages before delivery.

Usage: python3 paper/tools/page_fill.py build/<name>/render [--min 0.45]
Reads the p-NN.png files written by the build (pdftoppm), finds the lowest row that holds ink
below the page header, and prints the pages filled to less than --min of the text area. The last
page of a block that the house norm starts on a new page (summaries, references, appendices,
Technical Note, About the Author) is listed too; read those by eye.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


def fill(path: Path) -> float:
    """Return the share of the text area of one page image that lies above its last inked row.

    Parameters
    ----------
    path : Path
        A rendered page (PNG).

    Returns
    -------
    float
        0.0 for an empty text area, 1.0 for a page inked down to the bottom margin.
    """
    im = Image.open(path).convert("L")
    w, h = im.size
    top, bottom = int(h * 0.09), int(h * 0.91)  # 1 inch margins of a Letter page
    px = im.load()
    last = top
    for y in range(bottom, top, -1):
        if any(px[x, y] < 200 for x in range(int(w * 0.1), int(w * 0.9), 3)):
            last = y
            break
    return (last - top) / (bottom - top)


def main() -> None:
    """Print the fill of every page and flag the thin ones."""
    folder = Path(sys.argv[1])
    limit = float(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 0.45
    thin = []
    for page in sorted(folder.glob("p-*.png")):
        share = fill(page)
        if share < limit:
            thin.append(f"{page.stem[2:]}:{share:.0%}")
    print("pages filled below", f"{limit:.0%}:", " ".join(thin) or "none")


if __name__ == "__main__":
    main()
