"""Chart of every estimate of the effect in the 2026-11b study, for the third paper.

One dot plot in percentage points: the originating study, this study by judge and by model, and
the checks. Saved with a transparent background. The diagrams of the paper are vector drawings
made by ``paper/tools/make_diagrams.py``.

Called by ``analysis/make_figures.py``; inputs are the studies' own result files.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
STUDY2 = ROOT / "benchmark" / "study-2026-11b"
STUDY1 = ROOT / "benchmark" / "study-2026-11"
INK, INK_2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
BLUE, ORANGE, NEUTRAL, PALE_BLUE, PALE_ORANGE = (
    "#2a78d6",
    "#eb6834",
    "#8a8985",
    "#eaf2fd",
    "#fdeee7",
)

TEXT = {
    "en": {
        "fx": "difference in coverage, sentence minus plain (percentage points)",
        "s1": "Originating study (6 tasks, Opus 5.5)",
        "s2": "This study (12 tasks, two models)",
        "checks": "Checks on this study",
        "rowsfx": ["primary judge", "second judge", "primary judge, pooled", "second judge, pooled",
                   "Opus 5.5", "Sonnet 5.5", "without the 3 error strata",
                   "error trials scored as full coverage", "tables of 10 rows only",
                   "second yardstick, worded differently"],
        "ci": "bar: 95% bootstrap interval",
    },
    "pt-BR": {
        "fx": "diferença de cobertura, com a frase menos sem a frase (pontos percentuais)",
        "s1": "Estudo de origem (6 tarefas, Opus 5.5)",
        "s2": "Este estudo (12 tarefas, dois modelos)",
        "checks": "Verificações neste estudo",
        "rowsfx": ["juiz principal", "segundo juiz", "juiz principal, combinado",
                   "segundo juiz, combinado", "Opus 5.5", "Sonnet 5.5",
                   "sem os 3 estratos com erro", "rodadas com erro como cobertura total",
                   "só tabelas de 10 linhas", "segunda régua, com outras palavras"],
        "ci": "barra: intervalo bootstrap de 95%",
    },
    "es": {
        "fx": "diferencia de cobertura, con la frase menos sin la frase (puntos porcentuales)",
        "s1": "Estudio de origen (6 tareas, Opus 5.5)",
        "s2": "Este estudio (12 tareas, dos modelos)",
        "checks": "Comprobaciones en este estudio",
        "rowsfx": ["juez principal", "segundo juez", "juez principal, conjunto",
                   "segundo juez, conjunto", "Opus 5.5", "Sonnet 5.5",
                   "sin los 3 estratos con error", "ejecuciones con error como cobertura total",
                   "solo tablas de 10 filas", "segunda vara de medir, con otras palabras"],
        "ci": "barra: intervalo bootstrap del 95%",
    },
    "it": {
        "fx": "differenza di copertura, con la frase meno senza la frase (punti percentuali)",
        "s1": "Studio di origine (6 compiti, Opus 5.5)",
        "s2": "Questo studio (12 compiti, due modelli)",
        "checks": "Verifiche su questo studio",
        "rowsfx": ["giudice principale", "secondo giudice", "giudice principale, complessivo",
                   "secondo giudice, complessivo", "Opus 5.5", "Sonnet 5.5",
                   "senza i 3 strati con errore", "prove con errore come copertura totale",
                   "solo tabelle di 10 righe", "secondo metro di misura, con altre parole"],
        "ci": "barra: intervallo bootstrap al 95%",
    },
}  # fmt: skip


def effects(lang: str):
    """Plot every estimate of the effect of the sentence, from both studies and the checks.

    Parameters
    ----------
    lang : str
        Edition language.

    Returns
    -------
    matplotlib.figure.Figure
        A dot plot in percentage points, with the bootstrap interval where one was computed.
    """
    t = TEXT[lang]
    one = json.loads((STUDY1 / "results.json").read_text())
    two = json.loads((STUDY2 / "results.json").read_text())
    two_b = json.loads((STUDY2 / "yardstick2" / "results2.json").read_text())
    sens = json.loads((STUDY2 / "sensitivity.json").read_text())
    desc = json.loads((STUDY2 / "descriptives.json").read_text())
    key = "RED-risk - RED-plain"
    opus, sonnet = "claude-opus-5-5", "claude-sonnet-5-5"
    values = [
        (one["gemini"]["secondary"][key]["delta_bar"], None),
        (one["grok"]["secondary"][key]["delta_bar"], None),
        (two["gemini"]["delta_bar"], desc["bootstrap_95"]),
        (two["grok"]["delta_bar"], None),
        (two["gemini"]["by_model"][opus], desc["bootstrap_95_by_model"][opus]),
        (two["gemini"]["by_model"][sonnet], desc["bootstrap_95_by_model"][sonnet]),
        (sens["gemini"]["without_strata"]["delta_bar"], None),
        (desc["errors_as_full_coverage"]["gemini"], None),
        (desc["full_tables_only"]["delta_bar"], None),
        (two_b["gemini"]["delta_bar"], None),
    ]
    groups = {0: t["s1"], 2: t["s2"], 6: t["checks"]}
    colors = [NEUTRAL, NEUTRAL, ORANGE, ORANGE, ORANGE, ORANGE, BLUE, BLUE, BLUE, BLUE]
    fig, ax = plt.subplots(figsize=(5.6, 3.95))  # small canvas: the lettering survives the scaling
    y, ticks, labels = 0.0, [], []
    for i, ((value, interval), label) in enumerate(zip(values, t["rowsfx"], strict=True)):
        if i in groups:
            y += 0.55
            # right-aligned at the axis like the rows: a long translated heading cannot cross it
            ax.text(-0.025, y, groups[i], fontsize=8, color=INK, fontweight="bold", va="center",
                    ha="right", transform=ax.get_yaxis_transform())  # fmt: skip
            y += 0.75
        if interval:
            ax.plot([interval[0] * 100, interval[1] * 100], [y, y], color=colors[i], linewidth=2.2,
                    alpha=0.45, solid_capstyle="round")  # fmt: skip
        ax.plot(value * 100, y, "o", color=colors[i], markersize=7, markeredgecolor="white",
                markeredgewidth=1.2)  # fmt: skip
        number = f"+{value * 100:.1f}"
        ax.text(19.3, y, number if lang == "en" else number.replace(".", ","), fontsize=7.6,
                color=INK, va="center", ha="right")  # fmt: skip
        ticks.append(y)
        labels.append(label)
        y += 0.75
    ax.axvline(0, color=INK_2, linewidth=1)
    ax.set_yticks(ticks, labels, fontsize=7.6)
    ax.set_ylim(y, -0.2)
    ax.set_xlim(-1, 19.5)
    ax.set_xlabel(t["fx"], fontsize=7.8, color=INK_2)
    ax.set_xticks([0, 5, 10, 15])
    ax.text(
        0.99,
        0.985,
        t["ci"],
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7,
        color=INK_2,
        style="italic",
    )
    ax.tick_params(axis="y", length=0)
    ax.tick_params(colors=INK_2, labelsize=7.6)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.34, right=0.98, top=0.99, bottom=0.12)
    return fig


DRAWINGS = {"fig13_effects": effects}
