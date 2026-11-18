"""Figures as code, each tied to the claim it supports ("no figure without a claim").

Claim map
---------
fig1_silent_refusal_readings
    The July 2026 silent-refusal rate depends on how a decline is counted:
    18% (locked phrase detector) <= 24% (unambiguous declines) <= 38%
    (codebook majority) <= 40% (author label). The May 2026 detector reading
    (60%) is shown separately because it used a different model and CLI.
    Supports ``paper/graceful-refusals.md`` section 3.
fig2_adjudicator_fixture_check
    Instrument check, not an effect of ASP: on the author-constructed GREEN
    fixtures of the mock benchmark run, the deterministic matcher scores 80%
    against each task's own expected list and 0.5% mean (max 10%) against the
    other tasks' lists, so it discriminates task-specific vocabulary. Supports
    ``paper/asp-preprint.md`` section 5.2. (A RED-vs-GREEN bar chart of the same
    fixtures was dropped in v2.0: it reads as an ASP effect, which it is not.)
fig3_study_2026_11_coverage
fig4_study_2026_11b_coverage
fig5_study_2026_11b_design, fig6_study_2026_11b_null, fig7_study_2026_11b_items,
fig8_study_2026_11b_timeline
    The 2026-11b study for ``paper/one-sentence-premortem.md``: its design, the permutation
    null against the observed difference, coverage of each reference risk, and the order of
    the sealed events.
    The pre-registered 2026-11 study: share of the blind reference risks that each
    condition's final table covers, per task and overall, by the primary judge.
    ASP (``/asp --standard``) is below the plain request that asks for the ways
    the change could go wrong on all six tasks (48% vs 66%), and that one-sentence
    request is above the plain "Plan this change." (66% vs 56%). Supports
    ``paper/asp-preprint.md`` (study section) and the README.

Inputs come only from ``output/results.json`` and, for fig3,
``benchmark/study-2026-11/results.json``. Outputs: PNG + SVG in
``output/figures/``. Figures are informational in the provenance seal (not
hashed), because rasterisation varies by platform and library version.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from study2_illustrations import DRAWINGS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "output" / "results.json"
STUDY = ROOT / "benchmark" / "study-2026-11" / "results.json"
STUDY2 = ROOT / "benchmark" / "study-2026-11b"
FIGDIR = ROOT / "output" / "figures"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"  # categorical slot 1
ORANGE = "#eb6834"  # categorical slot 2
NEUTRAL = "#8a8985"  # third series, recessive
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


def _save(fig, name: str, clear: bool = False, close: bool = True) -> None:
    """Write one figure as PNG and SVG with stable metadata.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    name : str
        File stem.
    clear : bool
        Save with a transparent background (figures placed on the white page of a paper).
    close : bool
        Close the figure afterwards; pass False to save the same drawing again under another name.
    """
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGDIR / f"{name}.png", dpi=400 if clear else 200, bbox_inches="tight",
                metadata={"Software": None}, transparent=clear)  # fmt: skip
    fig.savefig(FIGDIR / f"{name}.svg", bbox_inches="tight", metadata={"Date": None},
                transparent=clear)  # fmt: skip
    if close:
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


# Figure text per edition language; English is the canonical figure, the others
# are written next to it as <name>.<lang>.png/svg for the translated papers.
LABELS = {
    "en": {
        "all4": "All 12 tasks",
        "x4": "% of the blind reference risks covered by the final risk table "
        "(judge: Gemini; 5 trials per point)",
        "green": "ASP (/asp --standard)",
        "red_risk": 'Plain + "list what could go wrong"',
        "red_plain": 'Plain "Plan this change."',
        "all": "All 6 tasks",
        "x3": "% of the blind reference risks covered by the final risk"
        " table (judge: Gemini; 5 trials per task, 30 overall)",
        "may": "May 2026 · locked phrase detector\nCC 2.1.143 · Opus 4.7",
        "jul_detector": "Jul 2026 · locked phrase detector",
        "jul_core": "Jul 2026 · unambiguous declines only",
        "jul_codebook": "Jul 2026 · codebook majority",
        "jul_author": "Jul 2026 · author label\nCC 2.1.200 · Fable 5 (+ Opus 4.8 on safety)",
        "x1": "% of 50 refusal-provoking prompts counted as exit 0 on a decline,"
        " by the reading named at left (95% Wilson CI)",
        "x2": "expected list scored against",
        "y2": "author-constructed GREEN fixture of task",
    },
    "pt-BR": {
        "all4": "As 12 tarefas",
        "x4": "% dos riscos de referência cegos cobertos pela tabela final "
        "(juiz: Gemini; 5 rodadas por ponto)",
        "green": "ASP (/asp --standard)",
        "red_risk": 'Simples + "liste o que pode dar errado"',
        "red_plain": 'Simples "Planeje esta mudança."',
        "all": "As 6 tarefas",
        "x3": "% dos riscos de referência cegos cobertos pela tabela"
        " final (juiz: Gemini; 5 rodadas por tarefa, 30 no total)",
        "may": "Mai 2026 · detector de frases travado\nCC 2.1.143 · Opus 4.7",
        "jul_detector": "Jul 2026 · detector de frases travado",
        "jul_core": "Jul 2026 · só recusas inequívocas",
        "jul_codebook": "Jul 2026 · maioria do codebook",
        "jul_author": "Jul 2026 · rótulo do autor\nCC 2.1.200 · Fable 5 (+ Opus 4.8 em segurança)",
        "x1": "% dos 50 prompts que saem com 0 numa recusa,"
        " pela leitura indicada à esquerda (IC de Wilson 95%)",
        "x2": "lista esperada usada na pontuação",
        "y2": "fixture GREEN escrito pelo autor, da tarefa",
    },
    "es": {
        "all4": "Las 12 tareas",
        "x4": "% de los riesgos de referencia ciegos cubiertos por la tabla final "
        "(juez: Gemini; 5 ejecuciones por punto)",
        "green": "ASP (/asp --standard)",
        "red_risk": 'Simple + "enumera lo que puede salir mal"',
        "red_plain": 'Simple "Planifica este cambio."',
        "all": "Las 6 tareas",
        "x3": "% de los riesgos de referencia ciegos cubiertos por la tabla"
        " final (juez: Gemini; 5 ejecuciones por tarea, 30 en total)",
        "may": "May 2026 · detector de frases precintado\nCC 2.1.143 · Opus 4.7",
        "jul_detector": "Jul 2026 · detector de frases precintado",
        "jul_core": "Jul 2026 · solo rechazos inequívocos",
        "jul_codebook": "Jul 2026 · mayoría del codebook",
        "jul_author": "Jul 2026 · etiqueta del autor\n"
        "CC 2.1.200 · Fable 5 (+ Opus 4.8 en seguridad)",
        "x1": "% de los 50 prompts que salen con 0 en un rechazo,"
        " según la lectura indicada a la izquierda (IC de Wilson 95%)",
        "x2": "lista esperada usada para puntuar",
        "y2": "fixture GREEN escrito por el autor, de la tarea",
    },
    "it": {
        "all4": "I 12 compiti",
        "x4": "% dei rischi di riferimento ciechi coperti dalla tabella finale "
        "(giudice: Gemini; 5 prove per punto)",
        "green": "ASP (/asp --standard)",
        "red_risk": 'Semplice + "elenca cosa può andare storto"',
        "red_plain": 'Semplice "Pianifica questa modifica."',
        "all": "Tutti i 6 compiti",
        "x3": "% dei rischi di riferimento ciechi coperti dalla tabella"
        " finale (giudice: Gemini; 5 esecuzioni per compito, 30 in totale)",
        "may": "Mag 2026 · rilevatore di frasi bloccato\nCC 2.1.143 · Opus 4.7",
        "jul_detector": "Lug 2026 · rilevatore di frasi bloccato",
        "jul_core": "Lug 2026 · solo rifiuti inequivocabili",
        "jul_codebook": "Lug 2026 · maggioranza del codebook",
        "jul_author": "Lug 2026 · etichetta dell'autore\n"
        "CC 2.1.200 · Fable 5 (+ Opus 4.8 sulla sicurezza)",
        "x1": "% dei 50 prompt che escono con 0 su un rifiuto,"
        " secondo la lettura indicata a sinistra (IC di Wilson 95%)",
        "x2": "lista attesa usata per il punteggio",
        "y2": "fixture GREEN scritta dall'autore, del compito",
    },
}


def fig1(results: dict, lang: str = "en") -> None:
    """Dot-and-interval plot of the silent-refusal readings.

    Parameters
    ----------
    results : dict
        Contents of ``output/results.json``.
    lang : str
        Edition language, a key of ``LABELS``.
    """
    t = LABELS[lang]
    jul = results["iron_law_11"]["july_2026"]
    may = results["iron_law_11"]["may_2026"]
    rows = [
        (
            t["may"],
            may["detector_silent_refusals"],
            ORANGE,
        ),
        (t["jul_detector"], jul["detector_silent_refusals"], BLUE),
        (t["jul_core"], jul["core_silent_refusals"], BLUE),
        (t["jul_codebook"], jul["codebook_silent_refusals"], BLUE),
        (
            t["jul_author"],
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
    ax.set_xlabel(t["x1"])
    _clean(ax)
    suffix = "" if lang == "en" else f".{lang}"
    _save(fig, "fig1_silent_refusal_readings" + suffix, close=False)
    _save(fig, "fig1_silent_refusal_readings_clear" + suffix, clear=True)  # the same drawing without a background, for the paper


def fig2(results: dict, lang: str = "en") -> None:
    """Heatmap of the 5x5 adjudicator check on the constructed fixtures.

    Parameters
    ----------
    results : dict
        Contents of ``output/results.json``.
    lang : str
        Edition language, a key of ``LABELS``.
    """
    t = LABELS[lang]
    bench = results["adjudicator_fixture_check_2026_05"]
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
    ax.set_xlabel(t["x2"])
    ax.set_ylabel(t["y2"])
    for side in ax.spines.values():
        side.set_visible(False)
    suffix = "" if lang == "en" else f".{lang}"
    _save(fig, "fig2_adjudicator_fixture_check" + suffix, close=False)
    _save(fig, "fig2_adjudicator_fixture_check_clear" + suffix, clear=True)  # the same drawing without a background, for the paper


def fig3(study: dict, lang: str = "en") -> None:
    """Per-task coverage of the three conditions of the 2026-11 study (primary judge).

    Parameters
    ----------
    study : dict
        Contents of ``benchmark/study-2026-11/results.json``.
    lang : str
        Edition language, a key of ``LABELS``.
    """
    t = LABELS[lang]
    means = study["gemini"]["means"]
    tasks = sorted(means)
    series = [("RED-plain", t["red_plain"], NEUTRAL), ("RED-risk", t["red_risk"], ORANGE),
              ("GREEN", t["green"], BLUE)]  # fmt: skip
    overall = study["gemini"]["overall"]
    rows = [*tasks, t["all"]]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    for k, (cond, label, color) in enumerate(series):
        xs = [means[task][cond] * 100 for task in tasks] + [overall[cond] * 100]
        ys = [y + (k - 1) * 0.18 for y in range(len(rows))]
        ax.plot(xs, ys, "o", color=color, markersize=7, markeredgecolor=SURFACE,
                markeredgewidth=1.5, label=label)  # fmt: skip
    ax.axhline(len(tasks) - 0.5, color=GRID, linewidth=1)
    ax.set_yticks(range(len(rows)), rows)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel(t["x3"], fontsize=8.5)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=8)
    _clean(ax)
    _save(fig, "fig3_study_2026_11_coverage" + ("" if lang == "en" else f".{lang}"))
    fig, ax = plt.subplots(
        figsize=(7.2, 3.8)
    )  # the same drawing without a background, for the third paper
    for k, (cond, label, color) in enumerate(series):
        xs = [means[task][cond] * 100 for task in tasks] + [overall[cond] * 100]
        ys = [y + (k - 1) * 0.18 for y in range(len(rows))]
        ax.plot(xs, ys, "o", color=color, markersize=7, markeredgecolor="white",
                markeredgewidth=1.5, label=label)  # fmt: skip
    ax.axhline(len(tasks) - 0.5, color=GRID, linewidth=1)
    ax.set_yticks(range(len(rows)), rows)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel(t["x3"], fontsize=8.5)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=8)
    _clean(ax)
    _save(fig, "fig3_study_2026_11_coverage_clear" + ("" if lang == "en" else f".{lang}"),
          clear=True)  # fmt: skip


def fig4(desc: dict, overall: dict, lang: str = "en") -> None:
    """Per-task coverage of the two conditions of the 2026-11b study, one panel per model.

    Parameters
    ----------
    desc : dict
        Contents of ``benchmark/study-2026-11b/descriptives.json``.
    overall : dict
        ``{model: {condition: coverage}}``, the mean over that model's twelve strata.
    lang : str
        Edition language, a key of ``LABELS``.
    """
    t = LABELS[lang]
    tasks = sorted(desc["per_task"])
    rows = [*tasks, t["all4"]]
    models = [("claude-opus-5-5", "Claude Opus 5.5"), ("claude-sonnet-5-5", "Claude Sonnet 5.5")]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.6), sharey=True)
    for ax, (model, title) in zip(axes, models, strict=True):
        plain = [desc["per_task"][k][model]["RED-plain"] * 100 for k in tasks]
        risk = [desc["per_task"][k][model]["RED-risk"] * 100 for k in tasks]
        plain.append(overall[model]["RED-plain"] * 100)
        risk.append(overall[model]["RED-risk"] * 100)
        ys = list(range(len(rows)))
        for y, a, b in zip(ys, plain, risk, strict=True):
            ax.plot([a, b], [y, y], color=GRID, linewidth=2.2, zorder=1)
        ax.plot(plain, ys, "o", color=NEUTRAL, markersize=7, markeredgecolor=SURFACE,
                markeredgewidth=1.5, label=t["red_plain"], zorder=2)  # fmt: skip
        ax.plot(risk, ys, "o", color=ORANGE, markersize=7, markeredgecolor=SURFACE,
                markeredgewidth=1.5, label=t["red_risk"], zorder=3)  # fmt: skip
        ax.axhline(len(tasks) - 0.5, color=GRID, linewidth=1)
        ax.set_yticks(ys, rows)
        ax.set_xlim(0, 100)
        ax.set_title(title, fontsize=9, loc="left")
        _clean(ax)
    axes[0].invert_yaxis()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 0.98), ncol=2,
               frameon=False, fontsize=8)  # fmt: skip
    fig.supxlabel(t["x4"], fontsize=8.5, color=INK_2)
    fig.tight_layout()
    _save(fig, "fig4_study_2026_11b_coverage" + ("" if lang == "en" else f".{lang}"), clear=True)


# Text of the study-2 figures added for the third paper, per edition language.
STUDY2_LABELS = {
    "en": {
        "null_x": "difference in coverage, sentence minus plain (percentage points)",
        "null_y": "shuffles (of 10,000)",
        "null_label": "labels shuffled within each task and model",
        "observed": "observed\n+{v} points",
        "largest": "largest shuffle\n+{v}",
        "item_x": "% of plain trials that cover the reference risk",
        "item_y": "% of trials with the sentence that cover it",
        "item_same": "same in both",
        "item_n": "each dot is one of the 100 reference risks (10 trials per condition)",
    },
    "pt-BR": {
        "null_x": "diferença de cobertura, com a frase menos sem a frase (pontos percentuais)",
        "null_y": "embaralhamentos (de 10.000)",
        "null_label": "rótulos embaralhados dentro de cada tarefa e modelo",
        "observed": "observado\n+{v} pontos",
        "largest": "maior embaralhamento\n+{v}",
        "item_x": "% das rodadas simples que cobrem o risco de referência",
        "item_y": "% das rodadas com a frase que o cobrem",
        "item_same": "igual nas duas",
        "item_n": "cada ponto é um dos 100 riscos de referência (10 rodadas por condição)",
    },
    "es": {
        "null_x": "diferencia de cobertura, con la frase menos sin la frase (puntos porcentuales)",
        "null_y": "permutaciones (de 10.000)",
        "null_label": "etiquetas permutadas dentro de cada tarea y modelo",
        "observed": "observado\n+{v} puntos",
        "largest": "mayor permutación\n+{v}",
        "item_x": "% de las ejecuciones simples que cubren el riesgo de referencia",
        "item_y": "% de las ejecuciones con la frase que lo cubren",
        "item_same": "igual en ambas",
        "item_n": "cada punto es uno de los 100 riesgos de referencia (10 ejecuciones "
        "por condición)",
    },
    "it": {
        "null_x": "differenza di copertura, con la frase meno senza la frase (punti percentuali)",
        "null_y": "permutazioni (su 10.000)",
        "null_label": "etichette permutate entro ogni compito e modello",
        "observed": "osservato\n+{v} punti",
        "largest": "permutazione massima\n+{v}",
        "item_x": "% delle prove semplici che coprono il rischio di riferimento",
        "item_y": "% delle prove con la frase che lo coprono",
        "item_same": "uguale in entrambe",
        "item_n": "ogni punto è uno dei 100 rischi di riferimento (10 prove per condizione)",
    },
}


def _num(x: float, lang: str) -> str:
    """Format a number of percentage points with the decimal mark of the edition language.

    Parameters
    ----------
    x : float
        Value in percentage points.
    lang : str
        Edition language.

    Returns
    -------
    str
        One decimal place, with a comma outside English.
    """
    text = f"{x:.1f}"
    return text if lang == "en" else text.replace(".", ",")


def fig6(desc: dict, lang: str = "en") -> None:
    """Permutation null of the primary statistic of the 2026-11b study, with the observed value.

    Parameters
    ----------
    desc : dict
        Contents of ``benchmark/study-2026-11b/descriptives.json``.
    lang : str
        Edition language.
    """
    t = STUDY2_LABELS[lang]
    null = desc["null"]
    xs = [float(k) * 100 for k in null["bins"]]
    width = null["bin_width"] * 100
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.bar(xs, list(null["bins"].values()), width=width * 0.92, align="edge", color=NEUTRAL,
           label=t["null_label"])  # fmt: skip
    obs, top = null["observed"] * 100, null["largest_shuffled"] * 100
    ymax = max(null["bins"].values())
    ax.axvline(obs, color=ORANGE, linewidth=2)
    ax.text(obs - 0.25, ymax * 0.78, t["observed"].format(v=_num(obs, lang)), color=ORANGE,
            ha="right", fontsize=8.5)  # fmt: skip
    ax.axvline(top, color=INK_2, linewidth=1, linestyle=":")
    ax.text(top + 0.15, ymax * 0.42, t["largest"].format(v=_num(top, lang)), color=INK_2,
            ha="left", fontsize=8)  # fmt: skip
    ax.set_xlim(-8, 13)
    ax.set_ylim(0, ymax * 1.2)  # headroom: the legend sits above the tallest bar, not on it
    if lang != "en":  # tick labels with the decimal mark of the edition, like the text around the figure
        ax.xaxis.set_major_formatter(lambda v, _pos: _num(v, lang).replace("-", "\u2212"))
    ax.set_xlabel(t["null_x"], fontsize=8.5)
    ax.set_ylabel(t["null_y"], fontsize=8.5)
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    _save(fig, "fig6_study_2026_11b_null" + ("" if lang == "en" else f".{lang}"), clear=True)


def fig7(desc: dict, lang: str = "en") -> None:
    """Coverage of each reference risk of the 2026-11b study, plain against sentence.

    Parameters
    ----------
    desc : dict
        Contents of ``benchmark/study-2026-11b/descriptives.json``.
    lang : str
        Edition language.
    """
    from collections import Counter

    t = STUDY2_LABELS[lang]
    items = desc["by_item"]["items"]
    counts = Counter(
        (round(v["RED-plain"] * 100), round(v["RED-risk"] * 100)) for v in items.values()
    )
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.plot([0, 100], [0, 100], color=GRID, linewidth=1.2, label=t["item_same"])
    for (x, y), n in counts.items():
        color = ORANGE if y > x else (NEUTRAL if y == x else BLUE)
        ax.scatter(x, y, s=30 * n, color=color, edgecolor=SURFACE, linewidth=0.8, zorder=3)
        if n > 1:
            ax.text(x, y, str(n), ha="center", va="center", fontsize=6.5, color=SURFACE, zorder=4)
    ax.set_xlim(-6, 106)
    ax.set_ylim(-6, 106)
    ax.set_xlabel(t["item_x"], fontsize=8.5)
    ax.set_ylabel(t["item_y"], fontsize=8.5)
    ax.set_title(t["item_n"], fontsize=7.5, color=INK_2, loc="left")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    _save(fig, "fig7_study_2026_11b_items" + ("" if lang == "en" else f".{lang}"), clear=True)


def main() -> None:
    """Render all figures from ``output/results.json``."""
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    desc = json.loads((STUDY2 / "descriptives.json").read_text(encoding="utf-8"))
    overall = {
        m: {
            c: sum(desc["per_task"][k][m][c] for k in desc["per_task"]) / len(desc["per_task"])
            for c in ("RED-plain", "RED-risk")
        }
        for m in ("claude-opus-5-5", "claude-sonnet-5-5")
    }
    for lang in LABELS:
        fig1(results, lang)
        fig2(results, lang)
        fig3(study, lang)
        with plt.rc_context(
            {"font.family": ["Helvetica Neue", "DejaVu Sans"]}
        ):  # the paper's charts
            fig4(desc, overall, lang)
            fig6(desc, lang)
            fig7(desc, lang)
            for name, draw in DRAWINGS.items():
                _save(draw(lang), name + ("" if lang == "en" else f".{lang}"), clear=True)
    print(f"figures -> {FIGDIR.relative_to(ROOT)} (8 x PNG+SVG, plus pt-BR, es, it editions)")


if __name__ == "__main__":
    main()
