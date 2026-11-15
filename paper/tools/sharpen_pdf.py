#!/usr/bin/env python3
"""Replace the figures inside a PDF made by Word with their full-resolution sources.

Word for Mac writes every picture into the PDF at about 192 pixels per inch, whatever the size of
the file it was given, so fine lettering in a diagram comes out soft. This script swaps each figure
image in the finished PDF for the source PNG, flattened on white, without touching the page: an
image in a PDF is drawn into a unit square that the page scales, so only the pixels change.

Usage::

    uv run --no-project --with pikepdf --with pillow python paper/tools/sharpen_pdf.py \
        build/<name>/<name>.pdf build/<name>/fonte.md [--width 2400]

The figures are matched in order of appearance to the image lines of the build source. The script
stops without writing if the counts differ or if a source's proportions do not match the image it
would replace.
"""

from __future__ import annotations

import re
import sys
import zlib
from pathlib import Path

import pikepdf
from PIL import Image


def sources(markdown: Path) -> list[Path]:
    """Return the figure files of a build source, in order.

    Parameters
    ----------
    markdown : Path
        The derived Markdown that the exporter read (``fonte.md``).

    Returns
    -------
    list of Path
        Absolute paths of the images.
    """
    text = markdown.read_text(encoding="utf-8")
    found = re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", text)
    base = markdown.parent
    out = []
    for item in found:
        path = Path(item)
        for root in (
            base,
            Path(__file__).resolve().parents[1],
            Path(__file__).resolve().parents[2],
        ):
            if (root / path).exists():
                path = (root / path).resolve()
                break
        out.append(path)
    return out


def main() -> None:
    """Swap the figure images of the PDF and report what changed."""
    pdf_path, md_path = Path(sys.argv[1]), Path(sys.argv[2])
    width = int(sys.argv[sys.argv.index("--width") + 1]) if "--width" in sys.argv else 2400
    figures = sources(md_path)
    pdf = pikepdf.open(pdf_path, allow_overwriting_input=True)
    targets, seen = [], set()
    for number, page in enumerate(pdf.pages, 1):
        if number == 1:
            continue  # the cover holds the logo, which is not a figure of the paper
        for _name, obj in (page.get("/Resources", {}).get("/XObject", {}) or {}).items():
            if (
                obj.get("/Subtype") == "/Image"
                and obj.objgen not in seen
                and int(obj["/Width"]) > 300
            ):
                seen.add(obj.objgen)
                targets.append(obj)
    if len(targets) != len(figures):
        sys.exit(
            f"[FAIL] {len(targets)} figure images in the PDF, {len(figures)} in {md_path.name}"
        )
    plan = []
    for obj, path in zip(targets, figures, strict=True):
        im = Image.open(path).convert("RGBA")
        ratio_pdf = int(obj["/Width"]) / int(obj["/Height"])
        if abs(im.width / im.height - ratio_pdf) / ratio_pdf > 0.02:
            sys.exit(f"[FAIL] {path.name}: proportions differ from the image it would replace")
        flat = Image.new("RGB", im.size, "white")
        flat.paste(im, mask=im.split()[3])
        if flat.width > width:
            flat = flat.resize((width, round(width * flat.height / flat.width)), Image.LANCZOS)
        plan.append((obj, flat))
    for obj, flat in plan:
        before = int(obj["/Width"])
        obj.write(zlib.compress(flat.tobytes(), 9), filter=pikepdf.Name.FlateDecode)
        obj["/Width"], obj["/Height"] = flat.width, flat.height
        obj["/ColorSpace"], obj["/BitsPerComponent"] = pikepdf.Name.DeviceRGB, 8
        for key in ("/DecodeParms", "/SMask", "/Interpolate", "/Mask"):
            if key in obj:
                del obj[key]
        print(f"   {before} -> {flat.width} px")
    pdf.save(pdf_path)
    print(f"[OK] {len(plan)} figures replaced at up to {width} px in {pdf_path.name}")


if __name__ == "__main__":
    main()
