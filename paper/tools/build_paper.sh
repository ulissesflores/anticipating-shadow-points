#!/usr/bin/env bash
# One article, end to end: canonical MD -> derived source -> DOCX -> PDF by Word -> crivo -> docs/paper/<nome>.en.* -> canon.
#   paper/tools/build_paper.sh iron-law-11|asp-preprint [--date 2026-11-07] [--drop-resumo] [--keep-colophon]
# Does NOT commit, does NOT touch the canonical Markdown.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"       # repo root
PY="${PYTHON_HOUSE:-/usr/bin/python3}"
NOME="$1"; shift
mkdir -p "$ROOT/build/$NOME" "$ROOT/docs/paper"
"$PY" -I "$ROOT/paper/tools/monta_asp.py" --src "$ROOT/paper/$NOME.md" --out "$ROOT/build/$NOME/fonte.md" "$@"
set +e
bash "$ROOT/paper/tools/build_house.sh" --src "$ROOT/build/$NOME/fonte.md" --out "$ROOT/build/$NOME" --nome "$NOME"
RC=$?
set -e
[ -s "$ROOT/build/$NOME/$NOME.pdf" ] || exit 70
cp "$ROOT/build/$NOME/$NOME.docx" "$ROOT/docs/paper/$NOME.en.docx"
cp "$ROOT/build/$NOME/$NOME.pdf" "$ROOT/docs/paper/$NOME.en.pdf"
echo "== copied to docs/paper/$NOME.en.{docx,pdf} (crivo exit $RC)"
PASTA="$("$PY" -I "$ROOT/paper/tools/canon_mirror.py" "$NOME")"
python3 /Users/ulissesflores/Developer/research-lab/metodo/tools/validate_canon.py "$PASTA" --lang en --json "$ROOT/build/$NOME/canon.json" | tee "$ROOT/build/$NOME/canon.txt" | tail -25 || true
exit $RC
