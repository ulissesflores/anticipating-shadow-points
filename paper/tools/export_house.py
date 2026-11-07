#!/usr/bin/env python3
r"""Exportador ASP (fork do export_v04.py do repo lgbt-indicador-violencia): Markdown em INGLES -> DOCX na norma Codex Hash.

Mesma tese do original (pandoc SEM reference-doc + padrao fisico aplicado depois, onde e verificavel; o crivo
`crivo_docx.py` importa as mesmas constantes). Diferencas para o original, todas necessarias porque os artigos do
ASP nascem em ingles e levam bloco de codigo:

* rotulos nativos em ingles (Table/Figure/Note./References/Appendix/Abstract/Date:); sem round-trip por rotulos PT;
* legenda `**Table N.** titulo` (mesma linha) e `![Figure N. legenda](../output/figures/x.png)`; figura que e um bloco
  de codigo (diagrama ASCII) com a legenda ABAIXO no Markdown sobe: rotulo + legenda ACIMA, como a norma manda;
* bloco de codigo = estilo CodeBlock em Courier New (UMA fonte mono, so no bloco; codigo inline segue em Times, regra
  do autor), tamanho 7,5 a 10 pt escolhido pela linha mais longa para nao quebrar linha de shell;
* SEM "Fonte: Elaboracao do autor." injetada: a norma pede Nota "quando houver"; elemento sem Nota apenas ganha
  espaco depois;
* idioma de revisao en-US; `--`/menos tipografico nao tocam codigo; secao 1 recebe quebra por `^1\. `, nao por nome;
  Resumo NAO tem quebra (canon en = exatamente 3 pageBreakBefore: Abstract, 1., References);
* lista e Nota seguem o espaco do corpo (duplo + 6 pt), emenda de 2026-11-06 da norma.

Uso: python3 paper/tools/export_house.py --src build/<nome>/fonte.md --work build/<nome>/work --out build/<nome>/<nome>.docx
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from lxml import etree
from PIL import Image, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rotulos  # noqa: E402  (rótulos por idioma da edição; `en` = literais originais)

# --------------------------------------------------------------------------- #
# 0. constantes de forma (UM lugar) — o crivo importa estas mesmas             #
# --------------------------------------------------------------------------- #
TNR = "Times New Roman"
CFG = {
    "fonte": TNR,
    "pt": 12,                      # tudo fora de tabela
    "pt_tabela": 10,               # teto da tabela
    "pt_tabela_min": 8,            # piso da tabela (APA 7 admite 8 a 14)
    "pagina_twips": (12240, 15840),  # Carta
    "margem_twips": 1440,          # 2,54 cm
    "cabecalho_twips": 720,
    "recuo_twips": 720,            # 1,27 cm
    "fig_largura_cm": 14.0,        # teto; ver docstring (1)
    "regua_sz": 6,                 # 1/8 pt: 6 = 0,75 pt, filetes horizontais da tabela APA
    "img_px": 1400,                # largura em pixels das copias embutidas (ajustada pelo build para <= 4 MB)
    "img_cores": 256,
    "menos_tipografico": True,     # "-12,3" -> "\u221212,3" (nao quebra linha depois do sinal)
}
# (entrelinha em multiplos de linha simples, antes em pt, depois em pt) por papel
ESP = {
    "corpo": (2.0, 0, 6),          # norma Codex Hash: sem recuo de 1a linha, 6 pt entre paragrafos
    "titulo1": (2.0, 12, 6),
    "titulo2": (2.0, 12, 6),
    "lista": (2.0, 0, 6),               # emenda 2026-11-06: lista com espaco do corpo (duplo + 6 pt)
    "referencia": (2.0, 0, 0),
    "rotulo": (1.0, 6, 0),         # "Tabela N"/"Figura N": 6 pt antes
    "titulo_elem": (1.0, 0, 6),    # titulo em italico, 6 pt ate a tabela/figura
    "imagem": (1.0, 0, 3),
    "nota": (2.0, 3, 12),          # Nota: espaco do corpo (duplo), 3 pt depois da tabela, 12 pt ate o proximo paragrafo
    "codigo": (1.0, 6, 12),        # bloco de codigo: espaco simples (preserva a leitura da linha), 12 pt ate o proximo
    "celula": (1.0, 1, 1),
    "titulo_doc": (1.0, 0, 12),
    "cabecalho": (1.0, 0, 0),
}
LISTA_DEPOIS_PT = 6               # espaco depois do paragrafo/titulo que precede uma lista
TITULO_DOC_ANTES_PT = 120         # a folha de rosto comeca cerca de 1/4 abaixo do topo
FOLGA_COLUNAS = 0.88             # soma dos pisos de coluna <= 88% da largura util, senao muda de fonte/orientacao
MARGEM_SEGURANCA_FIG_PT = 30      # folga na conta de altura de pagina das figuras

TWIPS_CM = 1440 / 2.54
EMU_CM = 360000
ZWSP = "​"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
THEME_ATTRS = ("asciiTheme", "hAnsiTheme", "cstheme", "eastAsiaTheme")

ROOT = Path(__file__).resolve().parents[1]  # paper/
LOGO = ROOT / "tools/assets/codex-hash-lockup-stacked@2x.png"   # copia do logo da casa (metodo/templates/assets)
LOGO_ALT = "Codex Hash Research Laboratory"
LOGO_CM = 5.2
MONO = "Courier New"                 # UMA fonte mono, so em bloco de codigo (registrada no relatorio)
CODE_PT_MAX, CODE_PT_MIN = 10, 7.5       # tamanho do bloco: o maior que deixa a linha mais longa numa linha


def quebra_direta(t: str) -> bool:
    """canon en: exatamente 3 pageBreakBefore = Abstract, 1. (primeira secao numerada) e References.
    Edicao traduzida: LB["breaks"] (pt-BR 4: Resumo, Abstract, 1., Referencias; es/it 3: resumo local, 1., refs)."""
    b = LB["breaks"]
    return (("abstract" in b and t == "Abstract") or ("resumo" in b and t == LB["resumo"])
            or ("refs" in b and t.startswith(LB["refs"])) or ("intro" in b and re.match(r"^1\. ", t) is not None))


def w(tag: str) -> str:
    return f"{{{W}}}{tag}"


def mk(tag: str, **attrs: object) -> etree._Element:
    el = etree.Element(w(tag))
    for k, v in attrs.items():
        el.set(w(k), str(v))
    return el


def sub(parent: etree._Element, tag: str, **attrs: object) -> etree._Element:
    el = mk(tag, **attrs)
    parent.append(el)
    return el


# --------------------------------------------------------------------------- #
# 1. medida de texto (Times New Roman real, para largura de coluna e de legenda) #
# --------------------------------------------------------------------------- #
_FONTES = {
    "r": "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "b": "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
    "i": "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf",
}
_cache: dict[tuple[str, int], ImageFont.FreeTypeFont | None] = {}


def largura_pt(texto: str, pt: float, estilo: str = "r") -> float:
    """Largura em pontos do texto em Times New Roman; estimativa 0,5 em se a fonte nao existir."""
    chave = (estilo, 100)
    if chave not in _cache:
        try:
            _cache[chave] = ImageFont.truetype(_FONTES[estilo], 100)
        except OSError:
            _cache[chave] = None
    f = _cache[chave]
    if f is None:
        return len(texto) * 0.5 * pt * (1.06 if estilo == "b" else 1.0)
    return f.getlength(texto) * pt / 100


def linhas_de(texto: str, pt: float, largura_cm: float, estilo: str = "r") -> int:
    """Quantas linhas um texto ocupa numa coluna de largura_cm (quebra gulosa por palavra)."""
    limite = largura_cm / 2.54 * 72
    n, atual = 1, 0.0
    espaco = largura_pt(" ", pt, estilo)
    for palavra in texto.split():
        lp = largura_pt(palavra, pt, estilo)
        if atual and atual + espaco + lp > limite:
            n += 1
            atual = lp
        else:
            atual += (espaco if atual else 0) + lp
    return n


# --------------------------------------------------------------------------- #
# 2. paper.md -> markdown de exportacao                                        #
# --------------------------------------------------------------------------- #
MESES = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
         "October", "November", "December"]
LB: dict = rotulos.get("en")      # rotulos da edicao (definir_idioma); o crivo le X.LB
RE_NOTA = RE_CAP = RE_FIG_IMG = None


def definir_idioma(lang: str) -> None:
    """Escolhe os rotulos estruturais da edicao (en = literais originais) e recompila as expressoes de captura."""
    global LB, RE_NOTA, RE_CAP, RE_FIG_IMG
    LB = rotulos.get(lang)
    nota = re.escape(LB["note"].rstrip("."))
    fonte = re.escape(LB["source"])
    RE_NOTA = re.compile(rf"^(\*{nota}\.?\*|{nota}\.|{fonte}:|\*{fonte})")
    t, f = re.escape(LB["table"]), re.escape(LB["figure"])
    RE_CAP = re.compile(rf"^\*\*({t}|{f}) ((?:[A-Z]\d+)|\d+)\.\*\*[ \t]+(.+)$")      # **Table 1.** titulo
    RE_FIG_IMG = re.compile(rf"^!\[{f} (\d+)\. (.+)\]\(([^)\s]+\.png)\)\s*$")       # ![Figure 1. legenda](caminho)


definir_idioma("en")


def front_matter(texto: str) -> tuple[dict[str, str], str]:
    m = re.match(r"---\n(.*?)\n---\n", texto, re.S)
    meta: dict[str, str] = {}
    if m:
        for linha in m.group(1).splitlines():
            k, _, v = linha.partition(":")
            meta[k.strip()] = v.strip().strip('"')
        texto = texto[m.end():]
    return meta, texto


def divs(estilo: str, texto: str) -> str:
    return f'::: {{custom-style="{estilo}"}}\n{texto}\n:::\n'


def split_legenda(legenda: str) -> tuple[str, str]:
    """Titulo = primeira frase (>= 20 caracteres); o resto vira Nota. Nenhuma palavra se perde.
    Legenda de ate 160 caracteres fica inteira como titulo."""
    if len(legenda) <= 160:
        return legenda.rstrip("."), ""
    for m in re.finditer(r"(?<=[a-zà-ÿ0-9\)%])\.\s+(?=[A-ZÀ-Ý“\"(])", legenda):
        if m.start() >= 20:
            return legenda[:m.start()].strip(), legenda[m.end():].strip()
    return legenda.rstrip("."), ""


def escapa_travessao(ln: str) -> str:
    """`--flag` em texto corrido vira travessao no pandoc (smart): escapa, MAS so fora de codigo inline e de tabela
    separadora (o original escapava ate dentro de `code`, que mostraria a barra invertida)."""
    if re.fullmatch(r"[|\s:\-]*|-{3,}", ln):
        return ln
    partes = re.split(r"((?<!`)(`+)(?!`).+?(?<!`)\2(?!`))", ln)
    out, i = [], 0
    while i < len(partes):                      # re.split com 2 grupos: [texto, span, crases, texto, ...]
        out.append(re.sub(r"(?<!\\)--", r"\\-\\-", partes[i]))
        if i + 1 < len(partes):
            out.append(partes[i + 1])
        i += 3
    return "".join(out)


def preparar_md(src: Path, work: Path, fig_cm: str) -> tuple[str, dict]:
    texto = src.read_text(encoding="utf-8")
    meta, texto = front_matter(texto)
    rel: dict = {"sem_nota": [], "quebras_manuais": 0, "figuras": [], "legendas_divididas": 0, "blocos_codigo": 0,
                 "figuras_codigo": 0}

    corte = texto.index("\n## ")
    h1 = re.search(r"^# (.+)$", texto[:corte], re.M)
    titulo = meta.get("title", (h1.group(1) if h1 else "")).strip()
    sub_t = meta.get("subtitle", "").strip()
    ano, mes, dia = (meta.get("date", "").split("-") + ["", "", ""])[:3]
    data_txt = LB["date_fmt"].format(mes=LB["months"][int(mes) - 1], dia=int(dia), ano=ano) if ano else ""
    espaco = lambda tw: f"```{{=openxml}}\n<w:p><w:pPr><w:spacing w:after=\"{tw}\"/></w:pPr></w:p>\n```\n"
    rosto = [divs("FigureImage", f"![{LOGO_ALT}](fig-embed/{LOGO.name})"), espaco(1100), divs("CoverTitle", titulo)]
    if sub_t:
        rosto.append(divs("CoverSubtitle", sub_t))
    rosto += [espaco(1100), divs("CoverInfo", f"**{meta.get('author', '')}**")]
    if meta.get("affiliation"):
        rosto.append(divs("CoverInfo", meta["affiliation"]))
    if meta.get("orcid"):
        rosto.append(divs("CoverSmall", f"ORCID: {meta['orcid']}"))
    if data_txt:
        rosto += [espaco(1400), divs("CoverInfo", f"{LB['date']}: {data_txt}")]
    corpo = texto[corte:]

    rel["quebras_manuais"] = corpo.count("<!-- quebra-de-pagina -->")
    corpo = re.sub(r"<!--.*?-->[ \t]*\n?", "", corpo, flags=re.S)

    linhas = corpo.split("\n")
    saida: list[str] = []
    i, n = 0, len(linhas)
    em_refs = False
    figuras: list[dict] = []

    def legenda_completa(i0: int, primeira: str) -> tuple[str, int]:
        """Legenda de varias linhas: junta ate a linha em branco. Devolve (texto, proxima linha)."""
        txt, j = primeira.strip(), i0 + 1
        while j < n and linhas[j].strip() and not linhas[j].startswith(("|", "```", "![", "#")):
            txt += " " + linhas[j].strip()
            j += 1
        return txt, j

    while i < n:
        ln = linhas[i]
        if ln.startswith("## "):
            em_refs = ln.strip().startswith("## " + LB["refs"])
            saida.append(ln)
            i += 1
            continue
        # --- bloco de codigo (cerca ```): intocado; se a legenda `**Figure N.**` vem DEPOIS, ela sobe ---
        if ln.startswith("```"):
            j = i + 1
            while j < n and not linhas[j].startswith("```"):
                j += 1
            bloco = linhas[i:j + 1]
            k = j + 1
            while k < n and not linhas[k].strip():
                k += 1
            m_cap = RE_CAP.match(linhas[k]) if k < n else None
            rel["blocos_codigo"] += 1
            if m_cap and m_cap.group(1) == LB["figure"]:
                tipo, num = m_cap.group(1), m_cap.group(2)
                legenda, prox = legenda_completa(k, m_cap.group(3))
                titulo_e, nota_e = split_legenda(legenda)
                if nota_e:
                    rel["legendas_divididas"] += 1
                saida += [divs("CaptionLabel", f"{tipo} {num}"), divs("CaptionText", titulo_e), ""]
                saida += bloco + [""]
                if nota_e:
                    saida.append(divs("TableNote", f"*{LB['note']}* {nota_e.rstrip('.')}."))
                else:
                    rel["sem_nota"].append(f"{tipo} {num}")
                rel["figuras_codigo"] += 1
                i = prox
                continue
            saida += bloco
            i = j + 1
            continue
        if em_refs:
            if ln.startswith("- "):
                item = ln[2:].strip()
                while i + 1 < n and linhas[i + 1].strip() and not linhas[i + 1].startswith(("- ", "#")):
                    i += 1
                    item += " " + linhas[i].strip()
                saida.append(divs("Bibliography", escapa_travessao(item)))
            elif ln.strip():
                if RE_NOTA.match(ln):
                    saida.append(divs("TableNote", ln.strip()))
                else:                                   # referencia em paragrafo simples
                    item = ln.strip()
                    while i + 1 < n and linhas[i + 1].strip() and not linhas[i + 1].startswith(("#", "- ")):
                        i += 1
                        item += " " + linhas[i].strip()
                    saida.append(divs("Bibliography", escapa_travessao(item)))
            i += 1
            continue
        # --- rotulo + titulo de tabela: `**Table N.** titulo` + tabela + `*Note.*` opcional ---------------
        m_cap = RE_CAP.match(ln)
        if m_cap and m_cap.group(1) == LB["table"]:
            num = m_cap.group(2)
            legenda, j = legenda_completa(i, m_cap.group(3))
            titulo_e, nota_e = split_legenda(legenda)
            if nota_e:
                rel["legendas_divididas"] += 1
            saida += [divs("CaptionLabel", f"{LB['table']} {num}"), divs("CaptionText", escapa_travessao(titulo_e)), ""]
            while j < n and not linhas[j].strip():
                j += 1
            while j < n and linhas[j].startswith("|"):
                saida.append(linhas[j])
                j += 1
            saida.append("")
            k = j
            while k < n and not linhas[k].strip():
                k += 1
            if nota_e:
                saida.append(divs("TableNote", f"*{LB['note']}* {escapa_travessao(nota_e.rstrip('.'))}."))
            if k < n and RE_NOTA.match(linhas[k]):
                saida.append(divs("TableNote", escapa_travessao(linhas[k].strip())))
                j = k + 1
            elif not nota_e:
                rel["sem_nota"].append(f"{LB['table']} {num}")
            i = j
            continue
        # --- figura-imagem: `![Figure N. legenda](caminho)` ------------------------------------------------
        m_fig = RE_FIG_IMG.match(ln)
        if m_fig:
            num, legenda, caminho = m_fig.group(1), m_fig.group(2).strip(), m_fig.group(3)
            titulo_f, nota_f = split_legenda(legenda)
            if nota_f:
                rel["legendas_divididas"] += 1
            figuras.append({"num": int(num), "arquivo": caminho, "titulo": titulo_f, "nota": nota_f})
            saida += [divs("CaptionLabel", f"{LB['figure']} {num}"), divs("CaptionText", escapa_travessao(titulo_f)),
                      divs("FigureImage", f"![{LB['figure']} {num}](fig-embed/{Path(caminho).name})")]
            j = i + 1
            while j < n and not linhas[j].strip():
                j += 1
            if nota_f:
                saida.append(divs("TableNote", f"*{LB['note']}* {escapa_travessao(nota_f.rstrip('.'))}."))
            if j < n and RE_NOTA.match(linhas[j]):
                saida.append(divs("TableNote", linhas[j].strip()))
                i = j + 1
                continue
            if not nota_f:
                rel["sem_nota"].append(f"{LB['figure']} {num}")
            i += 1
            continue
        saida.append(escapa_travessao(ln))
        i += 1
    rel["figuras"] = figuras
    titulo_meta = re.sub(r"`", "", f"{titulo}: {sub_t}" if sub_t else titulo)
    return "\n".join(rosto) + "\n" + "\n".join(saida), {"meta": meta, "titulo": titulo_meta, "rel": rel}


def copiar_figuras(figuras: list[dict], work: Path, px: int, cores: int) -> None:
    saida = work / "fig-embed"
    saida.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LOGO, saida / LOGO.name)
    for f in figuras:
        img = Image.open(ROOT / f["arquivo"]).convert("RGB")
        f["px_orig"] = img.size
        if img.width > px:
            img = img.resize((px, round(img.height * px / img.width)), Image.LANCZOS)
        q = img.quantize(cores, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) if cores else img
        q.save(saida / Path(f["arquivo"]).name, optimize=True)


def largura_figuras(figuras: list[dict], pedido: str) -> tuple[float, list[dict]]:
    """Largura unica das figuras (cm). `pedido` = numero em cm ou 'auto'. Devolve (cm, tabela de folga)."""
    pagina_h = (CFG["pagina_twips"][1] - 2 * CFG["margem_twips"]) / 20   # pt uteis
    util_cm = (CFG["pagina_twips"][0] - 2 * CFG["margem_twips"]) / TWIPS_CM
    linha = 13.8                                                       # Times 12 simples no Word
    tabela = []
    for f in figuras:
        wpx, hpx = f["px_orig"]
        fixo = (ESP["rotulo"][1] + linha
                + linhas_de(f["titulo"], CFG["pt"], util_cm, "i") * linha + ESP["titulo_elem"][2]
                + ESP["imagem"][2]
                + ESP["nota"][1] + ESP["nota"][2]
                + (linhas_de("Nota. " + f["nota"], CFG["pt"], util_cm) * linha if f["nota"] else 0)
                + linha                                                  # Fonte
                + MARGEM_SEGURANCA_FIG_PT)
        h_max_pt = pagina_h - fixo
        max_cm = h_max_pt / 72 * 2.54 * wpx / hpx
        tabela.append({"num": f["num"], "aspecto": round(hpx / wpx, 2), "max_cm": round(max_cm, 2)})
    teto = CFG["fig_largura_cm"]
    menor = min((t["max_cm"] for t in tabela), default=teto)
    if pedido == "auto":
        return math.floor(min(teto, menor) * 10) / 10, tabela
    cm = float(pedido)
    return cm, tabela


# --------------------------------------------------------------------------- #
# 3. estilos                                                                   #
# --------------------------------------------------------------------------- #
def rfonts() -> etree._Element:
    return mk("rFonts", ascii=TNR, hAnsi=TNR, cs=TNR, eastAsia=TNR)


def spacing_el(par: tuple[float, float, float]) -> etree._Element:
    linha, antes, depois = par
    return mk("spacing", before=int(antes * 20), after=int(depois * 20), line=int(round(linha * 240)),
              lineRule="auto")


def estilo_par(sid: str, nome: str, par_esp: tuple[float, float, float], base: str | None = "Normal",
               jc: str = "left", recuo: tuple[int, int, int] | None = (0, 0, 0), bold: bool = False,
               italic: bool = False, keep_next: bool = False, page_break: bool = False,
               outline: int | None = None, proximo: str | None = None, custom: bool = True,
               sz: int | None = None, keep_lines: bool = False) -> etree._Element:
    """Estilo de paragrafo completo. `recuo` = (left, right, firstLine ou -hanging)."""
    st = mk("style", type="paragraph", styleId=sid)
    if custom:
        st.set(w("customStyle"), "1")
    sub(st, "name", val=nome)
    if base:
        sub(st, "basedOn", val=base)
    if proximo:
        sub(st, "next", val=proximo)
    sub(st, "qFormat")
    ppr = sub(st, "pPr")
    if keep_next:
        sub(ppr, "keepNext")
    if keep_next or keep_lines:
        sub(ppr, "keepLines")
    if page_break:
        sub(ppr, "pageBreakBefore")
    sub(ppr, "widowControl")
    ppr.append(spacing_el(par_esp))
    if recuo is not None:
        esq, dir_, prim = recuo
        ind = sub(ppr, "ind", left=esq, right=dir_)
        ind.set(w("hanging") if prim < 0 else w("firstLine"), str(abs(prim)))
    sub(ppr, "jc", val=jc)
    if outline is not None:
        sub(ppr, "outlineLvl", val=outline)
    rpr = sub(st, "rPr")
    rpr.append(rfonts())
    if bold:
        sub(rpr, "b")
        sub(rpr, "bCs")
    if italic:
        sub(rpr, "i")
        sub(rpr, "iCs")
    sub(rpr, "sz", val=sz or CFG["pt"] * 2)
    sub(rpr, "szCs", val=sz or CFG["pt"] * 2)
    return st


def estilo_code() -> etree._Element:
    """Bloco de codigo: Courier New, espaco simples, a esquerda, nao parte entre paginas (o tamanho vai no run)."""
    st = estilo_par("CodeBlock", "CodeBlock", ESP["codigo"], keep_lines=True, sz=CODE_PT_MAX * 2)
    for rf in st.iter(w("rFonts")):
        for a in ("ascii", "hAnsi", "cs", "eastAsia"):
            rf.set(w(a), MONO)
    return st


def construir_estilos() -> list[etree._Element]:
    rec = CFG["recuo_twips"]
    pt_t = CFG["pt_tabela"] * 2
    return [
        # norma Codex Hash (CODEX-HASH-STYLE.md §2): corpo justificado sem recuo; titulos decimais em negrito a
        # esquerda, sem quebra de pagina no estilo (a quebra vai direto em Resumo/Abstract/1. Introducao/Referencias
        # e, por quebra manual, em cada apendice; ver quebras_de_pagina)
        estilo_par("Normal", "Normal", ESP["corpo"], base=None, jc="both", recuo=(0, 0, 0), custom=False),
        estilo_par("Heading1", "heading 1", ESP["titulo1"], jc="left", bold=True, keep_next=True,
                   outline=0, proximo="Normal", custom=False),
        estilo_par("Heading2", "heading 2", ESP["titulo2"], jc="left", bold=True, keep_next=True,
                   outline=1, proximo="Normal", custom=False),
        estilo_par("Heading3", "heading 3", ESP["titulo2"], jc="left", bold=True, keep_next=True,
                   outline=2, proximo="Normal", custom=False),
        estilo_par("Lista", "Lista", ESP["lista"], recuo=(rec, 0, -360)),
        # referencias a esquerda (APA 7): justificadas, as linhas com URL longa abriam vaos grandes
        estilo_par("Bibliography", "Bibliography", ESP["referencia"], recuo=(rec, 0, -rec)),
        estilo_par("CaptionLabel", "CaptionLabel", ESP["rotulo"], bold=True, keep_next=True),
        estilo_par("CaptionText", "CaptionText", ESP["titulo_elem"], italic=True, keep_next=True),
        estilo_par("FigureImage", "FigureImage", ESP["imagem"], jc="center", keep_next=True),
        estilo_par("TableNote", "TableNote", ESP["nota"], keep_lines=True),   # Nota nunca parte entre paginas (fica com a figura)
        estilo_par("Compact", "Compact", ESP["celula"], sz=pt_t),
        estilo_code(),
        # capa da casa (exemplar operating-point-dominance): logo, titulo 14 pt, subtitulo italico, autor, laboratorio,
        # ORCID e data, sem numero de pagina (titlePg)
        estilo_par("CoverOrg", "CoverOrg", (2.0, 12, 12), jc="center", bold=True, sz=28),
        estilo_par("CoverTitle", "CoverTitle", (2.0, 12, 6), jc="center", bold=True, sz=28),
        estilo_par("CoverSubtitle", "CoverSubtitle", (2.0, 0, 6), jc="center", italic=True),
        estilo_par("CoverInfo", "CoverInfo", (2.0, 0, 6), jc="center"),
        estilo_par("CoverSmall", "CoverSmall", (1.5, 0, 3), jc="center", sz=22),
        estilo_par("Cabecalho", "header", ESP["cabecalho"], jc="right", custom=False),
    ]


def estilo_char_hyperlink() -> etree._Element:
    st = mk("style", type="character", styleId="Hyperlink")
    sub(st, "name", val="Hyperlink")
    sub(st, "basedOn", val="DefaultParagraphFont")
    sub(st, "uiPriority", val=99)
    return st


def estilo_tabela() -> etree._Element:
    st = mk("style", type="table", styleId="Table")
    st.set(w("customStyle"), "1")
    sub(st, "name", val="Table")
    sub(st, "basedOn", val="TableNormal")
    tpr = sub(st, "tblPr")
    mar = sub(tpr, "tblCellMar")
    for lado, v in (("top", 20), ("left", 72), ("bottom", 20), ("right", 72)):
        sub(mar, lado, w=v, type="dxa")
    return st


def sanear_estilos(raiz: etree._Element) -> None:
    """Substitui os estilos que a casa define, apaga os proibidos e tira o tema de fonte de todo o resto."""
    novos = {e.get(w("styleId")): e for e in construir_estilos()}
    novos["Hyperlink"] = estilo_char_hyperlink()
    novos["Table"] = estilo_tabela()
    apagar = {"Compact", "SourceCode", "VerbatimChar", "BodyText", "FirstParagraph", "BodyTextChar"}
    for st in list(raiz.findall(w("style"))):
        sid = st.get(w("styleId"))
        if sid in apagar or sid.endswith("Tok"):
            raiz.remove(st)
        elif sid in novos:
            st.addprevious(novos.pop(sid))
            raiz.remove(st)
    ultimo = raiz.findall(w("style"))[-1]
    for sid, el in novos.items():
        ultimo.addnext(el)
        ultimo = el
    # docDefaults: Times 12, en-US, sem tema
    dd = raiz.find(w("docDefaults"))
    if dd is not None:
        raiz.remove(dd)
    dd = mk("docDefaults")
    rd = sub(dd, "rPrDefault")
    rpr = sub(rd, "rPr")
    rpr.append(rfonts())
    sub(rpr, "sz", val=CFG["pt"] * 2)
    sub(rpr, "szCs", val=CFG["pt"] * 2)
    sub(rpr, "lang", val=LB["code"], eastAsia=LB["code"], bidi="ar-SA")
    pd = sub(dd, "pPrDefault")
    sub(pd, "pPr")
    raiz.insert(0, dd)
    # qualquer estilo restante: Times, sem tema, sem cor azul/cinza de titulo
    for rf in raiz.iter(w("rFonts")):
        pai = next((a for a in rf.iterancestors() if a.tag == w("style")), None)
        mono = pai is not None and pai.get(w("styleId")) == "CodeBlock"
        for a in list(rf.attrib):
            if a.split("}")[1] in THEME_ATTRS:
                del rf.attrib[a]
        for a in ("ascii", "hAnsi", "cs", "eastAsia"):
            rf.set(w(a), MONO if mono else TNR)
    for st in raiz.findall(w("style")):
        if st.get(w("styleId")) in ("Hyperlink",):
            continue
        for c in st.iter(w("color")):
            c.getparent().remove(c)
    for tag in ("shd",):
        for el in list(raiz.iter(w(tag))):
            el.getparent().remove(el)


# --------------------------------------------------------------------------- #
# 4. ordenacao canonica de filhos (o esquema OOXML e sequencia, nao conjunto)  #
# --------------------------------------------------------------------------- #
ORD_PPR = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
           "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
           "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid",
           "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
           "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]
ORD_RPR = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline",
           "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing", "w",
           "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText", "vertAlign",
           "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath"]
ORD_TCPR = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar",
            "textDirection", "tcFitText", "vAlign", "hideMark"]
ORD_TBLPR = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize",
             "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook",
             "tblCaption", "tblDescription"]
ORD_SECT = ["headerReference", "footerReference", "footnotePr", "endnotePr", "type", "pgSz", "pgMar", "paperSrc",
            "pgBorders", "lnNumType", "pgNumType", "cols", "formProt", "vAlign", "noEndnote", "titlePg",
            "textDirection", "bidi", "rtlGutter", "docGrid"]


def ordenar(el: etree._Element, ordem: list[str]) -> None:
    def chave(c: etree._Element) -> int:
        nome = etree.QName(c).localname
        return ordem.index(nome) if nome in ordem else len(ordem)
    filhos = sorted(list(el), key=chave)       # sorted e estavel
    for c in filhos:
        el.remove(c)
    for c in filhos:
        el.append(c)


def get_or_add(pai: etree._Element, tag: str) -> etree._Element:
    el = pai.find(w(tag))
    return el if el is not None else sub(pai, tag)


def set_mono_run(r: etree._Element, pt: float) -> None:
    rpr = get_or_add(r, "rPr")
    r.remove(rpr)
    r.insert(0, rpr)
    old = rpr.find(w("rFonts"))
    if old is not None:
        rpr.remove(old)
    rpr.append(mk("rFonts", ascii=MONO, hAnsi=MONO, cs=MONO, eastAsia=MONO))
    for t in ("sz", "szCs"):
        e = rpr.find(w(t))
        if e is None:
            e = sub(rpr, t)
        e.set(w("val"), str(int(pt * 2)))
    ordenar(rpr, ORD_RPR)


def set_fonte_run(r: etree._Element, pt: int) -> None:
    rpr = get_or_add(r, "rPr")
    r.remove(rpr)
    r.insert(0, rpr)
    old = rpr.find(w("rFonts"))
    if old is not None:
        rpr.remove(old)
    rpr.append(rfonts())
    for t in ("sz", "szCs"):
        e = rpr.find(w(t))
        if e is None:
            e = sub(rpr, t)
        e.set(w("val"), str(pt * 2))
    ordenar(rpr, ORD_RPR)


# --------------------------------------------------------------------------- #
# 5. corpo do documento                                                        #
# --------------------------------------------------------------------------- #
def texto_de(el: etree._Element) -> str:
    return "".join(t.text or "" for t in el.iter(w("t")))


def estilo_de(p: etree._Element) -> str:
    ps = p.find(f"{w('pPr')}/{w('pStyle')}")
    return ps.get(w("val")) if ps is not None else "Normal"


def set_estilo(p: etree._Element, sid: str | None) -> None:
    ppr = get_or_add(p, "pPr")
    if p.index(ppr) != 0:
        p.remove(ppr)
        p.insert(0, ppr)
    ps = ppr.find(w("pStyle"))
    if sid in (None, "Normal"):
        if ps is not None:
            ppr.remove(ps)
        return
    if ps is None:
        ps = sub(ppr, "pStyle")
    ps.set(w("val"), sid)


def pxml(p: etree._Element) -> etree._Element:
    return get_or_add(p, "pPr")


def zwsp_token(token: str) -> str:
    """Oportunidade de quebra em token longo de CELULA (nome de arquivo, hash); URL de referencia fica intacta."""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T[\d:]+Z?", token):
        return token  # carimbo de data e hora fica inteiro (Tabela B3 partia em "2026-10-" / "22T21:19:32Z")
    if len(token) >= 30 and not re.search(r"[-._/]", token):
        return ZWSP.join(token[i:i + 12] for i in range(0, len(token), 12))
    if len(token) >= 14:
        return re.sub(r"([-._/])(?=[^-._/])", r"\1" + ZWSP, token)
    return token


def blocos(corpo: etree._Element) -> list[etree._Element]:
    return list(corpo)


def formatar_corpo(doc: etree._Element, media: dict[str, Path], fig_cm: float, rel: dict) -> dict:
    corpo = doc.find(w("body"))
    inf = {"tabelas": [], "paisagem": [], "figuras": 0, "listas": 0, "codigo": 0}

    # 5.0 bloco de codigo (pStyle SourceCode do pandoc): estilo CodeBlock, Courier New, tamanho pela linha mais longa
    codigo_runs: set = set()
    inf["blocos_codigo"] = []
    em_branco = rel.get("blank_numids", set())

    def continuacao(p: etree._Element) -> int | None:
        """Se p e o 2o bloco de um item de lista (numPr em branco do pandoc): tira o numPr e devolve o recuo em twips."""
        npr = p.find(f"{w('pPr')}/{w('numPr')}")
        if npr is None or npr.find(w("numId")).get(w("val")) not in em_branco:
            return None
        ilvl = int(npr.find(w("ilvl")).get(w("val")))
        npr.getparent().remove(npr)
        return CFG["recuo_twips"] * (ilvl + 1)

    for p in corpo.iter(w("p")):
        if estilo_de(p) != "SourceCode":
            continue
        recuo_cont = continuacao(p)
        linhas, atual = [], ""
        for r in p.findall(w("r")):
            for fe in r:
                if fe.tag == w("t"):
                    atual += fe.text or ""
                elif fe.tag == w("br"):
                    linhas.append(atual)
                    atual = ""
        linhas.append(atual)
        mais_longa = max(len(x.expandtabs(4)) for x in linhas)
        util_pt = (CFG["pagina_twips"][0] - 2 * CFG["margem_twips"] - (recuo_cont or 0)) / 20
        pt = CODE_PT_MAX
        while pt > CODE_PT_MIN and 0.6 * pt * mais_longa > util_pt:
            pt -= 0.5
        larg = 0.6 * pt * mais_longa
        inf["blocos_codigo"].append({"linhas": len(linhas), "colunas": mais_longa, "pt": pt, "largura_pt": round(larg, 1),
                                     "util_pt": util_pt, "cabe": larg <= util_pt})
        set_estilo(p, "CodeBlock")
        if recuo_cont:
            get_or_add(pxml(p), "ind").attrib.update({w("left"): str(recuo_cont), w("hanging"): "0"})
        for r in p.findall(w("r")):
            rs = r.find(f"{w('rPr')}/{w('rStyle')}")
            if rs is not None:
                rs.getparent().remove(rs)
            set_mono_run(r, pt)
            codigo_runs.add(r)

    # 5.1 runs: Times 12 em tudo (tabela recebe o tamanho dela depois); codigo inline vira texto Times
    for r in corpo.iter(w("r")):
        if r in codigo_runs:
            continue
        rs = r.find(f"{w('rPr')}/{w('rStyle')}")
        if rs is not None and rs.get(w("val")) == "VerbatimChar":
            rs.getparent().remove(rs)
            inf["codigo"] += 1
            codigo_runs.add(r)             # inline: Times, mas o menos tipografico nao o toca
        set_fonte_run(r, CFG["pt"])

    # 5.1b sinal de menos tipografico (U+2212) antes de digito, fora de palavra/numero: o Word quebra a linha
    # depois do hifen ("-12,3%" virava "-" no fim da linha e "12,3%" na seguinte; "[-0,0228" idem). Codigo fica de fora.
    if CFG["menos_tipografico"]:
        for t in corpo.iter(w("t")):
            if t.text and "-" in t.text and t.getparent() not in codigo_runs:
                t.text = re.sub(r"(?<!\w)-(?=\d)", "\u2212", t.text)

    # 5.2 paragrafos
    paragrafos = list(corpo.iter(w("p")))
    for p in paragrafos:
        em_tabela = any(a.tag == w("tc") for a in p.iterancestors())
        sid = estilo_de(p)
        if sid != "CodeBlock":
            recuo_cont = continuacao(p)
            if recuo_cont:                          # 2o paragrafo de um item de lista: recuo, sem marcador
                set_estilo(p, "Lista")
                get_or_add(pxml(p), "ind").attrib.update({w("left"): str(recuo_cont), w("hanging"): "0"})
                continue
        tem_lista = p.find(f"{w('pPr')}/{w('numPr')}") is not None
        if em_tabela:
            set_estilo(p, "Compact")
            continue
        if tem_lista and sid != "CodeBlock":
            set_estilo(p, "Lista")
            inf["listas"] += 1
        elif sid in ("FirstParagraph", "BodyText", "Compact"):
            set_estilo(p, None)

    # 5.2b marca de paragrafo em Times 12 (o rotulo de lista numerada herda a fonte da marca: sem isto o Word
    # desenha o espaco depois de "1." em Arial)
    for p in corpo.iter(w("p")):
        ppr = pxml(p)
        em_tab = any(a.tag == w("tc") for a in p.iterancestors())
        rp = ppr.find(w("rPr"))
        if rp is not None:
            ppr.remove(rp)
        rp = sub(ppr, "rPr")
        if estilo_de(p) == "CodeBlock":
            rp.append(mk("rFonts", ascii=MONO, hAnsi=MONO, cs=MONO, eastAsia=MONO))
            szp = next((r.find(f"{w('rPr')}/{w('sz')}").get(w("val")) for r in p.findall(w("r"))
                        if r.find(f"{w('rPr')}/{w('sz')}") is not None), str(CODE_PT_MAX * 2))
            for t in ("sz", "szCs"):
                sub(rp, t, val=szp)
            continue
        rp.append(rfonts())
        for t in ("sz", "szCs"):
            sub(rp, t, val=(CFG["pt_tabela"] if em_tab else CFG["pt"]) * 2)

    # 5.3 recuo do corpo: Resumo e Abstract sem recuo (APA); titulo/rotulo/nota/legenda ja vem do estilo
    atual = ""
    for el in list(corpo):
        if el.tag != w("p"):
            continue
        sid = estilo_de(el)
        if sid in ("Heading1", "Heading2"):
            atual = texto_de(el).strip() if sid == "Heading1" else atual
            continue
        if sid == "Normal" and atual in rotulos.TODOS_RESUMOS:
            t = texto_de(el).strip()
            if not t.startswith(rotulos.TODOS_KEYWORDS):
                ind = get_or_add(pxml(el), "ind")
                ind.set(w("firstLine"), "0")
        if sid == "Normal" and el.find(f".//{w('drawing')}") is not None:   # imagem solta: sem recuo
            get_or_add(pxml(el), "ind").set(w("firstLine"), "0")

    # 5.4 espaco depois do paragrafo/titulo que antecede uma lista
    ant = None
    for el in list(corpo):
        eh_lista = el.tag == w("p") and estilo_de(el) == "Lista"
        if eh_lista and ant is not None and ant.tag == w("p") and estilo_de(ant) != "Lista":
            sp = get_or_add(pxml(ant), "spacing")
            sp.set(w("after"), str(LISTA_DEPOIS_PT * 20))
        ant = el

    # 5.5 figuras: largura unica, alt-text sem caminho
    emu = int(fig_cm * EMU_CM)
    for inline in corpo.iter(f"{{{WP}}}inline"):
        if inline.find(f"{{{WP}}}docPr").get("descr") == LOGO_ALT:      # logo da capa: 5,2 cm, fora da largura unica
            cx = int(LOGO_CM * EMU_CM)
            ext = inline.find(f"{{{WP}}}extent")
            cy = round(cx * int(ext.get("cy")) / int(ext.get("cx")))
            for e in (ext, inline.find(f".//{{{A}}}ext")):
                e.attrib.update({"cx": str(cx), "cy": str(cy)})
            continue
        blip = inline.find(f".//{{{A}}}blip")
        rid = blip.get(f"{{{R}}}embed")
        arquivo = media[rid]
        with Image.open(arquivo) as im:
            wpx, hpx = im.size
        cy = round(emu * hpx / wpx)
        inline.find(f"{{{WP}}}extent").attrib.update({"cx": str(emu), "cy": str(cy)})
        ext = inline.find(f".//{{{A}}}ext")
        ext.attrib.update({"cx": str(emu), "cy": str(cy)})
        docpr = inline.find(f"{{{WP}}}docPr")
        for cnv in inline.iter(f"{{{PIC}}}cNvPr"):
            cnv.set("descr", docpr.get("descr", "Figure"))
            cnv.set("name", "Figure")
        docpr.set("name", "Figure")
        docpr.set("title", "")
        inf["figuras"] += 1

    # 5.6 tabelas
    for tbl in list(corpo.iter(w("tbl"))):
        inf["tabelas"].append(formatar_tabela(tbl))

    # 5.7 capa: o tamanho vem do estilo (titulo 14 pt, ORCID 11 pt), nao do 12 pt forcado em 5.1
    for p in corpo.iter(w("p")):
        if estilo_de(p).startswith("Cover"):
            for r in p.iter(w("r")):
                rpr = r.find(w("rPr"))
                for tag in ("sz", "szCs"):
                    for el in rpr.findall(w(tag)) if rpr is not None else []:
                        rpr.remove(el)
    quebras_de_pagina(corpo)
    for cb in corpo.iter(w("p")):                    # frase que apresenta o bloco de codigo fica com ele
        if estilo_de(cb) == "CodeBlock" and cb.getprevious() is not None and cb.getprevious().tag == w("p"):
            ant = cb.getprevious()
            if estilo_de(ant) not in ("CaptionText", "CaptionLabel"):
                get_or_add(pxml(ant), "keepNext")
                ordenar(pxml(ant), ORD_PPR)
    inf["espaco_sem_nota"] = espaco_sem_nota(corpo)
    for par in corpo.iter(w("p")):  # hash ou caminho longo nao parte: no justificado ele esticava a linha anterior
        # o mesmo vale para caminho de arquivo longo (token sem espaco de 35+ caracteres)
        if re.search(r"[^\s]{35,}", texto_de(par).replace(ZWSP, "")) and par.getparent().tag != w("tc"):
            ppr = pxml(par)
            for old in ppr.findall(w("jc")):
                ppr.remove(old)
            sub(ppr, "jc", val="left")
            ordenar(ppr, ORD_PPR)
    return inf


def espaco_sem_nota(corpo: etree._Element) -> int:
    """Tabela ou figura sem Nota: o paragrafo seguinte ganha 12 pt antes (a Nota daria esse espaco)."""
    n = 0
    for el in list(corpo):
        fim_figura = el.tag == w("p") and estilo_de(el) in ("FigureImage",) and el.find(f".//{w('drawing')}") is not None \
            and el.find(f".//{{{WP}}}docPr").get("descr") != LOGO_ALT
        if el.tag != w("tbl") and not fim_figura:
            continue
        nxt = el.getnext()
        if nxt is None or nxt.tag != w("p") or estilo_de(nxt) == "TableNote":
            continue
        if fim_figura:                                  # figura sem Nota: nao prende no paragrafo seguinte
            get_or_add(pxml(el), "keepNext").set(w("val"), "0")
        if estilo_de(nxt) in ("Heading1", "Heading2", "Heading3", "CodeBlock"):
            continue                                   # titulo ja tem 12 pt antes
        sp = get_or_add(pxml(nxt), "spacing")
        if int(sp.get(w("before"), "0")) < 240:
            sp.set(w("before"), "240")
            ordenar(pxml(nxt), ORD_PPR)
            n += 1
    return n


def quebras_de_pagina(corpo: etree._Element) -> None:
    """Canon en: pageBreakBefore so em Abstract, 1. e References; cada apendice comeca em pagina nova por quebra
    manual no proprio titulo (APA 7: cada apendice em pagina propria), sem contar como pageBreakBefore."""
    for p in corpo.iter(w("p")):
        if estilo_de(p) != "Heading1":
            continue
        t = texto_de(p).strip()
        if quebra_direta(t):
            sub(pxml(p), "pageBreakBefore")
        elif re.match(rf"^{re.escape(LB['appendix'])} [A-Z] —", t):
            r = mk("r")
            sub(r, "br", type="page")
            pxml(p).addnext(r)


# --------------------------------------------------------------------------- #
# 6. tabelas APA                                                               #
# --------------------------------------------------------------------------- #
def celula_texto(tc: etree._Element) -> list[tuple[str, bool]]:
    saida = []
    for p in tc.iter(w("p")):
        for r in p.iter(w("r")):
            negrito = r.find(f"{w('rPr')}/{w('b')}") is not None
            for t in r.iter(w("t")):
                saida.append((t.text or "", negrito))
    return saida


def larguras_coluna(linhas: list[list[etree._Element]], ncol: int, pt: int, util: int,
                    folga: float = 1.0) -> list[int] | None:
    """Reparte `util` twips: piso = maior pedaco indivisivel (Times real), alvo = maior celula em uma linha."""
    pad = 2 * 72 + 30
    pisos, alvos = [0.0] * ncol, [0.0] * ncol
    for k, linha in enumerate(linhas):
        for i, tc in enumerate(linha[:ncol]):
            partes = celula_texto(tc)
            estilo = "b" if k == 0 else "r"
            txt = "".join(t for t, _ in partes)
            for tok in re.split(r"[ \t\n]+", txt):  # o espaco que nao quebra (intervalo) fica dentro do pedaco
                iso = re.fullmatch(r"\d{4}-\d{2}-\d{2}T[\d:]+Z?", tok)  # carimbo de data e hora conta inteiro
                for pedaco in [tok] if iso else re.split(f"{ZWSP}|(?<=-)", tok):
                    pisos[i] = max(pisos[i], largura_pt(pedaco, pt, estilo) * 20)
            larg = largura_pt(txt.replace(ZWSP, ""), pt, estilo) * 20
            if k == 0:                       # cabecalho pode quebrar em varias linhas: pesa pouco no alvo
                larg = min(larg, 1500)
            alvos[i] = max(alvos[i], larg)
    pisos = [p + pad for p in pisos]
    alvos = [max(min(a, util * 0.45) + pad, p) for a, p in zip(alvos, pisos)]
    if sum(pisos) > util * folga:
        return None
    if sum(alvos) <= util:
        larg = [a * util / sum(alvos) for a in alvos]
    else:
        folga = util - sum(pisos)
        extra = [a - p for a, p in zip(alvos, pisos)]
        larg = [p + folga * e / max(sum(extra), 1) for p, e in zip(pisos, extra)]
    inteiros = [int(x) for x in larg]
    inteiros[-1] += util - sum(inteiros)
    return inteiros


def formatar_tabela(tbl: etree._Element, forcar_paisagem: bool = False) -> dict:
    nxt = tbl.getnext()
    tem_nota = nxt is not None and nxt.tag == w("p") and estilo_de(nxt) == "TableNote"
    linhas_tr = tbl.findall(w("tr"))
    linhas = [tr.findall(w("tc")) for tr in linhas_tr]
    ncol = len(linhas[0])
    util_ret = CFG["pagina_twips"][0] - 2 * CFG["margem_twips"]
    util_pai = CFG["pagina_twips"][1] - 2 * CFG["margem_twips"]
    # oportunidade de quebra em token longo (so dentro de celula)
    for tc in (c for linha in linhas for c in linha):
        for t in tc.iter(w("t")):
            if t.text:  # intervalo numerico nao parte entre linhas (colunas estreitas partiam "(2,58 a" / "8,90)")
                t.text = re.sub(r"([\d%]|p\.p\.) a ([+\-−]?\d)", "\\1\u00a0a\u00a0\\2", t.text)  # "(−19,1 a +10,8)", "47,38% a"
                t.text = re.sub(r"(\[[^\]\s;]+;) ([^\]\s]+\])", "\\1\u00a0\\2", t.text)  # "[3,57; 4,08]"
            if t.text and any(len(x) >= 14 for x in t.text.split()):
                t.text = " ".join(zwsp_token(x) for x in t.text.split(" "))
    # pisos somados tem de caber com folga (FOLGA_COLUNAS): sem folga a coluna de texto fica estreita demais
    # (Tabela 8: "Lula, 1o mandato (2003 a 2006)" quebrava em 4 linhas). Ordem: retrato 10..8 pt, paisagem 10..8 pt,
    # e so entao retrato a 8 pt sem folga.
    escolha = None
    tentativas = ([(False, pt, FOLGA_COLUNAS) for pt in range(CFG["pt_tabela"], CFG["pt_tabela_min"] - 1, -1)]
                  + [(True, pt, FOLGA_COLUNAS) for pt in range(CFG["pt_tabela"], CFG["pt_tabela_min"] - 1, -1)]
                  + [(False, CFG["pt_tabela_min"], 1.0)])
    if forcar_paisagem:
        tentativas = [t for t in tentativas if t[0]]
    for paisagem, pt, folga in tentativas:
        util = util_pai if paisagem else util_ret
        lg = larguras_coluna(linhas, ncol, pt, util, folga)
        if lg:
            escolha = (pt, lg, paisagem)
            break
    aviso = ""
    if not escolha:                              # nem em paisagem a 8 pt: piso proporcional (quebra por caractere)
        pt = CFG["pt_tabela_min"]
        lg = larguras_coluna(linhas, ncol, pt, 10 ** 7)
        fator = util_pai / sum(lg)
        lg = [int(x * fator) for x in lg]
        escolha, aviso = (pt, lg, True), "nem em paisagem a 8 pt: colunas espremidas"
    pt, lg, paisagem = escolha

    # tblPr limpo: sem preenchimento, so filetes horizontais (topo e base); a regua sob o cabecalho vai por celula
    for filho in list(tbl.find(w("tblPr"))):
        tbl.find(w("tblPr")).remove(filho)
    tpr = tbl.find(w("tblPr"))
    sub(tpr, "tblStyle", val="Table")
    sub(tpr, "tblW", w=sum(lg), type="dxa")
    sub(tpr, "tblInd", w=0, type="dxa")
    br = sub(tpr, "tblBorders")
    for lado in ("top", "bottom"):
        sub(br, lado, val="single", sz=CFG["regua_sz"], space=0, color="auto")
    sub(tpr, "tblLayout", type="fixed")
    mar = sub(tpr, "tblCellMar")
    for lado, v in (("top", 20), ("left", 72), ("bottom", 20), ("right", 72)):
        sub(mar, lado, w=v, type="dxa")
    sub(tpr, "tblLook", val="0420", firstRow=1, lastRow=0, firstColumn=0, lastColumn=0, noHBand=1, noVBand=1)
    ordenar(tpr, ORD_TBLPR)
    grade = tbl.find(w("tblGrid"))
    for g in list(grade):
        grade.remove(g)
    for x in lg:
        sub(grade, "gridCol", w=x)

    n = len(linhas_tr)
    # altura estimada (linhas de texto por linha da tabela, na largura de cada coluna) contra 70% da altura util da
    # pagina; a estimativa subestima (sem espaco entre paragrafos): calibrada no PDF de 2026-11-01, so a I1 passa
    linhas_txt = [max(math.ceil(largura_pt(texto_de(tc), pt) * 20 / max(lg[i] - 174, 1)) for i, tc in enumerate(tcs[:ncol]))
                  for tcs in linhas]
    alta = sum(linhas_txt) * pt * 1.2 > 0.7 * ((CFG["pagina_twips"][0 if paisagem else 1] - 2 * CFG["margem_twips"]) / 20)
    for k, (tr, tcs) in enumerate(zip(linhas_tr, linhas)):
        trpr = tr.find(w("trPr"))
        if trpr is not None:
            tr.remove(trpr)
        trpr = mk("trPr")
        tr.insert(0, trpr)
        sub(trpr, "cantSplit")
        if k == 0:
            sub(trpr, "tblHeader")
        # linha de subcabeçalho dentro da tabela ("Onde (V019) | n heterossexuais = 3.112 | n LGB+ = 179"): fica com
        # a linha seguinte, para não sobrar sozinha no pé da página (leitura do PDF v0.5, Tabela C4)
        sub_cab = k > 0 and len(tcs) > 1 and all(texto_de(tc).strip().startswith("n ") for tc in tcs[1:])
        for i, tc in enumerate(tcs):
            tcpr = tc.find(w("tcPr"))
            if tcpr is not None:
                tc.remove(tcpr)
            tcpr = mk("tcPr")
            tc.insert(0, tcpr)
            sub(tcpr, "tcW", w=lg[i], type="dxa")
            if k == 0:
                tb = sub(tcpr, "tcBorders")
                sub(tb, "bottom", val="single", sz=CFG["regua_sz"], space=0, color="auto")
            ordenar(tcpr, ORD_TCPR)
            for p in tc.findall(w("p")):
                ppr = pxml(p)
                set_estilo(p, "Compact")
                for old in ppr.findall(w("keepNext")):
                    ppr.remove(old)
                # sem Nota, a ultima linha NAO prende no que vem depois (senao a tabela arrasta a figura e o texto seguintes)
                if (_prender(k, n, alta) and (tem_nota or k < n - 1)) or sub_cab:
                    sub(ppr, "keepNext")
                for r in p.iter(w("r")):
                    set_fonte_run(r, pt)
                    if k == 0:
                        rpr = r.find(w("rPr"))
                        if rpr.find(w("b")) is None:
                            sub(rpr, "b")
                            sub(rpr, "bCs")
                        ordenar(rpr, ORD_RPR)
                ordenar(ppr, ORD_PPR)
    return {"pt": pt, "linhas": n, "colunas": ncol, "paisagem": paisagem, "aviso": aviso, "tbl": tbl}


def _prender(k: int, n: int, alta: bool = False) -> bool:
    """Linha k (0 = cabecalho) fica com a seguinte: nunca 1 linha sozinha no fim nem no comeco de pagina.

    Cabecalho + 1a linha de dados + 2a ficam juntos; penultima + ultima + Nota ficam juntas. Tabela curta
    (<= 10 linhas de dados) inteira numa pagina so: na v0.5 tabelas de 8 linhas partiam em 6 + 2 com a
    pagina meio vazia (leitura do PDF, Tabelas 3 e 5); se nao couber, o Word parte do mesmo jeito.
    """
    dados = n - 1
    if dados <= 10 and not alta:  # alta = enche a pagina: presa inteira, o Word a parte e a Nota cai sozinha (Tabela I1)
        return True                      # a ultima tambem: a Nota nunca fica sozinha na pagina seguinte
    return k in (0, 1) or k >= n - 2


# --------------------------------------------------------------------------- #
# 7. secoes, cabecalho com numero de pagina, paisagem                          #
# --------------------------------------------------------------------------- #
def sect(paisagem: bool, tipo_proxima: bool = True) -> etree._Element:
    s = mk("sectPr")
    sub(s, "headerReference", type="default").set(f"{{{R}}}id", "rIdCabV04")
    if tipo_proxima:
        sub(s, "type", val="nextPage")
    wp_, hp_ = CFG["pagina_twips"]
    if paisagem:
        sub(s, "pgSz", w=hp_, h=wp_, orient="landscape")
    else:
        sub(s, "pgSz", w=wp_, h=hp_)
    m = CFG["margem_twips"]
    sub(s, "pgMar", top=m, right=m, bottom=m, left=m, header=CFG["cabecalho_twips"],
        footer=CFG["cabecalho_twips"], gutter=0)
    sub(s, "cols", space=720)
    ordenar(s, ORD_SECT)
    return s


def par_secao(paisagem_que_termina: bool) -> etree._Element:
    """Paragrafo minusculo que carrega o sectPr da secao que TERMINA nele (OOXML)."""
    p = mk("p")
    ppr = sub(p, "pPr")
    sub(ppr, "spacing", before=0, after=0, line=20, lineRule="exact")
    sub(ppr, "ind", firstLine=0)
    rpr = sub(ppr, "rPr")
    rpr.append(rfonts())
    sub(rpr, "sz", val=2)
    sub(rpr, "szCs", val=2)
    ppr.append(sect(paisagem_que_termina))
    ordenar(ppr, ORD_PPR)
    return p


def aplicar_secoes(corpo: etree._Element, infos: list[dict]) -> int:
    """Cada tabela marcada paisagem ganha secao propria (rotulo + titulo + tabela + Nota)."""
    n = 0
    for inf in infos:
        if not inf["paisagem"]:
            continue
        tbl = inf["tbl"]
        ini = tbl
        while ini.getprevious() is not None and estilo_de(ini.getprevious()) in ("CaptionText", "CaptionLabel"):
            ini = ini.getprevious()
        fim = tbl
        while fim.getnext() is not None and fim.getnext().tag == w("p") and estilo_de(fim.getnext()) == "TableNote":
            fim = fim.getnext()
        ini.addprevious(par_secao(False))
        fim.addnext(par_secao(True))
        n += 1
    corpo.append(sect(False, tipo_proxima=False))
    ultimo = corpo.findall(w("sectPr"))
    for s in ultimo[:-1]:                    # sectPr de pandoc (so footnotePr) no fim do corpo: sai
        corpo.remove(s)
    return n


def cabecalho_xml() -> bytes:
    nsmap = {"w": W, "r": R}
    h = etree.Element(w("hdr"), nsmap=nsmap)
    p = sub(h, "p")
    ppr = sub(p, "pPr")
    sub(ppr, "pStyle", val="Cabecalho")
    sub(ppr, "jc", val="right")
    for fase, valor in (("begin", None), (None, " PAGE "), ("separate", None), ("txt", "1"), ("end", None)):
        r = sub(p, "r")
        rpr = sub(r, "rPr")
        rpr.append(rfonts())
        sub(rpr, "sz", val=CFG["pt"] * 2)
        sub(rpr, "szCs", val=CFG["pt"] * 2)
        if fase == "txt":
            sub(r, "t").text = valor
        elif fase is None:
            it = sub(r, "instrText")
            it.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            it.text = valor
        else:
            sub(r, "fldChar", fldCharType=fase)
    return etree.tostring(h, xml_declaration=True, encoding="UTF-8", standalone=True)


# --------------------------------------------------------------------------- #
# 8. pacote                                                                    #
# --------------------------------------------------------------------------- #
def numeracao(raiz: etree._Element) -> None:
    """Marcadores em Times: o pandoc usa Symbol, Courier New e Wingdings."""
    for lvl in raiz.iter(w("lvl")):
        fmt = lvl.find(w("numFmt")).get(w("val"))
        if fmt == "bullet":
            lvl.find(w("lvlText")).set(w("val"), "•")
        # o Word exporta a tabulacao depois do marcador ("1." ou "•") como espaco em ARIAL no PDF (medido:
        # pdffonts lista ArialMT so por isso). Sem sufixo e com 3 espacos duros a lista segue alinhada e so ha Times.
        lt = lvl.find(w("lvlText"))
        if not lt.get(w("val")).endswith("\u00a0"):
            lt.set(w("val"), lt.get(w("val")) + "\u00a0\u00a0\u00a0")
        if lvl.find(w("suff")) is None:
            lt.addprevious(mk("suff", val="nothing"))
        for old in lvl.findall(w("rPr")):
            lvl.remove(old)
        rpr = sub(lvl, "rPr")
        rpr.append(rfonts())
        rpr.find(w("rFonts")).set(w("hint"), "default")
        sub(rpr, "sz", val=CFG["pt"] * 2)
        ilvl = int(lvl.get(w("ilvl")))
        ind = lvl.find(f"{w('pPr')}/{w('ind')}")
        ind.set(w("left"), str(CFG["recuo_twips"] * (ilvl + 1)))
        ind.set(w("hanging"), "360")
    for rf in raiz.iter(w("rFonts")):
        for a in list(rf.attrib):
            if a.split("}")[1] in THEME_ATTRS:
                del rf.attrib[a]


def numids_continuacao(nm: etree._Element) -> set[str]:
    """numId das listas "em branco" do pandoc (marcador " "): servem so de recuo para o 2o bloco de um item de lista
    (bloco de codigo, paragrafo seguinte). O original da casa as transformava em bullet "•"; aqui viram recuo."""
    em_branco = {a.get(w("abstractNumId")) for a in nm.findall(w("abstractNum"))
                 if (a.find(f"{w('lvl')}/{w('lvlText')}") is not None
                     and a.find(f"{w('lvl')}/{w('lvlText')}").get(w("val")) == " ")}
    return {n.get(w("numId")) for n in nm.findall(w("num")) if n.find(w("abstractNumId")).get(w("val")) in em_branco}


def listas_em_texto(corpo: etree._Element, nm: etree._Element) -> int:
    """Listas depois de "References" (nos apendices) com o marcador escrito no texto, sem numeracao do Word.

    O validador da casa (validate_canon.py) le tudo o que vem depois de "References" como zona da lista de
    referencias e exige ali nenhuma numeracao automatica; o marcador ("•" ou "1.") vira texto com o mesmo recuo
    deslocado do estilo Lista, e a aparencia nao muda.
    """
    abstrato = {n.get(w("numId")): n.find(w("abstractNumId")).get(w("val")) for n in nm.findall(w("num"))}
    formato = {(a.get(w("abstractNumId")), lv.get(w("ilvl"))): lv.find(w("numFmt")).get(w("val"))
               for a in nm.findall(w("abstractNum")) for lv in a.findall(w("lvl"))}
    depois, conta, n = False, {}, 0
    for p in corpo.iter(w("p")):
        if estilo_de(p) == "Heading1" and texto_de(p).strip().startswith(LB["refs"]):
            depois = True
        npr = p.find(f"{w('pPr')}/{w('numPr')}")
        if not depois or npr is None:
            continue
        nid, ilvl = npr.find(w("numId")).get(w("val")), npr.find(w("ilvl")).get(w("val"))
        conta[(nid, ilvl)] = conta.get((nid, ilvl), 0) + 1
        fmt = formato.get((abstrato.get(nid), ilvl), "bullet")
        marca = "•" if fmt == "bullet" else f"{conta[(nid, ilvl)]}."
        npr.getparent().remove(npr)
        ind = get_or_add(pxml(p), "ind")
        ind.set(w("left"), str(CFG["recuo_twips"] * (int(ilvl) + 1)))
        ind.set(w("hanging"), "360")
        r = mk("r")
        rpr = sub(r, "rPr")
        rpr.append(rfonts())
        sub(r, "t").text = marca
        sub(r, "tab")        # tabulacao num run em Times: o texto para no recuo deslocado e as linhas seguintes alinham
        pxml(p).addnext(r)
        ordenar(pxml(p), ORD_PPR)
        n += 1
    return n


def escrever_pacote(raw: Path, out: Path, titulo: str, autor: str, fig_cm: float, rel: dict,
                    forcar_paisagem: str = "") -> dict:
    with zipfile.ZipFile(raw) as z:
        partes = {n: z.read(n) for n in z.namelist()}
    parse = etree.fromstring
    doc = parse(partes["word/document.xml"])
    rels = parse(partes["word/_rels/document.xml.rels"])
    media = {r.get("Id"): Path("word") / r.get("Target") for r in rels if r.get("Type", "").endswith("/image")}
    # imagens: bytes do pacote -> arquivo temporario para medir
    tmp = out.parent / "_media"
    tmp.mkdir(exist_ok=True)
    midia_local = {}
    for rid, caminho in media.items():
        destino = tmp / Path(str(caminho)).name
        destino.write_bytes(partes[str(caminho).replace("\\", "/")])
        midia_local[rid] = destino

    rel["blank_numids"] = numids_continuacao(parse(partes["word/numbering.xml"]))
    inf = formatar_corpo(doc, midia_local, fig_cm, rel)
    inf["listas_texto"] = listas_em_texto(doc.find(w("body")), parse(partes["word/numbering.xml"]))
    # tabelas forcadas para paisagem (teste do caminho): reformatar
    if forcar_paisagem:
        for k, i in enumerate(inf["tabelas"]):
            rot = ""
            prev = i["tbl"].getprevious()
            while prev is not None and prev.tag == w("p") and estilo_de(prev) in ("CaptionText", "CaptionLabel"):
                if estilo_de(prev) == "CaptionLabel":
                    rot = texto_de(prev)
                prev = prev.getprevious()
            if rot == forcar_paisagem:
                inf["tabelas"][k] = formatar_tabela(i["tbl"], forcar_paisagem=True)
    corpo = doc.find(w("body"))
    inf["secoes_paisagem"] = aplicar_secoes(corpo, inf["tabelas"])
    primeira = next(corpo.iter(w("sectPr")))          # capa sem numero de pagina (canon: titlePg)
    sub(primeira, "titlePg")
    ordenar(primeira, ORD_SECT)
    for p in corpo.iter(w("p")):
        ordenar(pxml(p), ORD_PPR) if p.find(w("pPr")) is not None else None
    partes["word/document.xml"] = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)

    st = parse(partes["word/styles.xml"])
    sanear_estilos(st)
    partes["word/styles.xml"] = etree.tostring(st, xml_declaration=True, encoding="UTF-8", standalone=True)

    nm = parse(partes["word/numbering.xml"])
    numeracao(nm)
    partes["word/numbering.xml"] = etree.tostring(nm, xml_declaration=True, encoding="UTF-8", standalone=True)

    for nome in ("word/footnotes.xml", "word/comments.xml", "word/fontTable.xml"):
        if nome in partes:
            x = parse(partes[nome])
            for rf in x.iter(w("rFonts")):
                for a in list(rf.attrib):
                    if a.split("}")[1] in THEME_ATTRS:
                        del rf.attrib[a]
            partes[nome] = etree.tostring(x, xml_declaration=True, encoding="UTF-8", standalone=True)

    # configuracao: modo de compatibilidade moderno e idioma de revisao
    se = parse(partes["word/settings.xml"])
    for t in se.findall(w("themeFontLang")):
        t.set(w("val"), LB["code"])
    if se.find(w("compat")) is None:
        c = mk("compat")
        sub(c, "compatSetting", name="compatibilityMode", uri="http://schemas.microsoft.com/office/word", val=15)
        se.insert(len(se) - 4 if len(se) > 4 else len(se), c)
    partes["word/settings.xml"] = etree.tostring(se, xml_declaration=True, encoding="UTF-8", standalone=True)

    # cabecalho com numero de pagina
    partes["word/header-v04.xml"] = cabecalho_xml()
    rel_el = etree.SubElement(rels, f"{{{REL}}}Relationship")
    rel_el.set("Id", "rIdCabV04")
    rel_el.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header")
    rel_el.set("Target", "header-v04.xml")
    partes["word/_rels/document.xml.rels"] = etree.tostring(rels, xml_declaration=True, encoding="UTF-8",
                                                           standalone=True)
    ct = parse(partes["[Content_Types].xml"])
    ov = etree.SubElement(ct, f"{{{CT}}}Override")
    ov.set("PartName", "/word/header-v04.xml")
    ov.set("ContentType", "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml")
    partes["[Content_Types].xml"] = etree.tostring(ct, xml_declaration=True, encoding="UTF-8", standalone=True)

    # propriedades: titulo e autor (nada de caminho, nada de lastModifiedBy)
    core = parse(partes["docProps/core.xml"])
    DC = "http://purl.org/dc/elements/1.1/"
    for tag, val in ((f"{{{DC}}}title", titulo), (f"{{{DC}}}creator", autor)):
        el = core.find(tag)
        if el is None:
            el = etree.SubElement(core, tag)
        el.text = val
    partes["docProps/core.xml"] = etree.tostring(core, xml_declaration=True, encoding="UTF-8", standalone=True)

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        ordem = ["[Content_Types].xml"] + [n for n in partes if n != "[Content_Types].xml"]
        for n in ordem:
            z.writestr(n, partes[n])
    shutil.rmtree(tmp, ignore_errors=True)
    return inf


# --------------------------------------------------------------------------- #
# 9. orquestracao                                                              #
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=str(ROOT / "paper.md"))
    ap.add_argument("--work", required=True, help="pasta de trabalho (md de exportacao, copias leves das figuras)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fig-cm", default="auto", help="largura unica das figuras em cm, ou 'auto' (ver docstring)")
    ap.add_argument("--img-px", type=int, default=CFG["img_px"])
    ap.add_argument("--img-cores", type=int, default=CFG["img_cores"])
    ap.add_argument("--lang", default="en", choices=rotulos.IDIOMAS,
                    help="idioma da edicao: rotulos estruturais, idioma de revisao do Word e quebras de pagina")
    ap.add_argument("--forcar-paisagem", default="", help="ex.: 'Tabela 19' (teste do caminho paisagem)")
    a = ap.parse_args(argv)
    definir_idioma(a.lang)
    src, work, out = Path(a.src).resolve(), Path(a.work).resolve(), Path(a.out).resolve()
    work.mkdir(parents=True, exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)

    md, ctx = preparar_md(src, work, a.fig_cm)
    rel = ctx["rel"]
    copiar_figuras(rel["figuras"], work, a.img_px, a.img_cores)
    fig_cm, folga = largura_figuras(rel["figuras"], a.fig_cm)
    export_md = work / "export-v04.md"
    export_md.write_text(md, encoding="utf-8")

    raw = work / "raw-pandoc.docx"
    subprocess.run(["pandoc", str(export_md), "-f", "markdown-tex_math_dollars-implicit_figures",
                    "--shift-heading-level-by=-1", "--syntax-highlighting=none", "-M", f"lang={LB['code']}",
                    f"--resource-path={work}",
                    "-o", str(raw)], check=True)
    inf = escrever_pacote(raw, out, ctx["titulo"], ctx["meta"].get("author", ""), fig_cm, rel, a.forcar_paisagem)

    meta_json = {"fig_largura_cm": fig_cm, "fig_teto_cm": CFG["fig_largura_cm"],
                 "fig_max_por_figura": folga, "img_px": a.img_px,
                 "sem_nota": rel["sem_nota"], "quebras_manuais_descartadas": rel["quebras_manuais"],
                 "legendas_divididas": rel["legendas_divididas"], "blocos_codigo": inf["blocos_codigo"],
                 "figuras_codigo": rel["figuras_codigo"], "espaco_sem_nota": inf["espaco_sem_nota"],
                 "tabelas": [{k: v for k, v in t.items() if k != "tbl"} for t in inf["tabelas"]],
                 "secoes_paisagem": inf["secoes_paisagem"], "listas": inf["listas"], "figuras": inf["figuras"]}
    out.with_suffix(".meta.json").write_text(json.dumps(meta_json, ensure_ascii=False, indent=1), encoding="utf-8")
    pior = sorted(folga, key=lambda t: t["max_cm"])[:5]
    print(f"[OK] {out}")
    print(f"     figuras: {inf['figuras']} a {fig_cm} cm (teto {CFG['fig_largura_cm']}); maior largura que cabe: "
          + ", ".join(f"Fig {t['num']} (razao {t['aspecto']}) {t['max_cm']} cm" for t in pior))
    print(f"     tabelas: {len(inf['tabelas'])} (pt: " + "/".join(str(t['pt']) for t in inf['tabelas']) +
          f"); secoes paisagem: {inf['secoes_paisagem']}; listas (itens): {inf['listas']}; codigo inline: {inf['codigo']}")
    print(f"     blocos de codigo ({MONO}): " + "; ".join(
        f"{b['linhas']} linhas x {b['colunas']} col a {b['pt']} pt ({b['largura_pt']} pt de {b['util_pt']:.0f}{'' if b['cabe'] else ' NAO CABE'})"
        for b in inf["blocos_codigo"]) + f"; figuras de codigo: {rel['figuras_codigo']}")
    print(f"     sem Nota (nada injetado): {', '.join(rel['sem_nota']) or 'nenhum'}; legendas divididas titulo+Nota: "
          f"{rel['legendas_divididas']}; paragrafos com espaco extra apos elemento sem Nota: {inf['espaco_sem_nota']}")
    for t in inf["tabelas"]:
        if t["aviso"]:
            print(f"     AVISO tabela: {t['aviso']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
