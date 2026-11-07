"""Figures as code, each tied to the claim it supports ("no figure without a claim").

Claim map
---------
fig1_silent_refusal_readings
    The July 2026 silent-refusal rate depends on how a decline is counted:
    18% (locked phrase detector) <= 24% (unambiguous declines) <= 38%
    (codebook majority) <= 40% (author label). The May 2026 detector reading
    (60%) is shown separately because it used a different model and CLI.
    Supports ``paper/iron-law-11.md`` section 3.
fig2_permutation_control
    Scoring each GREEN transcript against another task's expected list drops
    the deterministic match from 80% (diagonal) to 0.5% mean (max 10%), so the
    matcher discriminates task-specific content. Supports
    ``paper/asp-preprint.md`` section 5.2 (negative control).
fig3_red_green
    Per-evaluation deterministic match, RED vs GREEN (means 4% vs 80%), under
    an author-defined criterion. Supports ``paper/asp-preprint.md`` section 5.2.

Inputs come only from ``output/results.json``. Outputs: PNG + SVG in
``output/figures/``. Figures are informational in the provenance seal (not
hashed), because rasterisation varies by platform and library version.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "output" / "results.json"
FIGDIR = ROOT / "output" / "figures"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"  # categorical slot 1
ORANGE = "#eb6834"  # categorical slot 2
SEQ_BLUE = ["#f3f8fe", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0f3d75"]

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "svg.hashsalt": "asp-figures",
        "svg.fonttype": "none",
    }
)


def _save(fig, name: str) -> None:
    """Write one figure as PNG and SVG with stable metadata.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    name : str
        File stem.
    """
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGDIR / f"{name}.png", dpi=200, bbox_inches="tight", metadata={"Software": None})
    fig.savefig(FIGDIR / f"{name}.svg", bbox_inches="tight", metadata={"Date": None})
    plt.close(fig)


def _clean(ax) -> None:
    """Make axes recessive: no top/right spines, light horizontal grid.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to style.
    """
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def fig1(results: dict) -> None:
    """Dot-and-interval plot of the silent-refusal readings.

    Parameters
    ----------
    results : dict
        Contents of ``output/results.json``.
    """
    jul = results["iron_law_11"]["july_2026"]
    may = results["iron_law_11"]["may_2026"]
    rows = [
        (
            "May 2026 · locked phrase detector\nCC 2.1.143 · Opus 4.7",
            may["detector_silent_refusals"],
            ORANGE,
        ),
        ("Jul 2026 · locked phrase detector", jul["detector_silent_refusals"], BLUE),
        ("Jul 2026 · unambiguous declines only", jul["core_silent_refusals"], BLUE),
        ("Jul 2026 · codebook majority", jul["codebook_silent_refusals"], BLUE),
        (
            "Jul 2026 · author label\nCC 2.1.200 · Fable 5 (+ Opus 4.8 on safety)",
            jul["author_silent_refusals"],
            BLUE,
        ),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    for y, (_label, block, color) in enumerate(rows):
        lo, hi = block["wilson95"]
        ax.plot([lo * 100, hi * 100], [y, y], color=color, linewidth=2, solid_capstyle="round")
        ax.plot(
            block["rate"] * 100,
            y,
            "o",
            color=color,
            markersize=8,
            markeredgecolor=SURFACE,
            markeredgewidth=2,
        )
        ax.annotate(
            f"{block['k']}/{block['n']} = {block['rate'] * 100:.0f}%",
            (hi * 100, y),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            color=INK,
            fontsize=9,
        )
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=8.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel("exit 0 on a graceful decline, % of 50 refusal-provoking prompts (95% Wilson CI)")
    ax.set_title(
        "How often `claude -p` exits 0 on a decline depends on how a decline is counted",
        fontsize=10,
        loc="left",
    )
    _clean(ax)
    _save(fig, "fig1_silent_refusal_readings")


def fig2(results: dict) -> None:
    """Heatmap of the 5x5 label-permutation control.

    Parameters
    ----------
    results : dict
        Contents of ``output/results.json``.
    """
    bench = results["benchmark_2026_05"]
    ids = bench["eval_ids"]
    m = [[bench["permutation_matrix"][i][j] * 100 for j in ids] for i in ids]
    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list("seq_blue", SEQ_BLUE)
    fig, ax = plt.subplots(figsize=(4.6, 4.0))
    ax.imshow(m, cmap=cmap, vmin=0, vmax=100)
    for r, row in enumerate(m):
        for c, val in enumerate(row):
            ax.text(
                c,
                r,
                f"{val:.0f}%",
                ha="center",
                va="center",
                fontsize=9,
                color=SURFACE if val >= 50 else INK,
            )
    ax.set_xticks(range(len(ids)), ids)
    ax.set_yticks(range(len(ids)), ids)
    ax.set_xlabel("expected list scored against")
    ax.set_ylabel("GREEN transcript of task")
    for side in ax.spines.values():
        side.set_visible(False)
    diag = bench["permutation_diagonal_mean"] * 100
    off = bench["permutation_offdiagonal_mean"] * 100
    off_max = bench["permutation_offdiagonal_max"] * 100
    ax.set_title(
        f"Own list {diag:.0f}% · other task's list {off:.1f}% (max {off_max:.0f}%)",
        fontsize=10,
        loc="left",
    )
    _save(fig, "fig2_permutation_control")


def fig3(results: dict) -> None:
    """Plot RED vs GREEN deterministic match per evaluation as grouped bars.

    Parameters
    ----------
    results : dict
        Contents of ``output/results.json``.
    """
    bench = results["benchmark_2026_05"]
    ids = bench["eval_ids"]
    names = {
        "E1": "E1 schema migration",
        "E2": "E2 edge deploy",
        "E3": "E3 shared-util refactor",
        "E4": "E4 RLS policy",
        "E5": "E5 cron conflict",
    }
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    h = 0.36
    for k, eid in enumerate(ids):
        y = len(ids) - 1 - k
        for off, cond, color in ((h / 2 + 0.01, "red", ORANGE), (-h / 2 - 0.01, "green", BLUE)):
            val = bench[f"{cond}_coverage"][eid] * 100
            ax.barh(y + off, max(val, 0.6), height=h, color=color)
            ax.annotate(
                f"{val:.0f}%",
                (max(val, 0.6), y + off),
                xytext=(4, 0),
                textcoords="offset points",
                va="center",
                fontsize=8.5,
                color=INK,
            )
    ax.set_yticks(range(len(ids)), [names[e] for e in reversed(ids)], fontsize=9)
    ax.set_xlim(0, 110)
    ax.set_xlabel("deterministic match vs the author's expected list (%)")
    ax.legend(
        handles=[
            plt.Rectangle(
                (0, 0),
                1,
                1,
                color=ORANGE,
                label=f"RED, no ASP (mean {bench['red_mean'] * 100:.0f}%)",
            ),
            plt.Rectangle(
                (0, 0),
                1,
                1,
                color=BLUE,
                label=f"GREEN, ASP loaded (mean {bench['green_mean'] * 100:.0f}%)",
            ),
        ],
        frameon=False,
        loc="lower left",
        bbox_to_anchor=(0, 1.0),
        ncol=2,
        fontsize=8.5,
    )
    ax.set_title(
        "One transcript per cell: descriptive, not inferential", fontsize=10, loc="left", pad=24
    )
    _clean(ax)
    _save(fig, "fig3_red_green")


def main() -> None:
    """Render all figures from ``output/results.json``."""
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    fig1(results)
    fig2(results)
    fig3(results)
    print(f"figures -> {FIGDIR.relative_to(ROOT)} (3 x PNG+SVG)")


if __name__ == "__main__":
    main()
