"""Turn the real-time recording of a live ASP run into the README GIF.

The recording (``asp-live.tape``) is made at real speed. This script keeps the opening (the
install, the project, the command) and the ending (the result) at real speed, and speeds up only
the wait in between, by a factor it prints and shows on screen in a badge for as long as it
applies. In the opening, a frozen screen (the marketplace clone) plays at most 4x faster;
typing and output stay at real speed. Nothing is cut and nothing is replayed.

The two cut points come from the run itself: ``t_show`` is the time the recording became visible,
and ``times.json`` (written by ``asp_view.py``) holds when the run started and when its result
arrived. Needs ffmpeg, gifsicle and CairoSVG::

    python make_gif.py --raw raw.mp4 --dir <folder with t_show and times.json> --out asp-live.gif
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

BADGE = """<svg xmlns="http://www.w3.org/2000/svg" width="200" height="36">
<rect width="200" height="36" rx="18" fill="#F5A524"/>
<text x="100" y="25" font-family="JetBrains Mono" font-weight="700" font-size="19"
 fill="#0B1B2B" text-anchor="middle">&#9654;&#9654; {k}&#215; faster</text></svg>"""


def cut_points(folder: Path, keep: float) -> tuple[float, float]:
    """Return the start and end, in video seconds, of the stretch to speed up.

    Parameters
    ----------
    folder : Path
        Folder holding ``t_show`` and ``times.json``.
    keep : float
        Seconds of the run kept at real speed after it starts, so the first actions read live.

    Returns
    -------
    tuple of float
        ``(start, end)`` of the sped-up stretch.
    """
    shown = float((folder / "t_show").read_text().strip())
    times = json.loads((folder / "times.json").read_text())
    return times["start"] - shown + keep, times["result"] - shown - 0.5


def main() -> None:
    """Build the GIF and print the speed-up factor."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--wait-seconds", type=float, default=14.0, help="length of the wait in the GIF"
    )
    parser.add_argument("--keep", type=float, default=1.0)
    args = parser.parse_args()
    import cairosvg

    start, end = cut_points(args.dir, args.keep)
    factor = max(2, round((end - start) / args.wait_seconds))
    badge = args.dir / "badge.png"
    cairosvg.svg2png(bytestring=BADGE.format(k=factor).encode(), write_to=str(badge))
    graph = (
        f"[0:v]trim=0:{start:.2f},setpts=PTS-STARTPTS,mpdecimate=max=3,setpts=N/FRAME_RATE/TB[a];"
        f"[0:v]trim={start:.2f}:{end:.2f},setpts=(PTS-STARTPTS)/{factor}[w];"
        "[w][1:v]overlay=W-w-16:4[b];"
        f"[0:v]trim=start={end:.2f},setpts=PTS-STARTPTS[c];"
        "[a][b][c]concat=n=3:v=1[v];"
        "[v]fps=10,scale=1100:-1:flags=lanczos,split[x][y];"
        "[x]palettegen=max_colors=64:stats_mode=diff[p];[y][p]paletteuse=dither=none"
    )
    raw = args.raw
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(raw),
            "-i",
            str(badge),
            "-filter_complex",
            graph,
            str(args.out),
        ],
        check=True,
    )
    subprocess.run(["gifsicle", "-O3", "--lossy=20", "--batch", str(args.out)], check=True)
    size = args.out.stat().st_size
    print(f"gif -> {args.out} | wait {end - start:.0f} s shown at {factor}x | {size} bytes")


if __name__ == "__main__":
    main()
