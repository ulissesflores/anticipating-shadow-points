"""Brand assets for ASP, drawn as code: icon, README banners, social preview, phase diagram.

Claim map (no picture without a claim):

- ``icon*.svg``: the "A" monogram. The shadow inside the A ends in one amber point: the
  failure seen before it happens.
- ``banner-{dark,light}.svg``: the README hero, "Plan before you code."
- ``phases-{dark,light}.svg``: the protocol in six stages; the pre-mortem is the highlighted
  stage because it is what the plugin adds to a plain request.
- ``social-preview.png``: the image GitHub shows when the repository link is shared.

All text is converted to outlines with fontTools, so the SVGs look the same on every screen
and need no installed font. Fonts used (SIL Open Font License 1.1, not redistributed here):
Space Grotesk 500 and 700, and Inter 600, as published by Fontsource
(https://fontsource.org). Run::

    python assets/brand/make_brand.py --fonts <folder with the three .woff files>

``--png`` also renders PNG copies with CairoSVG (needs the cairo library).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

OUT = Path(__file__).resolve().parent
FONT_FILES = {
    "display": "space-grotesk-latin-700-normal.woff",
    "label": "space-grotesk-latin-500-normal.woff",
    "body": "inter-latin-600-normal.woff",
}
NAVY, AMBER, AMBER_ON_LIGHT, WHITE = "#0B1B2B", "#F5A524", "#B86E00", "#FFFFFF"
THEMES = {
    "dark": {
        "bg": "#0D1117",
        "grid": "#161B22",
        "ink": WHITE,
        "shadow": "#22405F",
        "accent": AMBER,
        "muted": "#8B949E",
        "box": "#161B22",
        "stroke": "#30363D",
    },
    "light": {
        "bg": "#F6F8FA",
        "grid": "#E8ECF0",
        "ink": NAVY,
        "shadow": "#2E5070",
        "accent": AMBER_ON_LIGHT,
        "muted": "#57606A",
        "box": WHITE,
        "stroke": "#D0D7DE",
    },
}


class Fonts:
    """Turn strings into SVG outline paths.

    Parameters
    ----------
    folder : Path
        Folder holding the files named in ``FONT_FILES``.
    """

    def __init__(self, folder: Path) -> None:
        """Open the three faces named in ``FONT_FILES``."""
        self.faces = {key: TTFont(folder / name) for key, name in FONT_FILES.items()}

    def width(self, face: str, text: str, size: float, tracking: float = 0.0) -> float:
        """Return the advance width of ``text``.

        Parameters
        ----------
        face : str
            Key in ``FONT_FILES``.
        text : str
            The string.
        size : float
            Font size in user units.
        tracking : float
            Extra space after each character, in user units.

        Returns
        -------
        float
            Width in user units.
        """
        font = self.faces[face]
        cmap, hmtx = font.getBestCmap(), font["hmtx"]
        scale = size / font["head"].unitsPerEm
        return sum(hmtx[cmap[ord(ch)]][0] * scale + tracking for ch in text) - tracking

    def path(
        self,
        face: str,
        text: str,
        x: float,
        y: float,
        size: float,
        fill: str,
        tracking: float = 0.0,
        anchor: str = "start",
    ) -> str:
        """Return ``text`` as one SVG ``<path>`` whose baseline starts at ``(x, y)``.

        Parameters
        ----------
        face : str
            Key in ``FONT_FILES``.
        text : str
            The string.
        x, y : float
            Baseline position.
        size : float
            Font size in user units.
        fill : str
            Fill colour.
        tracking : float
            Extra space after each character.
        anchor : str
            ``"start"``, ``"middle"`` or ``"end"``, as in SVG ``text-anchor``.

        Returns
        -------
        str
            An SVG ``<path>`` element.
        """
        font = self.faces[face]
        cmap, hmtx, glyphs = font.getBestCmap(), font["hmtx"], font.getGlyphSet()
        scale = size / font["head"].unitsPerEm
        width = self.width(face, text, size, tracking)
        cursor = x - {"start": 0.0, "middle": width / 2, "end": width}[anchor]
        parts = []
        for ch in text:
            name = cmap[ord(ch)]
            pen = SVGPathPen(glyphs, ntos=lambda n: f"{n:.1f}".rstrip("0").rstrip("."))
            glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, y)))
            parts.append(pen.getCommands())
            cursor += hmtx[name][0] * scale + tracking
        return f'<path fill="{fill}" d="{" ".join(p for p in parts if p)}"/>'


def monogram(x: float, y: float, size: float, ink: str, shadow: str, dot: str) -> str:
    """Return the "A" monogram drawn in a ``size`` x ``size`` box at ``(x, y)``.

    Parameters
    ----------
    x, y : float
        Top-left corner of the box.
    size : float
        Side of the box.
    ink, shadow, dot : str
        Colours of the A, of the shadow inside it and of the point.

    Returns
    -------
    str
        An SVG ``<g>`` element.
    """
    s = size / 1000
    return (
        f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.5f})">'
        f'<path fill="{ink}" d="M500 110 L890 880 L748 880 L500 382 L252 880 L110 880 Z"/>'
        f'<path fill="{shadow}" d="M500 440 L604 640 L500 790 L396 640 Z"/>'
        f'<circle fill="{dot}" cx="500" cy="800" r="50"/>'
        "</g>"
    )


def svg(width: int, height: int, body: str, title: str) -> str:
    """Wrap ``body`` in an accessible SVG document.

    Parameters
    ----------
    width, height : int
        Canvas size.
    body : str
        SVG elements.
    title : str
        Accessible name.

    Returns
    -------
    str
        The SVG document.
    """
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">'
        f"<title>{title}</title>{body}</svg>\n"
    )


def grid(width: int, height: int, colour: str, step: int = 32) -> str:
    """Return a faint background grid.

    Parameters
    ----------
    width, height : int
        Canvas size.
    colour : str
        Line colour.
    step : int
        Spacing between lines.

    Returns
    -------
    str
        An SVG ``<path>`` element.
    """
    lines = [f"M{x} 0V{height}" for x in range(step, width, step)]
    lines += [f"M0 {y}H{width}" for y in range(step, height, step)]
    return f'<path stroke="{colour}" stroke-width="1" fill="none" d="{" ".join(lines)}"/>'


def icon_tile() -> str:
    """Return the plugin icon: white A on a navy rounded tile, legible on light and dark UIs.

    Returns
    -------
    str
        The SVG document.
    """
    body = f'<rect width="1024" height="1024" rx="224" fill="{NAVY}"/>' + monogram(
        112, 96, 800, WHITE, "#2E5070", AMBER
    )
    return svg(1024, 1024, body, "ASP icon: a shadow inside the letter A ends in one amber point")


def banner(fonts: Fonts, theme: str) -> str:
    """Return the 1280x320 README banner.

    Parameters
    ----------
    fonts : Fonts
        Loaded fonts.
    theme : str
        ``"dark"`` or ``"light"``.

    Returns
    -------
    str
        The SVG document.
    """
    t = THEMES[theme]
    body = (
        f'<rect width="1280" height="320" fill="{t["bg"]}"/>'
        + grid(1280, 320, t["grid"])
        + monogram(64, 64, 190, t["ink"], t["shadow"], AMBER)
        + fonts.path("display", "ASP", 268, 196, 132, t["ink"], tracking=2)
        + fonts.path("label", "ANTICIPATING SHADOW POINTS", 272, 240, 21, t["accent"], tracking=3.2)
        + fonts.path("display", "Plan before", 1216, 150, 68, t["accent"], anchor="end")
        + fonts.path("display", "you code.", 1216, 228, 68, t["accent"], anchor="end")
    )
    return svg(1280, 320, body, "ASP, Anticipating Shadow Points: plan before you code")


def social_preview(fonts: Fonts) -> str:
    """Return the 1280x640 image GitHub shows when the repository link is shared.

    Parameters
    ----------
    fonts : Fonts
        Loaded fonts.

    Returns
    -------
    str
        The SVG document.
    """
    t = THEMES["dark"]
    body = (
        f'<rect width="1280" height="640" fill="{t["bg"]}"/>'
        + grid(1280, 640, t["grid"])
        + monogram(170, 120, 260, t["ink"], t["shadow"], AMBER)
        + fonts.path("display", "ASP", 460, 300, 190, t["ink"], tracking=3)
        + fonts.path("label", "ANTICIPATING SHADOW POINTS", 466, 360, 30, AMBER, tracking=4.5)
        + fonts.path("display", "Plan before you code.", 640, 480, 76, AMBER, anchor="middle")
        + fonts.path(
            "body",
            "A pre-mortem for your coding agent, in one command  ·  Claude Code plugin",
            640,
            560,
            26,
            t["muted"],
            anchor="middle",
        )
    )
    return svg(1280, 640, body, "ASP: plan before you code. A pre-mortem for your coding agent")


STAGES = [
    ("Research", "codebase, prior art, lessons"),
    ("Pre-mortem", "14 MAST failure modes"),
    ("Plan + check", "an independent subagent"),
    ("You approve", "charter, plan, deliverables"),
    ("Execute", "tasks with acceptance tests"),
    ("Sign off", "evidence per deliverable"),
]


def phases(fonts: Fonts, theme: str) -> str:
    """Return the protocol drawn as six stages, the pre-mortem highlighted.

    Parameters
    ----------
    fonts : Fonts
        Loaded fonts.
    theme : str
        ``"dark"`` or ``"light"``.

    Returns
    -------
    str
        The SVG document.
    """
    t = THEMES[theme]
    w, gap, x0, top, h = 186, 26, 23, 40, 150
    body = [f'<rect width="1280" height="230" rx="16" fill="{t["bg"]}"/>']
    for i, (name, note) in enumerate(STAGES):
        x = x0 + i * (w + gap)
        hot = name == "Pre-mortem"
        body.append(
            f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="14" fill="{t["box"]}" '
            f'stroke="{t["accent"] if hot else t["stroke"]}" stroke-width="{3 if hot else 1.5}"/>'
        )
        body.append(f'<circle cx="{x + 34}" cy="{top + 36}" r="17" fill="{AMBER}"/>')
        body.append(fonts.path("display", str(i + 1), x + 34, top + 44, 22, NAVY, anchor="middle"))
        body.append(fonts.path("display", name, x + 18, top + 98, 25, t["ink"]))
        note_size = min(14.0, 14.0 * (w - 34) / fonts.width("body", note, 14.0))  # fit the box
        body.append(fonts.path("body", note, x + 18, top + 128, note_size, t["muted"]))
        if i < len(STAGES) - 1:
            ax = x + w + 4
            body.append(
                f'<path d="M{ax} {top + h / 2} h{gap - 10} m-7 -6 l7 6 l-7 6" fill="none" '
                f'stroke="{t["muted"]}" stroke-width="2" stroke-linecap="round" '
                'stroke-linejoin="round"/>'
            )
    return svg(
        1280, 230, "".join(body), "The ASP protocol in six stages; the pre-mortem is stage 2"
    )


def main() -> None:
    """Write every asset into this folder; optionally render PNG copies."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fonts", type=Path, required=True)
    parser.add_argument("--png", action="store_true")
    args = parser.parse_args()
    fonts = Fonts(args.fonts)
    files = {
        "icon.svg": icon_tile(),
        "banner-dark.svg": banner(fonts, "dark"),
        "banner-light.svg": banner(fonts, "light"),
        "phases-dark.svg": phases(fonts, "dark"),
        "phases-light.svg": phases(fonts, "light"),
        "social-preview.svg": social_preview(fonts),
    }
    for name, text in files.items():
        (OUT / name).write_text(text, encoding="utf-8")
    if args.png:
        import cairosvg

        cairosvg.svg2png(
            url=str(OUT / "social-preview.svg"), write_to=str(OUT / "social-preview.png")
        )
    print("brand ->", OUT, "|", ", ".join(files))


if __name__ == "__main__":
    main()
