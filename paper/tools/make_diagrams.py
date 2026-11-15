#!/usr/bin/env python3
"""Draw the diagrams of ``paper/one-sentence-premortem.md`` as vector graphics, one set per language.

Each diagram is written as SVG on a fixed grid, with one type scale and one palette, and rendered
to a 3000-pixel PNG with a transparent background (the paper's build embeds the PNG). The numbers,
fingerprints and example answers are read from the study's files, never typed here; only wording
that the files do not hold (labels, and the translations of the literal English strings) lives in
``TEXT``. The charts of measured data stay in ``analysis/make_figures.py``.

Usage::

    uv run --with resvg-py python paper/tools/make_diagrams.py [--lang pt-BR]

Output: ``paper/figures/<name>[.<lang>].svg`` and ``.png``.
"""

from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "benchmark" / "study-2026-11b"
OUT = ROOT / "paper" / "figures"
W = 1000  # drawing width; the paper prints every figure 14 cm wide, so 22 px here is about 8.7 pt
INK, MUTED, RULE, PAPER = "#1b1b1b", "#5c5c5c", "#c8c8c8", "#ffffff"
BLUE, BLUE_TINT, ORANGE, ORANGE_TINT, GREY_TINT = (
    "#1c64c7",
    "#edf3fc",
    "#d2501a",
    "#fdf0e8",
    "#f4f4f3",
)
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
MONO = "Menlo, Consolas, monospace"
SENTENCE = "Before planning, list the ways this change could go wrong."
PLAIN = "Plan this change."
EXAMPLE = (
    "t078",
    "t051",
)  # a real plain trial and a real trial with the sentence, task U08, Opus 5.5

TEXT = {
    "en": {
        "klein": "KLEIN'S PRE-MORTEM (2007)",
        "half1": "Assume the plan has already failed",
        "half2": "List the reasons it failed",
        "unused": "not used in this study",
        "tested": "the sentence tested in this study",
        "sentence_local": "",
        "plain_local": "",
        "tasks": "12 change requests on 12 public repositories, each fixed at one version",
        "yardstick": "THE YARDSTICK",
        "yardstick_sub": "reference risks, written without seeing the agent",
        "answers": "THE ANSWERS",
        "answers_sub": "the coding agent under test",
        "y1": "3 reviewer models of other vendors read each repository",
        "y2": "369 problems they expect",
        "y3": "kept when 2 of the 3 name the same problem",
        "y4": "100 reference risks",
        "a1": "Claude Code in plan mode, on Opus 5.5 and Sonnet 5.5",
        "a2": "Plain request",
        "a3": "Request with the sentence",
        "trials": "120 trials",
        "a4": "Each answer ends with a table of at most 10 risks",
        "judge": "A blind judge of another vendor checks each reference risk against the table",
        "coverage": "coverage = reference risks covered ÷ reference risks",
        "sealed": "sealed and timestamped before trial 1",
        "plain_t": "Plain request",
        "sent_t": "Request with the sentence",
        "req_label": "CHANGE REQUEST (example: task U08)",
        "req": "Change the default signing digest from SHA-1 to SHA-256.",
        "req_local": "",
        "line_label": "THE ONLY LINE THAT DIFFERS",
        "contract_label": "OUTPUT CONTRACT (same in both)",
        "contract": "State assumptions, edit no file, and end with a table of at most 10 risks.",
        "ans_plain": "Answer to the plain request",
        "ans_sent": "Answer to the request with the sentence",
        "ans_sub": "risk column of the final table · trial {t}",
        "covers": "covers {k} of the 6 reference risks",
        "ref_head": "Reference risk (task U08)",
        "col_plain": "plain",
        "col_sent": "with the sentence",
        "refs": ["Old tokens stop validating after the upgrade",
                 "The two classes end up with different defaults",
                 "The derived key changes in value and length",
                 "Tests assert outputs that match SHA-1",
                 "Longer signatures overflow columns, URLs or cookies",
                 "Documentation and doctests still say SHA-1"],
        "total": "covered",
        "of": "of",
        "plain_rows": ["Existing tokens stop verifying", "Plain Signer and TimestampSigner tokens break",
                       "FIPS builds raise ValueError on bad tokens", "Repeats the 1.0.0 problem",
                       "Longer tokens", "The fallback keeps SHA-1 accepted",
                       "Hard-coded tokens in tests", "Downstream code relies on the default",
                       "Code that imports _lazy_sha1 or checks the default"],
        "sent_rows": ["All existing tokens stop verifying",
                      "Direct Signer and TimestampSigner users get no fallback",
                      "A custom fallback_signers list drops SHA-1", "FIPS regression",
                      "Same mistake as the yanked 1.0.0", "Cookies and URLs get longer",
                      "Rolling deploys reject new tokens", "Subclass and introspection breakage",
                      "Downstream libraries change behaviour silently", "Tests and docs go stale"],
        "translated": "",
        "how": "Each entry keeps the fingerprint of one file and the hash of the entry before it",
        "entry": "Entry",
        "file": "file",
        "prev": "previous",
        "hash": "hash",
        "more": "more than 1,200 entries follow, each linked to the one before",
        "stages": ["Protocol, lists and code", "240 answers", "720 verdicts", "Analysis"],
        "head1": "Head before trial 1",
        "head2": "Head after the analysis",
        "btc": "anchored in Bitcoin block 975226",
        "sub": "anchored in Bitcoin block 975820",
        "tamper": "Changing any recorded file changes every hash after it.",
        "before": "BEFORE ANY DATA",
        "events": [("9 Nov · 15:25", "Tasks fixed"), ("9 Nov · 16:08", "Protocol, reference lists and code sealed"),
                   ("9 Nov · 16:10", "Trial 1"), ("9 Nov · 16:19", "Collection paused at 38 trials"),
                   ("13 Nov · 09:40", "Collection resumed"), ("14 Nov · 00:30", "240 answers published"),
                   ("14 Nov · 12:44", "720 verdicts sealed"), ("14 Nov · 12:45", "Analysis run and sealed")],
        "tz": "November 2026, São Paulo time",
    },
    "pt-BR": {
        "klein": "PRÉ-MORTEM DE KLEIN (2007)",
        "half1": "Suponha que o plano já fracassou",
        "half2": "Liste os motivos do fracasso",
        "unused": "não usado neste estudo",
        "tested": "a frase testada neste estudo",
        "sentence_local": "Antes de planejar, liste as maneiras como esta mudança pode dar errado.",
        "plain_local": "Planeje esta mudança.",
        "tasks": "12 pedidos de mudança em 12 repositórios públicos, cada um fixado numa versão",
        "yardstick": "A RÉGUA",
        "yardstick_sub": "riscos de referência, escritos sem ver o agente",
        "answers": "AS RESPOSTAS",
        "answers_sub": "o agente de código testado",
        "y1": "3 modelos revisores de outros fornecedores leem cada repositório",
        "y2": "369 problemas que eles esperam",
        "y3": "fica o que 2 dos 3 apontam como o mesmo problema",
        "y4": "100 riscos de referência",
        "a1": "Claude Code em modo de planejamento, no Opus 5.5 e no Sonnet 5.5",
        "a2": "Pedido simples",
        "a3": "Pedido com a frase",
        "trials": "120 rodadas",
        "a4": "Cada resposta termina com uma tabela de até 10 riscos",
        "judge": "Um juiz cego de outro fornecedor confere cada risco de referência contra a tabela",
        "coverage": "cobertura = riscos de referência cobertos ÷ riscos de referência",
        "sealed": "selado e carimbado antes da rodada 1",
        "plain_t": "Pedido simples",
        "sent_t": "Pedido com a frase",
        "req_label": "PEDIDO DE MUDANÇA (exemplo: tarefa U08)",
        "req": "Change the default signing digest from SHA-1 to SHA-256.",
        "req_local": "Mude o algoritmo padrão de assinatura de SHA-1 para SHA-256.",
        "line_label": "A ÚNICA LINHA QUE MUDA",
        "contract_label": "CONTRATO DE SAÍDA (igual nos dois)",
        "contract": "Declare as suposições, não edite arquivos e termine com uma tabela de até 10 riscos.",
        "ans_plain": "Resposta ao pedido simples",
        "ans_sent": "Resposta ao pedido com a frase",
        "ans_sub": "coluna de riscos da tabela final · rodada {t}",
        "covers": "cobre {k} dos 6 riscos de referência",
        "ref_head": "Risco de referência (tarefa U08)",
        "col_plain": "simples",
        "col_sent": "com a frase",
        "refs": ["Tokens antigos deixam de validar depois da atualização",
                 "As duas classes ficam com padrões diferentes",
                 "A chave derivada muda de valor e de tamanho",
                 "Testes afirmam saídas que batem com SHA-1",
                 "Assinaturas maiores estouram colunas, URLs ou cookies",
                 "Documentação e doctests ainda dizem SHA-1"],
        "total": "cobertos",
        "of": "de",
        "plain_rows": ["Tokens existentes deixam de ser verificados",
                       "Tokens de Signer e TimestampSigner simples quebram",
                       "Builds FIPS lançam ValueError em tokens inválidos",
                       "Repete o problema da versão 1.0.0", "Tokens mais longos",
                       "O fallback mantém o SHA-1 aceito", "Tokens fixos nos testes",
                       "Código de terceiros depende do padrão",
                       "Código que importa _lazy_sha1 ou confere o padrão"],
        "sent_rows": ["Todos os tokens existentes deixam de ser verificados",
                      "Quem usa Signer e TimestampSigner direto fica sem fallback",
                      "Uma lista fallback_signers própria descarta o SHA-1", "Regressão em FIPS",
                      "Mesmo erro da versão 1.0.0, que foi retirada", "Cookies e URLs ficam mais longos",
                      "Implantações graduais rejeitam tokens novos",
                      "Quebra de subclasses e de introspecção",
                      "Bibliotecas dependentes mudam de comportamento em silêncio",
                      "Testes e documentação ficam defasados"],
        "translated": "traduzido do inglês; o original está no repositório",
        "how": "Cada entrada guarda a impressão digital de um arquivo e o hash da entrada anterior",
        "entry": "Entrada",
        "file": "arquivo",
        "prev": "anterior",
        "hash": "hash",
        "more": "seguem mais de 1.200 entradas, cada uma ligada à anterior",
        "stages": ["Protocolo, listas e código", "240 respostas", "720 vereditos", "Análise"],
        "head1": "Cabeça antes da rodada 1",
        "head2": "Cabeça depois da análise",
        "btc": "ancorada no bloco 975226 do Bitcoin",
        "sub": "ancorada no bloco 975820 do Bitcoin",
        "tamper": "Mudar qualquer arquivo registrado muda todos os hashes depois dele.",
        "before": "ANTES DE QUALQUER DADO",
        "events": [("9 nov · 15:25", "Tarefas fixadas"),
                   ("9 nov · 16:08", "Protocolo, listas de referência e código selados"),
                   ("9 nov · 16:10", "Rodada 1"), ("9 nov · 16:19", "Coleta pausada em 38 rodadas"),
                   ("13 nov · 09:40", "Coleta retomada"), ("14 nov · 00:30", "240 respostas publicadas"),
                   ("14 nov · 12:44", "720 vereditos selados"),
                   ("14 nov · 12:45", "Análise executada e selada")],
        "tz": "novembro de 2026, horário de São Paulo",
    },
}  # fmt: skip

# Spanish and Italian labels live in a JSON file next to this script (same keys as above).
for _lang, _labels in json.loads(
    (Path(__file__).with_name("diagram_text_es_it.json")).read_text(encoding="utf-8")
).items():
    TEXT[_lang] = {**_labels, "events": [tuple(e) for e in _labels["events"]]}


def wrap(text: str, width: float, size: float, bold: bool = False) -> list[str]:
    """Break ``text`` into lines that fit ``width`` pixels at ``size``, by an average glyph width.

    Parameters
    ----------
    text : str
        Text without line breaks.
    width : float
        Available width in drawing units.
    size : float
        Font size.
    bold : bool
        Bold text runs a little wider.

    Returns
    -------
    list of str
        The lines.
    """
    limit = max(8, int(width / (size * (0.52 if bold else 0.48))))
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > limit:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return [*lines, line] if line else lines


class Drawing:
    """One SVG drawing ``W`` units wide, built from a handful of primitives."""

    def __init__(self, height: int) -> None:
        """Start an empty drawing.

        Parameters
        ----------
        height : int
            Height in drawing units.
        """
        self.height = height
        self.parts: list[str] = []

    def rect(self, x, y, w, h, fill="none", stroke=RULE, dash=False, width=2, radius=12) -> None:
        """Add a rounded rectangle.

        Parameters
        ----------
        x, y, w, h : float
            Position of the top-left corner and size.
        fill, stroke : str
            Colours.
        dash : bool
            Dashed outline.
        width : float
            Stroke width.
        radius : float
            Corner radius.
        """
        extra = ' stroke-dasharray="9 7"' if dash else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}"{extra}/>'
        )

    def text(self, x, y, lines, size=22, fill=INK, anchor="start", weight=400, italic=False,
             mono=False, spacing=None, leading=1.32) -> float:  # fmt: skip
        """Add one or more lines of text and return the y of the line after the last.

        Parameters
        ----------
        x, y : float
            Anchor of the first baseline.
        lines : str or list of str
            Text; a list is set as successive lines.
        size : float
            Font size.
        fill : str
            Colour.
        anchor : str
            ``start``, ``middle`` or ``end``.
        weight : int
            Font weight.
        italic, mono : bool
            Style switches.
        spacing : float, optional
            Letter spacing (used for small capital labels).
        leading : float
            Line height as a multiple of the size.

        Returns
        -------
        float
            The baseline a following line would use.
        """
        for line in [lines] if isinstance(lines, str) else lines:
            style = ' font-style="italic"' if italic else ""
            track = f' letter-spacing="{spacing}"' if spacing else ""
            self.parts.append(
                f'<text x="{x}" y="{y}" font-family="{MONO if mono else FONT}" font-size="{size}" '
                f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{style}{track}>'
                f"{escape(line)}</text>"
            )
            y += size * leading
        return y

    def block(self, x, y, w, text, size=22, **kw) -> float:
        """Add wrapped text inside a column ``w`` wide; return the next baseline.

        Parameters
        ----------
        x, y, w : float
            Left edge (or centre, with ``anchor="middle"``), first baseline and column width.
        text : str
            Text to wrap.
        size : float
            Font size.
        **kw
            Passed to :meth:`text`.

        Returns
        -------
        float
            The baseline a following line would use.
        """
        return self.text(x, y, wrap(text, w, size, kw.get("weight", 400) >= 600), size=size, **kw)

    def line(self, x1, y1, x2, y2, stroke=RULE, width=2, dash=False) -> None:
        """Add a straight line.

        Parameters
        ----------
        x1, y1, x2, y2 : float
            End points.
        stroke : str
            Colour.
        width : float
            Stroke width.
        dash : bool
            Dashed line.
        """
        extra = ' stroke-dasharray="6 6"' if dash else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{width}" stroke-linecap="round"{extra}/>'
        )

    def arrow(self, x1, y1, x2, y2, color=MUTED, width=2.5) -> None:
        """Add a straight arrow with a filled head at ``(x2, y2)``.

        Parameters
        ----------
        x1, y1, x2, y2 : float
            Start and end points; the arrow is horizontal or vertical.
        color : str
            Colour.
        width : float
            Stroke width.
        """
        s = 9
        if abs(x2 - x1) > abs(y2 - y1):
            d = 1 if x2 > x1 else -1
            head = f"{x2},{y2} {x2 - d * s * 1.5},{y2 - s} {x2 - d * s * 1.5},{y2 + s}"
            self.line(x1, y1, x2 - d * s, y2, color, width)
        else:
            d = 1 if y2 > y1 else -1
            head = f"{x2},{y2} {x2 - s},{y2 - d * s * 1.5} {x2 + s},{y2 - d * s * 1.5}"
            self.line(x1, y1, x2, y2 - d * s, color, width)
        self.parts.append(f'<polygon points="{head}" fill="{color}"/>')

    def badge(self, x, y, label, color=INK, fill=PAPER) -> None:
        """Add a numbered circle centred on ``(x, y)``.

        Parameters
        ----------
        x, y : float
            Centre.
        label : str
            One or two characters.
        color, fill : str
            Outline and text colour, and fill.
        """
        self.parts.append(
            f'<circle cx="{x}" cy="{y}" r="19" fill="{fill}" stroke="{color}" stroke-width="2"/>'
        )
        self.text(x, y + 7.5, label, size=21, fill=color, anchor="middle", weight=600)

    def mark(self, x, y, yes: bool) -> None:
        """Add a check mark or a cross centred on ``(x, y)``.

        Parameters
        ----------
        x, y : float
            Centre.
        yes : bool
            Check mark when true, cross otherwise.
        """
        if yes:
            path, color = f"M{x - 11},{y + 1} l8,9 l15,-19", BLUE
        else:
            path, color = f"M{x - 8},{y - 8} l16,16 M{x + 8},{y - 8} l-16,16", "#9a9a9a"
        self.parts.append(
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="4" '
            'stroke-linecap="round" stroke-linejoin="round"/>'
        )

    def svg(self) -> str:
        """Return the drawing as an SVG document.

        Returns
        -------
        str
            SVG source.
        """
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {self.height}" '
            f'width="{W}" height="{self.height}">\n' + "\n".join(self.parts) + "\n</svg>\n"
        )


def quote(d: Drawing, x, y, w, english: str, local: str, size=24, color=INK) -> float:
    """Set a literal English string in bold with its translation below; return the next baseline.

    Parameters
    ----------
    d : Drawing
        Drawing to add to.
    x, y, w : float
        Centre, first baseline and column width.
    english : str
        The literal string, as sent to the model.
    local : str
        Its translation in the edition language; empty in the English edition.
    size : float
        Size of the English string.
    color : str
        Colour of the English string.

    Returns
    -------
    float
        The baseline a following line would use.
    """
    y = d.block(x, y, w, f"“{english}”", size=size, anchor="middle", weight=700, fill=color)
    if local:
        y = d.block(x, y + 4, w, local, size=size - 4, anchor="middle", italic=True, fill=MUTED)
    return y


def halves(t: dict) -> Drawing:
    """Draw the two halves of a pre-mortem and the one the tested sentence keeps.

    Parameters
    ----------
    t : dict
        Text of the edition language.

    Returns
    -------
    Drawing
        The diagram.
    """
    d = Drawing(470 if t["sentence_local"] else 430)
    d.text(W / 2, 34, t["klein"], size=19, fill=MUTED, anchor="middle", weight=600, spacing=2)
    d.line(60, 52, W - 60, 52)
    d.rect(60, 80, 400, 130, dash=True, stroke="#9a9a9a")
    d.badge(104, 145, "1", color="#8a8a8a")
    d.block(140, 138, 300, t["half1"], size=24, fill=MUTED)
    d.text(260, 242, t["unused"], size=19, fill="#8a8a8a", anchor="middle", italic=True)
    d.text(500, 156, "+", size=34, fill=MUTED, anchor="middle")
    d.rect(540, 80, 400, 130, fill=ORANGE_TINT, stroke=ORANGE)
    d.badge(584, 145, "2", color=ORANGE)
    d.block(620, 138, 300, t["half2"], size=24, weight=600)
    d.arrow(740, 214, 740, 268, color=ORANGE)
    bottom = d.height - 20
    d.rect(180, 272, 760, bottom - 272, stroke=ORANGE, width=2.5)
    d.text(
        560,
        304,
        t["tested"].upper(),
        size=17,
        fill=ORANGE,
        anchor="middle",
        weight=600,
        spacing=1.5,
    )
    quote(d, 560, 346, 700, SENTENCE, t["sentence_local"], size=25)
    return d


def design(t: dict) -> Drawing:
    """Draw the design of the study: the yardstick, the answers and the judge.

    Parameters
    ----------
    t : dict
        Text of the edition language.

    Returns
    -------
    Drawing
        The diagram.
    """
    d = Drawing(1010)
    d.rect(140, 20, 720, 84, fill=GREY_TINT, stroke=RULE)
    d.block(W / 2, 54, 660, t["tasks"], size=23, anchor="middle", weight=600)
    d.arrow(300, 104, 300, 150)
    d.arrow(700, 104, 700, 150)
    # left lane: the yardstick
    d.text(40, 186, t["yardstick"], size=20, fill=BLUE, weight=700, spacing=2)
    d.block(40, 214, 430, t["yardstick_sub"], size=19, fill=MUTED, italic=True)
    ys = [250, 386, 492, 628]
    for k, (y, h, key) in enumerate(
        zip(ys, [104, 74, 104, 84], ["y1", "y2", "y3", "y4"], strict=True)
    ):
        last = key == "y4"
        d.rect(
            40, y, 430, h, fill=BLUE_TINT if last else PAPER, stroke=BLUE, width=2.5 if last else 2
        )
        lines = wrap(t[key], 380, 22, last)
        d.text(255, y + h / 2 + 8 - (len(lines) - 1) * 14.5, lines, size=22, anchor="middle",
               weight=700 if last else 400)  # fmt: skip
        if k < 3:
            d.arrow(255, y + h, 255, ys[k + 1] - 2, color=BLUE)
    # right lane: the answers
    d.text(530, 186, t["answers"], size=20, fill=ORANGE, weight=700, spacing=2)
    d.block(530, 214, 430, t["answers_sub"], size=19, fill=MUTED, italic=True)
    d.rect(530, 250, 430, 104, stroke=MUTED)
    lines = wrap(t["a1"], 380, 22)
    d.text(745, 250 + 52 + 8 - (len(lines) - 1) * 14.5, lines, size=22, anchor="middle")
    d.arrow(637, 354, 637, 400)
    d.arrow(853, 354, 853, 400)
    for x, key, edge, fill in ((530, "a2", MUTED, PAPER), (746, "a3", ORANGE, ORANGE_TINT)):
        d.rect(x, 402, 214, 124, fill=fill, stroke=edge, width=2.5 if key == "a3" else 2)
        lines = wrap(t[key], 190, 22, True)
        y = d.text(
            x + 107, 446 - (len(lines) - 1) * 14, lines, size=22, anchor="middle", weight=700
        )
        d.text(x + 107, y + 6, t["trials"], size=20, anchor="middle", fill=MUTED)
        d.arrow(x + 107, 526, x + 107, 576)
    d.rect(530, 578, 430, 104, stroke=MUTED)
    lines = wrap(t["a4"], 380, 22)
    d.text(745, 578 + 52 + 8 - (len(lines) - 1) * 14.5, lines, size=22, anchor="middle")
    # the judge
    d.arrow(255, 712, 255, 780, color=BLUE)
    d.arrow(745, 682, 745, 780)
    d.rect(40, 782, 920, 170, fill=GREY_TINT, stroke=INK, width=2.5)
    y = d.block(W / 2, 826, 840, t["judge"], size=23, anchor="middle")
    d.block(W / 2, y + 16, 840, t["coverage"], size=24, anchor="middle", weight=700)
    d.text(40, 992, t["sealed"], size=19, fill=BLUE, italic=True)
    return d


def requests(t: dict) -> Drawing:
    """Draw the two requests side by side on a real task, with the one line that differs.

    Parameters
    ----------
    t : dict
        Text of the edition language.

    Returns
    -------
    Drawing
        The diagram.
    """
    local = bool(t["sentence_local"])
    d = Drawing(650 if local else 560)
    row = [70, 250 if local else 220, 470 if local else 400, d.height - 20]  # block tops
    labels = [t["req_label"], t["line_label"], t["contract_label"]]
    for x, title, edge in ((40, t["plain_t"], MUTED), (520, t["sent_t"], ORANGE)):
        d.text(x + 220, 42, title, size=26, anchor="middle", weight=700)
        d.rect(x, 62, 440, d.height - 72, stroke=edge, width=2.5 if edge == ORANGE else 2)
        for k, label in enumerate(labels):
            y = row[k]
            if k:
                d.line(x + 20, y, x + 420, y, stroke=RULE, width=1.5)
            d.text(x + 24, y + 34, label, size=15.5, fill=ORANGE if k == 1 else MUTED, weight=600,
                   spacing=1)  # fmt: skip
        quote(d, x + 220, row[0] + 76, 390, t["req"], t["req_local"], size=22)
        if edge == ORANGE:
            d.rect(x + 14, row[1] + 48, 412, row[2] - row[1] - 62, fill=ORANGE_TINT, stroke="none")
            quote(d, x + 220, row[1] + 90, 380, SENTENCE, t["sentence_local"], size=23)
        else:
            quote(d, x + 220, row[1] + 90, 380, PLAIN, t["plain_local"], size=23)
        d.block(x + 220, row[2] + 74, 380, t["contract"], size=20, anchor="middle", fill=MUTED)
    return d


def answers(t: dict) -> Drawing:
    """Draw the risk column of two real answers to the same task, one per condition.

    Parameters
    ----------
    t : dict
        Text of the edition language.

    Returns
    -------
    Drawing
        The diagram. The rows are the titles of each answer's risk table.
    """
    covered = [len(json.loads((STUDY / "judge" / "gemini" / f"{x}.json").read_text())["covered"])
               for x in EXAMPLE]  # fmt: skip
    d = Drawing(784 if t["translated"] else 740)
    for x, title, rows, trial, k, edge in (
        (40, t["ans_plain"], t["plain_rows"], EXAMPLE[0], covered[0], MUTED),
        (520, t["ans_sent"], t["sent_rows"], EXAMPLE[1], covered[1], ORANGE),
    ):
        d.block(x + 220, 36, 430, title, size=24, anchor="middle", weight=700)
        d.rect(x, 60, 440, 610, stroke=edge, width=2.5 if edge == ORANGE else 2)
        d.text(x + 24, 96, t["ans_sub"].format(t=trial), size=16.5, fill=MUTED, italic=True)
        d.line(x + 20, 112, x + 420, 112, stroke=RULE, width=1.5)
        y = 148
        for i, row in enumerate(rows, 1):
            d.text(x + 46, y, str(i), size=19, fill=MUTED, anchor="end", weight=600)
            lines = wrap(row, 360, 19)
            d.text(x + 60, y, lines, size=19)
            y += 26 * len(lines) + 12
        d.rect(x + 40, 690, 360, 46, fill=ORANGE_TINT if edge == ORANGE else GREY_TINT, stroke=edge)
        d.text(x + 220, 720, t["covers"].format(k=k), size=20, anchor="middle", weight=700)
    if t["translated"]:
        d.text(W / 2, 772, t["translated"], size=16.5, fill=MUTED, anchor="middle", italic=True)
    return d


def scoring(t: dict) -> Drawing:
    """Draw how the two example answers are scored against the six reference risks of the task.

    Parameters
    ----------
    t : dict
        Text of the edition language.

    Returns
    -------
    Drawing
        The diagram, with the judge's real verdicts for the two trials.
    """
    verdicts = [set(json.loads((STUDY / "judge" / "gemini" / f"{x}.json").read_text())["covered"])
                for x in EXAMPLE]  # fmt: skip
    d = Drawing(560)
    d.text(40, 44, t["ref_head"], size=22, weight=700)
    for x, label, trial, color in (
        (700, t["col_plain"], EXAMPLE[0], INK),
        (880, t["col_sent"], EXAMPLE[1], ORANGE),
    ):
        d.text(x, 30, label, size=21, weight=700, anchor="middle", fill=color)
        d.text(x, 54, trial, size=16.5, anchor="middle", fill=MUTED, mono=True)
    d.line(40, 70, 960, 70, stroke=INK, width=2)
    for i, ref in enumerate(t["refs"], 1):
        y = 70 + i * 62
        d.text(64, y - 22, str(i), size=20, fill=MUTED, anchor="end", weight=600)
        d.text(80, y - 22, ref, size=21)
        d.mark(700, y - 28, i in verdicts[0])
        d.mark(880, y - 28, i in verdicts[1])
        d.line(40, y, 960, y, stroke=RULE, width=1.2)
    y = 70 + 6 * 62 + 62
    d.text(80, y - 12, t["total"].capitalize(), size=22, weight=700)
    for x, v, color, fill in (
        (700, verdicts[0], INK, GREY_TINT),
        (880, verdicts[1], ORANGE, ORANGE_TINT),
    ):
        d.rect(x - 78, y - 46, 156, 54, fill=fill, stroke=color)
        share = f"{len(v) / 6:.0%}"
        d.text(x, y - 11, f"{len(v)} {t['of']} 6 = {share}", size=21, anchor="middle", weight=700)
    return d


def chain(t: dict) -> Drawing:
    """Draw the hash chain of the study's ledger with its first real entries and its two heads.

    Parameters
    ----------
    t : dict
        Text of the edition language.

    Returns
    -------
    Drawing
        The diagram.
    """
    entries = [json.loads(x) for x in (STUDY / "ledger.jsonl").read_text().splitlines()[:3]]
    heads = [
        (STUDY / f).read_text().split()[-1] for f in ("pretrial-head.txt", "analysis-head.txt")
    ]
    d = Drawing(830)
    d.block(W / 2, 34, 900, t["how"], size=21, anchor="middle", fill=MUTED, italic=True)
    for i, e in enumerate(entries):
        x = 40 + i * 320
        d.rect(x, 64, 280, 226, stroke=BLUE, width=2.5)
        d.text(x + 140, 100, f"{t['entry']} {e['n']}", size=22, anchor="middle", weight=700)
        d.text(
            x + 140, 126, Path(e["path"]).name, size=17.5, anchor="middle", fill=MUTED, mono=True
        )
        for k, (label, value, color, fill) in enumerate((
            (t["file"], e["sha256"], INK, PAPER), (t["prev"], e["prev"], MUTED, PAPER),
            (t["hash"], e["hash"], BLUE, BLUE_TINT),
        )):  # fmt: skip
            y = 146 + k * 46
            d.text(x + 18, y + 25, label, size=18, fill=MUTED)
            d.rect(
                x + 118, y, 146, 36, fill=fill, stroke=color, radius=8, width=2.5 if k == 2 else 1.5
            )
            d.text(x + 191, y + 25, value[:8] + "…", size=18.5, anchor="middle", fill=color, mono=True,
                   weight=600 if k == 2 else 400)  # fmt: skip
        if i < 2:  # this entry's hash is the next entry's "previous"
            x2, yh, yp = x + 320, 146 + 2 * 46 + 18, 146 + 46 + 18
            d.parts.append(
                f'<path d="M{x + 264},{yh} H{x + 300} V{yp} H{x2 - 12}" fill="none" stroke="{BLUE}" '
                'stroke-width="2.5" stroke-linejoin="round"/>'
            )
            d.parts.append(
                f'<polygon points="{x2},{yp} {x2 - 14},{yp - 8} {x2 - 14},{yp + 8}" fill="{BLUE}"/>'
            )
    d.text(W / 2, 330, "· · ·", size=30, anchor="middle", fill=MUTED)
    d.text(W / 2, 362, t["more"], size=19, anchor="middle", fill=MUTED, italic=True)
    xs = [40, 282, 524, 766]
    for k, (x, label) in enumerate(zip(xs, t["stages"], strict=True)):
        first = k == 0
        d.rect(x, 400, 194, 112, fill=BLUE_TINT if first else ORANGE_TINT, stroke=BLUE if first else ORANGE,
               width=2.5)  # fmt: skip
        lines = wrap(label, 170, 20, True)
        d.text(x + 97, 456 + 7 - (len(lines) - 1) * 13, lines, size=20, anchor="middle", weight=700)
    for x in xs[:3]:  # the links of the chain, drawn over the boxes they join
        d.rect(x + 176, 440, 84, 32, stroke=INK, width=5, radius=16)
    for x, label, head, note, color in ((168, t["head1"], heads[0], t["btc"], BLUE),
                                        (832, t["head2"], heads[1], t["sub"], ORANGE)):  # fmt: skip
        d.arrow(x, 514, x, 566, color=color)
        d.text(x, 600, label, size=21, anchor="middle", weight=700)
        d.rect(x - 128, 616, 256, 40, stroke=color, radius=8)
        d.text(
            x,
            643,
            head[:8] + "…" + head[-8:],
            size=18.5,
            anchor="middle",
            fill=color,
            mono=True,
            weight=600,
        )
        d.block(x, 686, 330, note, size=19, anchor="middle", fill=color, italic=True)
    d.line(40, 760, 960, 760, stroke=RULE, width=1.5)
    d.text(W / 2, 800, t["tamper"], size=21, anchor="middle", weight=600)
    return d


def timeline(t: dict) -> Drawing:
    """Draw the order of the sealed events of the study as a vertical timeline.

    Parameters
    ----------
    t : dict
        Text of the edition language.

    Returns
    -------
    Drawing
        The diagram. The spacing is ordinal, not to scale.
    """
    step = 62
    d = Drawing(116 + step * len(t["events"]))
    d.rect(40, 20, 920, 2 * step + 30, fill=BLUE_TINT, stroke="none")
    d.text(940, 50, t["before"], size=16.5, fill=BLUE, anchor="end", weight=700, spacing=1.5)
    x = 300
    d.line(x, 56, x, 82 + step * (len(t["events"]) - 1), stroke=RULE, width=3)
    for i, (when, what) in enumerate(t["events"]):
        y = 56 + i * step + (26 if i >= 2 else 0)
        color = BLUE if i < 2 else (MUTED if i in (3, 4) else ORANGE)
        d.parts.append(
            f'<circle cx="{x}" cy="{y}" r="10" fill="{color}" stroke="{PAPER}" stroke-width="3"/>'
        )
        d.text(x - 30, y + 7, when, size=20, anchor="end", fill=MUTED, mono=True)
        d.text(x + 30, y + 7, what, size=22, weight=600 if i in (1, 7) else 400)
    d.text(x + 30, 56 + step + 34, t["btc"], size=18, fill=BLUE, italic=True)
    d.text(940, d.height - 14, t["tz"], size=17, fill=MUTED, anchor="end", italic=True)
    return d


DIAGRAMS = {
    "d1_premortem_halves": halves,
    "d2_design": design,
    "d3_two_requests": requests,
    "d4_two_answers": answers,
    "d5_scoring": scoring,
    "d6_hash_chain": chain,
    "d7_timeline": timeline,
}


def main() -> None:
    """Write every diagram as SVG and PNG for each language (or the one given with ``--lang``)."""
    import resvg_py

    langs = [sys.argv[sys.argv.index("--lang") + 1]] if "--lang" in sys.argv else list(TEXT)
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in langs:
        for name, draw in DIAGRAMS.items():
            stem = name + ("" if lang == "en" else f".{lang}")  # a language tag is not a suffix
            source = draw(TEXT[lang]).svg()
            (OUT / f"{stem}.svg").write_text(source, encoding="utf-8")
            png = resvg_py.svg_to_bytes(svg_string=source, width=3000)
            (OUT / f"{stem}.png").write_bytes(bytes(png))
    print(
        f"diagrams -> {OUT.relative_to(ROOT)} ({len(DIAGRAMS)} x {len(langs)} languages, SVG + PNG)"
    )


if __name__ == "__main__":
    main()
