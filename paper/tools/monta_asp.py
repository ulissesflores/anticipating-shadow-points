#!/usr/bin/env python3
"""Derive the build source of one ASP paper from its canonical Markdown (the canonical file is never touched).

The exporter (export_house.py) wants YAML front matter and a body without the hand-written header block. This
script only changes STRUCTURE, never the scientific text. Every change is counted and printed so the caller can
declare it:

  1. header block (title, author/contact lines, Version/DOI/Status/License/Replication/Companion lines) -> YAML
     front matter (title/subtitle/author/affiliation/orcid/date) for the cover; the Version/DOI/Status/License/
     Replication/Companion lines are KEPT and moved, as plain paragraphs, to the end of the Abstract block
     (just before "## Resumo"); the author/contact lines are dropped (the cover and "About the Author" carry them);
  2. thematic breaks (`---` lines) removed (pandoc would draw a rule in the DOCX);
  3. the references (paragraphs under "## References...") become `- ` items (what validate_canon counts) and any
     other `- ` bullet AFTER the references becomes `* ` (appendix lists must not be counted as references);
  3b. in "About the Author", the Identifiers/Contact and (c)/licence lines (written on consecutive lines, meant as
     one line each) become separate paragraphs;
  4. the Portuguese Resumo is kept and marked lang=pt-BR (so Word does not spell-check it as English);
  5. the closing colophon line ("*End of whitepaper. References: 28 entries...*") is dropped unless
     --keep-colophon: validate_canon locates the reference list with doc.rfind("References"), and that line
     contains the word, which empties the list zone (artefact of the validator, not a defect of the paper).

Usage: python3 -I paper/tools/monta_asp.py --src paper/iron-law-11.md --out build/iron-law-11/fonte.md [--date 2026-11-07]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

AUTHOR = "Carlos Ulisses Flores"
AFFIL = "Codex Hash Research Laboratory"
ORCID = "0000-0002-6034-7765"
INFO_RX = re.compile(r"^\*\*(?!Author\*\*)")  # header lines that open with a bold label, except the Author line


def split_title(titulo: str) -> tuple[str, str]:
    """Cover needs a title and a subtitle (canon: CoverSubtitle is required)."""
    for sep in (" — ", ": "):
        if sep in titulo:
            a, b = titulo.split(sep, 1)
            return a.strip(), b.strip()
    raise SystemExit(f"title without ' — ' or ': ' to split into title/subtitle: {titulo!r}")


def derive(src: Path, date: str, keep_colophon: bool, drop_resumo: bool) -> tuple[str, dict]:
    texto = src.read_text(encoding="utf-8")
    rel: dict = {"hr_removed": 0, "refs": 0, "bullets_after_refs": 0, "info_lines": 0, "colophon_dropped": False,
                 "resumo": "dropped" if drop_resumo else "kept (lang=pt-BR, no page break)"}
    corte = texto.index("\n## ")
    cab, corpo = texto[:corte], texto[corte + 1:]
    h1 = re.search(r"^# (.+)$", cab, re.M)
    assert h1, "no H1 title"
    titulo, subtitulo = split_title(h1.group(1).strip())
    # header lines after the title: keep the labelled ones (Version, DOI, Status...), join wrapped continuations
    info: list[str] = []
    for ln in cab[h1.end():].splitlines():
        s = ln.strip()
        if not s or s == "---":
            continue
        if INFO_RX.match(s):
            info.append(s)
        elif info and not s.startswith(("CTO", "ORCID", "c.ulisses", "**Author")) and not s.startswith("**"):
            info[-1] += " " + s
    rel["info_lines"] = len(info)
    rel["titulo"], rel["subtitulo"] = titulo, subtitulo

    linhas = corpo.split("\n")
    saida: list[str] = []
    em_codigo = False
    for ln in linhas:
        if ln.startswith("```"):
            em_codigo = not em_codigo
        if not em_codigo and ln.strip() == "---":
            rel["hr_removed"] += 1
            continue
        saida.append(ln)
    corpo = re.sub(r"\n{3,}", "\n\n", "\n".join(saida))

    # colophon: last paragraph, italic, begins "*End of whitepaper" / "*End of note"
    m = re.search(r"\n\n\*End of [^\n]*(?:\n[^\n]+)*\s*\Z", corpo)
    if m and not keep_colophon:
        corpo = corpo[:m.start()] + "\n"
        rel["colophon_dropped"] = True

    # references -> '- ' items; later bullets -> '* '
    blocos = re.split(r"(?m)^(?=## )", corpo)
    novos, depois_refs = [], False
    for b in blocos:
        cabeca = b.split("\n", 1)[0]
        if cabeca.startswith("## References"):
            corpo_b = b.split("\n", 1)[1]
            itens = [re.sub(r"\s*\n\s*", " ", p.strip()) for p in re.split(r"\n\s*\n", corpo_b) if p.strip()]
            rel["refs"] = len(itens)
            b = cabeca + "\n\n" + "\n".join("- " + i for i in itens) + "\n\n"
            depois_refs = True
        elif depois_refs:
            b, k = re.subn(r"(?m)^- ", "* ", b)
            rel["bullets_after_refs"] += k
            if cabeca.startswith("## About the Author"):
                # the source writes Identifiers/Contact and the (c) / licence lines on consecutive lines meaning
                # one line each; Markdown would fuse them into one paragraph
                b, k = re.subn(r"\n(?=\*\*Contact\*\*|Text licensed|Paper text licensed)", "\n\n", b)
                rel["about_lines_split"] = k
        elif cabeca.strip() == "## Resumo":
            if drop_resumo:
                continue
            resto = b.split("\n", 1)[1].rstrip("\n")
            b = f"::: {{lang=pt-BR}}\n{cabeca}\n{resto}\n:::\n\n"
        novos.append(b)
    corpo = "".join(novos)
    # info block just before "## Resumo" (or before "## 1." when the Resumo is dropped)
    bloco_info = "".join(i + "\n\n" for i in info)
    ancora = "::: {lang=pt-BR}\n## Resumo" if not drop_resumo else None
    if ancora and ancora in corpo:
        corpo = corpo.replace(ancora, bloco_info + ancora, 1)
    else:
        m1 = re.search(r"(?m)^## 1\. ", corpo)
        corpo = corpo[:m1.start()] + bloco_info + corpo[m1.start():]
    meta = (f'---\ntitle: "{titulo}"\nsubtitle: "{subtitulo}"\nauthor: "{AUTHOR}"\naffiliation: "{AFFIL}"\n'
            f'orcid: "{ORCID}"\ndate: "{date}"\nlang: en-US\n---\n\n')
    return meta + "# " + h1.group(1).strip() + "\n\n" + corpo.rstrip() + "\n", rel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", default="2026-11-07")
    ap.add_argument("--keep-colophon", action="store_true")
    ap.add_argument("--drop-resumo", action="store_true")
    a = ap.parse_args()
    md, rel = derive(Path(a.src), a.date, a.keep_colophon, a.drop_resumo)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"[OK] {out} ({len(md.split())} words)")
    for k, v in rel.items():
        print(f"     {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
