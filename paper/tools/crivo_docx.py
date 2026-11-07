#!/usr/bin/env python3
"""Crivo de aceite do DOCX/PDF (fork ASP do crivo_docx.py do repo lgbt-indicador-violencia, rotulos em ingles).

Falha e LISTA cada violacao. Nada e "validado" sem ele. Diferencas para o original: Table/Figure/References/Appendix;
bloco de codigo (estilo CodeBlock, Courier New 8 a 10 pt) e permitido; Nota/Fonte abaixo de tabela e figura e opcional
(a norma diz "quando houver": o exportador nao injeta mais "Fonte"), e a ausencia vira [info], nao violacao.

    python3 tools/crivo_docx.py paper-v04.docx [--pdf paper-v04.pdf] [--render pasta] [--fig-cm 14]

Saida: exit 0 = limpo; 1 = violacao de FORMA (pipeline a corrigir); 2 = so pendencia de CONTEUDO (texto do
paper.md, frente P3). Cada violacao imprime `[FORMA|CONTEUDO] codigo: mensagem`.

Fase DOCX (stdlib + lxml):
  F01 run sem Times New Roman (efetivo), F02 tema de fonte (asciiTheme/hAnsiTheme/cstheme/eastAsiaTheme) em
  qualquer parte, F03 tamanho != 12 pt fora de tabela (tabela: de 8 a 10 pt), F04 shd/fill em tabela,
  F05 estilos Compact/SourceCode/VerbatimChar usados, F06 figura com largura != constante (ou mais alta que a
  pagina), F07 titulo nivel 1 / apendice / anexo sem quebra de pagina antes, F08 bullet dentro do Resumo/
  Abstract, F09 '/Users/' no zip, F10 pagina/margens, F11 alinhamento justificado, F12 lista: um estilo so e
  marcadores em Times, F13 tabela: filete so horizontal, cabecalho repetido, cantSplit, titulo acima e Nota/
  Fonte abaixo, F14 figura: rotulo + titulo acima e Nota/Fonte abaixo, F15 referencias: recuo deslocado e sem
  etiqueta estranha, F16 cabecalho com numero de pagina.
  C07 tabela sem rotulo/titulo no paper.md,
  C01 placeholder [REPO_URL]/[SHA-...], C02 a palavra 'Destaque', C03 'Nivel da fonte' ou '[nivel:' nas
  referencias, C04 'PDF de anexos'/'artigo principal' (o artigo agora e um PDF so), C05 'Fonte: Elaboração
  do autor.' injetada pelo exportador (atribuir a fonte real), C06 bullet em Resumo/Abstract.
Fase PDF (poppler + PyMuPDF): P01 pdffonts so TimesNewRoman, P02 <= 4 MB, P03 tabela com 1 linha de dados no
fim/comeco de pagina, P04 figura fora da area util ou separada do rotulo, P05 pagina em branco, e a lista de
paginas a renderizar com `pdftoppm -r 100` (primeiras 10, tabelas, apendices/anexos, figuras).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_house as X  # noqa: E402  (mesmas constantes que o exportador)

W, WP, A = X.W, X.WP, X.A
w = X.w
ESCONDIDOS = ("Compact", "SourceCode", "VerbatimChar")
TETO_BYTES = 4 * 1024 * 1024
V: list[tuple[str, str, str]] = []
INFO: list[str] = []


def v(cat: str, cod: str, msg: str) -> None:
    V.append((cat, cod, msg))


def limpa(t: str) -> str:
    return t.replace(X.ZWSP, "")


def texto(el: etree._Element) -> str:
    return limpa("".join(t.text or "" for t in el.iter(w("t"))))


# --------------------------------------------------------------------------- #
# estilos: resolucao efetiva                                                   #
# --------------------------------------------------------------------------- #
class Estilos:
    def __init__(self, raiz: etree._Element) -> None:
        self.por_id = {s.get(w("styleId")): s for s in raiz.findall(w("style"))}
        dd = raiz.find(f"{w('docDefaults')}/{w('rPrDefault')}/{w('rPr')}")
        self.padrao = dd

    def cadeia(self, sid: str | None) -> list[etree._Element]:
        out, vistos = [], set()
        while sid and sid in self.por_id and sid not in vistos:
            vistos.add(sid)
            st = self.por_id[sid]
            out.append(st)
            b = st.find(w("basedOn"))
            sid = b.get(w("val")) if b is not None else None
        return out

    def _procura_rpr(self, sids: list[str | None], tag: str, attr: str) -> str | None:
        for sid in sids:
            for st in self.cadeia(sid):
                e = st.find(f"{w('rPr')}/{w(tag)}")
                if e is not None and e.get(w(attr)) is not None:
                    return e.get(w(attr))
        if self.padrao is not None:
            e = self.padrao.find(w(tag))
            if e is not None:
                return e.get(w(attr))
        return None

    def fonte(self, r: etree._Element, pstyle: str | None) -> str | None:
        rf = r.find(f"{w('rPr')}/{w('rFonts')}")
        if rf is not None and rf.get(w("ascii")):
            return rf.get(w("ascii"))
        rs = r.find(f"{w('rPr')}/{w('rStyle')}")
        return self._procura_rpr([rs.get(w("val")) if rs is not None else None, pstyle], "rFonts", "ascii")

    def tamanho(self, r: etree._Element, pstyle: str | None) -> float | None:
        sz = r.find(f"{w('rPr')}/{w('sz')}")
        val = sz.get(w("val")) if sz is not None else None
        if val is None:
            rs = r.find(f"{w('rPr')}/{w('rStyle')}")
            val = self._procura_rpr([rs.get(w("val")) if rs is not None else None, pstyle], "sz", "val")
        return int(val) / 2 if val else None

    def ppr_bool(self, p: etree._Element, tag: str) -> bool:
        e = p.find(f"{w('pPr')}/{w(tag)}")
        if e is not None:
            return e.get(w("val")) not in ("0", "false")
        ps = p.find(f"{w('pPr')}/{w('pStyle')}")
        for st in self.cadeia(ps.get(w("val")) if ps is not None else "Normal"):
            e = st.find(f"{w('pPr')}/{w(tag)}")
            if e is not None:
                return e.get(w("val")) not in ("0", "false")
        return False


def sid_de(p: etree._Element) -> str:
    ps = p.find(f"{w('pPr')}/{w('pStyle')}")
    return ps.get(w("val")) if ps is not None else "Normal"


# --------------------------------------------------------------------------- #
# fase DOCX                                                                    #
# --------------------------------------------------------------------------- #
def crivo_docx(docx: Path, fig_cm: float) -> dict:
    z = zipfile.ZipFile(docx)
    partes = {n: z.read(n) for n in z.namelist()}
    doc = etree.fromstring(partes["word/document.xml"])
    est = Estilos(etree.fromstring(partes["word/styles.xml"]))
    corpo = doc.find(w("body"))
    ctx = {"tabelas": [], "figuras": [], "titulos": []}

    # F09: caminho de usuario em qualquer membro (texto ou binario)
    for n, b in partes.items():
        if b"/Users/" in b:
            v("FORMA", "F09", f"'/Users/' em {n}")

    # F02: tema de fonte em qualquer parte XML
    pad = re.compile(rb'w:(?:ascii|hAnsi|eastAsia)Theme=|w:cstheme=')
    for n, b in partes.items():
        if n.endswith(".xml") and n.startswith("word/") and "theme/" not in n:
            k = len(pad.findall(b))
            if k:
                v("FORMA", "F02", f"{k} atributo(s) de tema de fonte em {n}")

    # F01/F03: fonte e tamanho efetivos de cada run
    sem_times, sem_12, fora_tab = {}, {}, {}
    for r in corpo.iter(w("r")):
        p = next((a for a in r.iterancestors() if a.tag == w("p")), None)
        if p is None or (not r.findall(w("t")) and r.find(f".//{w('drawing')}") is None):
            continue
        ps = sid_de(p)
        em_tab = any(a.tag == w("tc") for a in r.iterancestors())
        f = est.fonte(r, ps)
        codigo = ps == "CodeBlock"
        if f != X.TNR and not (codigo and f == X.MONO):
            sem_times[f] = sem_times.get(f, 0) + 1
        t = est.tamanho(r, ps)
        if codigo:
            if t is None or not (X.CODE_PT_MIN <= t <= X.CODE_PT_MAX):
                sem_12[t] = sem_12.get(t, 0) + 1
            continue
        if em_tab:
            if t is None or not (X.CFG["pt_tabela_min"] <= t <= X.CFG["pt_tabela"]):
                fora_tab[t] = fora_tab.get(t, 0) + 1
        elif t != X.CFG["pt"] and not ps.startswith("Cover"):   # capa da casa: titulo 14 pt, ORCID 11 pt
            if r.find(f".//{w('drawing')}") is None:
                sem_12[t] = sem_12.get(t, 0) + 1
    for f, k in sem_times.items():
        v("FORMA", "F01", f"{k} run(s) com fonte efetiva {f!r} (esperado Times New Roman)")
    for t, k in sem_12.items():
        v("FORMA", "F03", f"{k} run(s) fora de tabela com {t} pt (esperado {X.CFG['pt']})")
    for t, k in fora_tab.items():
        v("FORMA", "F03", f"{k} run(s) em tabela com {t} pt (esperado {X.CFG['pt_tabela_min']} a {X.CFG['pt_tabela']})")

    # F04: preenchimento em tabela (corpo e estilo de tabela usado)
    for i, tbl in enumerate(corpo.iter(w("tbl")), 1):
        for s in tbl.iter(w("shd")):
            v("FORMA", "F04", f"tabela {i}: shd/fill ({s.get(w('fill'))}) em {etree.QName(s.getparent()).localname}")
            break
        sid = tbl.find(f"{w('tblPr')}/{w('tblStyle')}")
        for st in est.cadeia(sid.get(w("val")) if sid is not None else None):
            if st.find(f".//{w('shd')}") is not None:
                v("FORMA", "F04", f"tabela {i}: o estilo {st.get(w('styleId'))!r} tem shd")
    # F05: estilos proibidos usados
    uso = re.findall(rb'w:(?:pStyle|rStyle) w:val="(SourceCode|VerbatimChar)"', b"".join(
        b for n, b in partes.items() if n.startswith("word/") and n.endswith(".xml")))
    for nome in sorted(set(uso)):
        v("FORMA", "F05", f"estilo {nome.decode()} usado {uso.count(nome)} vez(es)")
    # F11: corpo justificado (norma Codex Hash §2; o APA puro alinha a esquerda)
    normal = re.search(rb'<w:style [^>]*w:styleId="Normal".*?</w:style>', partes["word/styles.xml"], re.S)
    if not normal or b'<w:jc w:val="both"/>' not in normal.group(0):
        v("FORMA", "F11", "estilo Normal sem alinhamento justificado (norma Codex Hash)")

    # F10: pagina e margens
    carta = {(12240, 15840), (15840, 12240)}
    for s in corpo.iter(w("sectPr")):
        pg, pm = s.find(w("pgSz")), s.find(w("pgMar"))
        dims = (int(pg.get(w("w"))), int(pg.get(w("h"))))
        if dims not in carta:
            v("FORMA", "F10", f"papel {dims} nao e Carta")
        for lado in ("top", "bottom", "left", "right"):
            if int(pm.get(w(lado))) != X.CFG["margem_twips"]:
                v("FORMA", "F10", f"margem {lado} = {pm.get(w(lado))} twips (esperado {X.CFG['margem_twips']})")
        if s.find(w("headerReference")) is None:
            v("FORMA", "F16", "secao sem cabecalho (numero de pagina)")
    hdr = partes.get("word/header-v04.xml", b"")
    if b"PAGE" not in hdr or b'w:val="right"' not in hdr:
        v("FORMA", "F16", "cabecalho sem campo PAGE alinhado a direita")

    # percorre o corpo em ordem
    filhos = list(corpo)
    atual_h1 = ""
    em_refs = False
    for idx, el in enumerate(filhos):
        if el.tag == w("p"):
            sid = sid_de(el)
            t = texto(el).strip()
            if sid == "Heading1":
                atual_h1 = t
                em_refs = t.startswith("References")
                quebra = est.ppr_bool(el, "pageBreakBefore") or el.find(f".//{w('br')}[@{w('type')}='page']") is not None
                if (X.quebra_direta(t) or re.match(r"^Appendix [A-Z] —", t)) and not quebra:
                    v("FORMA", "F07", f"titulo sem quebra de pagina antes: {t[:50]!r}")
                ctx["titulos"].append(t)
            elif re.match(r"^Appendix [A-Z] —", t):
                v("FORMA", "F07", f"apendice fora de Heading1: {t[:50]!r}")
            if sid == "Lista" or el.find(f"{w('pPr')}/{w('numPr')}") is not None:
                if sid != "Lista":
                    v("FORMA", "F12", f"item de lista com estilo {sid!r} (esperado Lista): {t[:40]!r}")
                if atual_h1 in ("Resumo", "Abstract"):
                    v("CONTEUDO", "C06", f"bullet dentro de {atual_h1}: {t[:60]!r}")
            if em_refs and sid not in ("Heading1",):
                if sid != "Bibliography":
                    v("FORMA", "F15", f"paragrafo da lista de referencias com estilo {sid!r}: {t[:50]!r}")
            if el.find(f".//{w('drawing')}") is not None and el.find(f".//{{{WP}}}docPr").get("descr") != X.LOGO_ALT:
                ctx["figuras"].append(el)
        elif el.tag == w("tbl"):
            ctx["tabelas"].append((idx, el))

    # F06/F14: figuras
    emu = round(fig_cm * X.EMU_CM)
    util_h = (X.CFG["pagina_twips"][1] - 2 * X.CFG["margem_twips"]) / 20 * 12700
    larguras = set()
    for p in ctx["figuras"]:
        ext = p.find(f".//{{{WP}}}extent")
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        larguras.add(cx)
        idx = filhos.index(p)
        rot = texto(filhos[idx - 2]) if idx >= 2 else ""
        if abs(cx - emu) > 2:
            v("FORMA", "F06", f"{rot or 'figura'}: largura {cx / X.EMU_CM:.2f} cm != constante {fig_cm:.2f} cm")
        if cy > util_h:
            v("FORMA", "F06", f"{rot}: altura {cy / X.EMU_CM:.1f} cm passa da pagina util")
        if not (idx >= 2 and sid_de(filhos[idx - 2]) == "CaptionLabel" and sid_de(filhos[idx - 1]) == "CaptionText"):
            v("FORMA", "F14", f"{rot or 'figura'}: sem rotulo e titulo acima")
        nxt = filhos[idx + 1] if idx + 1 < len(filhos) else None
        if nxt is None or sid_de(nxt) != "TableNote":
            INFO.append(f"{rot or 'figura'}: sem Nota abaixo (a norma diz 'quando houver'; nada injetado)")
        alt = p.find(f".//{{{WP}}}docPr").get("descr", "")
        if "/" in alt or not alt:
            v("FORMA", "F09", f"{rot}: alt-text vazio ou com caminho: {alt!r}")
    if len(larguras) > 1:
        v("FORMA", "F06", f"figuras com {len(larguras)} larguras distintas")

    # F13: tabelas
    for idx, tbl in ctx["tabelas"]:
        nome = f"tabela #{ctx['tabelas'].index((idx, tbl)) + 1}"
        rots = []
        j = idx - 1
        while j >= 0 and filhos[j].tag == w("p") and sid_de(filhos[j]) in ("CaptionText", "CaptionLabel"):
            rots.append(texto(filhos[j]))
            j -= 1
        cab = limpa(texto(tbl.find(w("tr")))).strip()
        nome = rots[-1] if rots else nome
        if not rots:
            # tabela sem numero e titulo no paper.md: o numero e o titulo sao texto do autor, nao do pipeline
            v("CONTEUDO", "C07", f"tabela sem rotulo e titulo no Markdown (precisa de `**Table N.** titulo`): {cab[:40]!r}")
        else:
            nxt = filhos[idx + 1] if idx + 1 < len(filhos) else None
            if nxt is None or sid_de(nxt) != "TableNote":
                INFO.append(f"{nome}: sem Nota abaixo (a norma diz 'quando houver'; nada injetado)")
        b = tbl.find(f"{w('tblPr')}/{w('tblBorders')}")
        lados = {etree.QName(c).localname for c in b} if b is not None else set()
        if lados != {"top", "bottom"}:
            v("FORMA", "F13", f"{nome}: bordas {sorted(lados)} (esperado so top e bottom)")
        trs = tbl.findall(w("tr"))
        if trs[0].find(f"{w('trPr')}/{w('tblHeader')}") is None:
            v("FORMA", "F13", f"{nome}: cabecalho nao se repete")
        if any(tr.find(f"{w('trPr')}/{w('cantSplit')}") is None for tr in trs):
            v("FORMA", "F13", f"{nome}: linha sem cantSplit")
        if trs[0].find(f".//{w('tcBorders')}/{w('bottom')}") is None:
            v("FORMA", "F13", f"{nome}: sem filete sob o cabecalho")
        k = len(trs) - 1
        if k >= 2:
            chave = [any(p.find(f"{w('pPr')}/{w('keepNext')}") is not None for p in tr.iter(w("p"))) for tr in trs]
            if not (chave[0] and chave[1]):
                v("FORMA", "F13", f"{nome}: cabecalho/1a linha sem keepNext (risco de linha orfa no comeco)")
            if k >= 2 and not chave[-2]:
                v("FORMA", "F13", f"{nome}: penultima linha sem keepNext (risco de linha orfa no fim)")

    # F12: listas e marcadores em Times
    num = partes["word/numbering.xml"].decode("utf-8")
    for fonte in set(re.findall(r'w:ascii="([^"]+)"', num)):
        if fonte != X.TNR:
            v("FORMA", "F12", f"marcador de lista em {fonte!r} (esperado Times New Roman)")

    # F07 (anexos nao-H1) ja coberto; C01/C02/C04: texto
    alvo = [(texto(p), p) for p in corpo.iter(w("p"))]
    for t, p in alvo:
        for m in re.finditer(r"\[(?:REPO_URL|SHA[-\w…\.]*|[A-Z]{2,}(?:_[A-Z0-9]+)+|TODO|TBD|XXX+|\.\.\.|…|a (?:atualizar|criar|definir))\]", t):
            v("CONTEUDO", "C01", f"placeholder {m.group(0)} em: {t[:70]!r}")
    meta = docx.with_suffix(".meta.json")
    if meta.exists():
        m = json.loads(meta.read_text())
        if m.get("sem_nota"):
            INFO.append("sem Nota no Markdown (nada injetado): " + ", ".join(m["sem_nota"]))
        for b in m.get("blocos_codigo", []):
            INFO.append(f"bloco de codigo {X.MONO}: {b['linhas']} linhas x {b['colunas']} col a {b['pt']} pt, "
                        f"{b['largura_pt']} pt de {b.get('util_pt', 468):.0f}{'' if b['cabe'] else ' (NAO CABE: linha quebra)'}")
            if not b["cabe"]:
                v("FORMA", "F03", f"bloco de codigo com linha de {b['colunas']} colunas nao cabe a {X.CODE_PT_MIN} pt")
        INFO.append(f"figuras a {m['fig_largura_cm']} cm (teto da constante: {m['fig_teto_cm']} cm); tabelas: "
                    f"{len(m['tabelas'])}; secoes paisagem: {m['secoes_paisagem']}")
        if m["fig_largura_cm"] < m["fig_teto_cm"]:
            tabela = sorted(m["fig_max_por_figura"], key=lambda t: t["max_cm"])[:5]
            INFO.append(f"largura unica ({m['fig_largura_cm']} cm) menor que o teto ({m['fig_teto_cm']} cm): a figura "
                        "mais alta nao cabe numa pagina com legenda; maior largura que cabe: " +
                        ", ".join(f"Fig {t['num']} {t['max_cm']} cm" for t in tabela))
    return ctx


# --------------------------------------------------------------------------- #
# fase PDF                                                                     #
# --------------------------------------------------------------------------- #
def crivo_pdf(pdf: Path, docx_ctx: dict, render: Path | None) -> None:
    tam = pdf.stat().st_size
    if tam > TETO_BYTES:
        v("FORMA", "P02", f"PDF com {tam} bytes (> 4 MB)")
    fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    nomes = [ln.split()[0] for ln in fonts if ln.strip()]
    mono = X.MONO.replace(" ", "")
    ruins = [n for n in nomes if "TimesNewRoman" not in n and mono not in n]
    for n in ruins:
        v("FORMA", "P01", f"pdffonts: fonte {n} (so Times New Roman e permitido)")
    INFO.append(f"pdffonts: {len(nomes)} faces ({', '.join(sorted(set(nomes)))}); PDF {tam} bytes")
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("NAO EXERCIDO: P03/P04/P05 (PyMuPDF ausente; rode com /usr/bin/python3)")
        return
    d = fitz.open(str(pdf))
    INFO.append(f"PDF: {len(d)} paginas")
    paginas_render = set(range(1, min(len(d), 10) + 1))
    # tabelas: linhas horizontais (filetes) por pagina
    for n, pg in enumerate(d, 1):
        txt = pg.get_text("text").strip()
        if not txt and not pg.get_images():
            v("FORMA", "P05", f"pagina {n} em branco")
        if re.search(r"^(Table|Figure) [A-Z]?\d+\s*$", txt, re.M):
            paginas_render.add(n)
        if re.search(r"^Appendix [A-Z] —", txt, re.M):
            paginas_render.update({n, n + 1})
        # figura dentro da area util e com rotulo na mesma pagina
        mx = X.CFG["margem_twips"] / 20
        for im in pg.get_image_info():
            x0, y0, x1, y1 = im["bbox"]
            if x0 < mx - 2 or x1 > pg.rect.width - mx + 2 or y0 < mx - 2 or y1 > pg.rect.height - mx + 2:
                v("FORMA", "P04", f"pagina {n}: figura fora da area util ({[round(c) for c in im['bbox']]})")
            if n > 1 and not re.search(r"^Figure [A-Z]?\d+\s*$", txt, re.M):   # p. 1 = logo da capa
                v("FORMA", "P04", f"pagina {n}: figura sem rotulo 'Figure N' na mesma pagina")
            paginas_render.add(n)
    # orfas: para cada tabela com rotulo, em que pagina cai a 1a celula de cada linha de dados
    # (a busca comeca na pagina do rotulo "Tabela N", que e ancora unica; texto normalizado)
    paginas_texto = [re.sub(r"\s+", " ", pg.get_text("text")) for pg in d]
    ancora: dict[str, int] = {}
    for n, pg in enumerate(d):
        for m in re.finditer(r"^(Table [A-Z]?\d+)\s*$", pg.get_text("text"), re.M):
            ancora.setdefault(m.group(1), n)
    nao_verif, verificadas = [], 0
    for idx, tbl in docx_ctx["tabelas"]:
        trs = tbl.findall(w("tr"))
        rot = ""
        prev = tbl.getprevious()
        while prev is not None and prev.tag == w("p") and sid_de(prev) in ("CaptionText", "CaptionLabel"):
            if sid_de(prev) == "CaptionLabel":
                rot = texto(prev).strip()
            prev = prev.getprevious()
        if rot not in ancora or len(trs) < 4:
            continue
        chaves = [re.sub(r"\s+", " ", limpa(texto(tr.find(w("tc"))))).strip()[:22] for tr in trs[1:]]
        p0, onde = ancora[rot], []
        for chave in chaves:
            # chave so de digitos ("24") casa como numero inteiro: "2024" na pagina anterior dava falsa linha orfa
            casa = ((lambda t, c=chave: re.search(rf"(?<![\d,.]){c}(?![\d,.])", t) is not None) if chave.isdigit()
                    else (lambda t, c=chave: c in t))
            achou = next((n for n in range(p0, min(p0 + 8, len(d))) if chave and casa(paginas_texto[n])), None)
            onde.append(achou)
            if achou is not None:
                p0 = achou
        validas = [x for x in onde if x is not None]
        if len(validas) < 0.7 * len(chaves):
            nao_verif.append(rot)
            continue
        verificadas += 1
        por_pagina: dict[int, int] = {}
        for x in validas:
            por_pagina[x] = por_pagina.get(x, 0) + 1
        ordem = sorted(por_pagina)
        if len(ordem) > 1:
            for pgn in (ordem[0], ordem[-1]):
                if por_pagina[pgn] == 1:
                    v("FORMA", "P03", f"{rot}: apenas 1 linha de dados na pagina {pgn + 1} "
                      f"({'inicio' if pgn == ordem[0] else 'fim'} da tabela)")
            paginas_render.update(p + 1 for p in ordem)
        else:
            paginas_render.add(ordem[0] + 1)
    INFO.append(f"P03 (linha orfa): {verificadas} tabelas verificadas"
                + (f"; NAO verificaveis (celula inicial nao localizada): {', '.join(nao_verif)}" if nao_verif else ""))
    if render:
        render.mkdir(parents=True, exist_ok=True)
        lista = sorted(p for p in paginas_render if 1 <= p <= len(d))
        (render / "paginas-a-ler.txt").write_text(" ".join(map(str, lista)) + "\n")
        INFO.append("paginas a renderizar e LER (primeiras 10 + tabelas + figuras + apendices/anexos): "
                    + " ".join(map(str, lista)))
        INFO.append(f"renderizar TODAS: pdftoppm -r 100 -png {pdf} {render}/p")


def autoteste(docx: Path, fig_cm: float) -> int:
    """Controle negativo: estraga um DOCX bom de dez jeitos e exige que o crivo acuse cada um."""
    import tempfile
    z = zipfile.ZipFile(docx)
    base = {n: z.read(n) for n in z.namelist()}
    estragos = {
        "F01": ("word/document.xml", lambda b: b.replace(b'w:ascii="Times New Roman"', b'w:ascii="Calibri"', 3)),
        "F02": ("word/document.xml", lambda b: b.replace(b"<w:rFonts ", b'<w:rFonts w:asciiTheme="minorHAnsi" ', 1)),
        # F03 e F06 estragam o CORPO (depois de "Abstract"): a capa tem 14/11 pt e o logo a 5,2 cm de proposito
        "F03": ("word/document.xml", lambda b: b[:b.index(b"Abstract</w:t>")] + b[b.index(b"Abstract</w:t>"):].replace(
            b'<w:sz w:val="24"/>', b'<w:sz w:val="26"/>', 2)),
        "F04": ("word/document.xml", lambda b: b.replace(b"<w:tcPr>", b'<w:tcPr><w:shd w:val="clear" w:fill="E9EEF4"/>', 1)),
        "F05": ("word/document.xml", lambda b: b.replace(b'<w:pStyle w:val="Lista"/>', b'<w:pStyle w:val="SourceCode"/>', 1)),
        "F06": ("word/document.xml", lambda b: b[:b.index(b"Abstract</w:t>")] + re.sub(
            rb'(<wp:extent cx=")\d+"', rb'\g<1>3000000"', b[b.index(b"Abstract</w:t>"):], count=1)),
        "F07": ("word/document.xml", lambda b: b.replace(b"<w:pageBreakBefore/>", b"")),
        "F09": ("docProps/core.xml", lambda b: b.replace(b"</cp:coreProperties>", b"<dc:description xmlns:dc=\"http://purl.org/dc/elements/1.1/\">/Users/x/y</dc:description></cp:coreProperties>")),
        "F11": ("word/styles.xml", lambda b: b.replace(b'<w:jc w:val="both"/>', b'<w:jc w:val="left"/>')),
        "C01": ("word/document.xml", lambda b: re.sub(rb"(<w:t(?: [^>]*)?>)", rb"\1[REPO_URL] ", b, count=1)),
    }
    falhas = 0
    for cod, (parte, fn) in estragos.items():
        novo = dict(base)
        antes = novo[parte]
        novo[parte] = fn(antes)
        if novo[parte] == antes:
            print(f"  autoteste {cod}: NAO EXERCIDO (o estrago nao alterou o arquivo)")
            falhas += 1
            continue
        with tempfile.TemporaryDirectory() as td:
            alvo = Path(td) / "ruim.docx"
            with zipfile.ZipFile(alvo, "w", zipfile.ZIP_DEFLATED) as zo:
                for n, b in novo.items():
                    zo.writestr(n, b)
            V.clear()
            try:
                crivo_docx(alvo, fig_cm)
            except Exception as e:  # estrago que quebra o parser tambem conta como acusado
                v("FORMA", cod, f"excecao: {e}")
            achou = any(c == cod for _, c, _ in V)
        print(f"  autoteste {cod}: {'acusado' if achou else 'NAO ACUSADO  <-- crivo cego'}")
        falhas += 0 if achou else 1
    V.clear()
    return 1 if falhas else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--autoteste", action="store_true", help="controle negativo sobre o DOCX dado")
    ap.add_argument("docx")
    ap.add_argument("--pdf")
    ap.add_argument("--render", help="pasta onde gravar a lista de paginas a ler (e onde render sera feito)")
    ap.add_argument("--fig-cm", type=float, help="largura esperada das figuras (padrao: a gravada no .meta.json)")
    a = ap.parse_args()
    docx = Path(a.docx)
    meta = docx.with_suffix(".meta.json")
    fig_cm = a.fig_cm or (json.loads(meta.read_text())["fig_largura_cm"] if meta.exists() else X.CFG["fig_largura_cm"])
    if a.autoteste:
        return autoteste(docx, fig_cm)
    ctx = crivo_docx(docx, fig_cm)
    if a.pdf:
        crivo_pdf(Path(a.pdf), ctx, Path(a.render) if a.render else None)
    forma = [x for x in V if x[0] == "FORMA"]
    cont = [x for x in V if x[0] == "CONTEUDO"]
    vistos = set()
    for cat, cod, msg in V:
        if (cod, msg) not in vistos:
            vistos.add((cod, msg))
            print(f"[{cat}] {cod}: {msg}")
    for i in INFO:
        print(f"[info] {i}")
    print(f"== crivo: {len(forma)} violacao(oes) de FORMA, {len(cont)} pendencia(s) de CONTEUDO")
    return 1 if forma else (2 if cont else 0)


if __name__ == "__main__":
    sys.exit(main())
