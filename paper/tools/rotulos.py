#!/usr/bin/env python3
"""Rótulos estruturais por idioma da edição (UM lugar): o exportador, o crivo e o espelho do canon leem daqui.

Edição inglesa (`en`) reproduz byte a byte os literais que o exportador tinha antes desta tabela; as outras três
(`pt-BR`, `es`, `it`) são as edições traduzidas. A edição traduzida leva o resumo no idioma dela e o Abstract em
inglês (espelho literal do `paper/<nome>.md`); a camada i18n do canon
(/Users/ulissesflores/Developer/research-lab/metodo/templates/codex-hash-canon.json) fixa a ordem e as quebras de
página: pt-BR = 4 (Resumo, Abstract, 1., Referências), es/it = 3 (resumo local, 1., Referências; o Abstract vem logo
depois do resumo local, sem quebra, como o Resumo na edição inglesa).

Campos:
  code      idioma de revisão do Word (w:lang) e dc:language                 | table/figure/note/source  rótulos
  refs      título da seção de referências (casa por prefixo)                | resumo   título do resumo local
  keywords  marcador de palavras-chave (sem os dois-pontos)                  | appendix "Apêndice X —"
  date      rótulo da data na capa; date_fmt/months formatam                 | breaks   títulos com pageBreakBefore
  about     prefixos (minúsculos) do título "Sobre o autor" (casa por prefixo)
  author    rótulo da linha de autoria do cabeçalho do Markdown (descartada: a capa a repõe)
"""
from __future__ import annotations

LABELS: dict[str, dict] = {
    "en": dict(
        code="en-US", table="Table", figure="Figure", note="Note.", source="Source", refs="References",
        resumo="Resumo", keywords="Keywords", appendix="Appendix", date="Date", date_fmt="{mes} {dia}, {ano}",
        months=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                "November", "December"],
        breaks=("abstract", "intro", "refs"), about=("about the author",), author="Author"),
    "pt-BR": dict(
        code="pt-BR", table="Tabela", figure="Figura", note="Nota.", source="Fonte", refs="Referências",
        resumo="Resumo", keywords="Palavras-chave", appendix="Apêndice", date="Data",
        date_fmt="{dia} de {mes} de {ano}",
        months=["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
                "novembro", "dezembro"],
        breaks=("resumo", "abstract", "intro", "refs"), about=("sobre o autor",), author="Autor"),
    "es": dict(
        code="es-ES", table="Tabla", figure="Figura", note="Nota.", source="Fuente", refs="Referencias",
        resumo="Resumen", keywords="Palabras clave", appendix="Apéndice", date="Fecha",
        date_fmt="{dia} de {mes} de {ano}",
        months=["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
                "noviembre", "diciembre"],
        breaks=("resumo", "intro", "refs"), about=("sobre el autor", "acerca del autor"), author="Autor"),
    "it": dict(
        code="it-IT", table="Tabella", figure="Figura", note="Nota.", source="Fonte", refs="Riferimenti bibliografici",
        resumo="Riassunto", keywords="Parole chiave", appendix="Appendice", date="Data", date_fmt="{dia} {mes} {ano}",
        months=["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre",
                "ottobre", "novembre", "dicembre"],
        breaks=("resumo", "intro", "refs"), about=("sull'autore", "l'autore", "sull’autore", "l’autore"),
        author="Autore"),
}
IDIOMAS = tuple(LABELS)

# União de todos os idiomas: o exportador usa para recuo de Resumo/Abstract e marcador de palavras-chave, e o crivo
# para "bullet dentro do resumo" (independe do idioma da edição).
TODOS_RESUMOS = ("Abstract",) + tuple(dict.fromkeys(v["resumo"] for v in LABELS.values()))
TODOS_KEYWORDS = tuple(dict.fromkeys(v["keywords"] for v in LABELS.values()))
TODOS_AUTHOR = tuple(dict.fromkeys(v["author"] for v in LABELS.values()))


def get(lang: str) -> dict:
    if lang not in LABELS:
        raise SystemExit(f"idioma {lang!r} desconhecido (use um de {', '.join(IDIOMAS)})")
    return LABELS[lang]
