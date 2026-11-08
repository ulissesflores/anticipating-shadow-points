#!/usr/bin/env bash
# One article, end to end: canonical MD -> derived source -> DOCX -> PDF by Word -> crivo -> docs/paper/<nome>.<lang>.* -> canon.
#
#   English edition (the canonical Markdown, unchanged path):
#     paper/tools/build_paper.sh graceful-refusals|asp-preprint [--date 2026-11-07] [--drop-resumo] [--keep-colophon]
#   Translated edition (pt-BR, es, it):
#     paper/tools/build_paper.sh <nome> --lang pt-BR|es|it [--i18n-src <translated.md>] [--date 2026-11-07] [--keep-colophon]
#
# Translated edition:
#   * source  = paper/i18n/<nome>.<lang>.md (override the path with --i18n-src, e.g. build/i18n-test/<nome>.pt-BR.md);
#               the translated Markdown has the structure of paper/<nome>.md with the labels in its language and NO
#               "## Abstract": the English Abstract + Keywords are copied verbatim from paper/<nome>.md at build time.
#   * order   = cover -> local summary (Resumo / Resumen / Riassunto) + Keywords + Version/DOI/Status lines ->
#               Abstract (English) + Keywords -> 1. ...   (canon order; pt-BR: page break before the Abstract too,
#               as the canon's 4 breaks demand; es/it: no break, the canon has 3). About the Author: new page.  Details: header of paper/tools/monta_asp.py.
#   * labels  = Table/Figure/Note./References/Appendix/Date: in the edition language (paper/tools/rotulos.py), Word
#               proofing language pt-BR|es-ES|it-IT (docDefaults, theme, dc:language), crivo run with the same labels.
#   * output  = build/<nome>.<lang>/ and docs/paper/<nome>.<lang>.{docx,pdf}, tracked; their SHA-256 go to paper/PAPER-SHA256.txt.
#   * canon   = pt-BR: validate_canon --lang pt-BR (the known repo failure "manifest pip_freeze" is not ours to fix);
#               es/it: validate_canon --lang es|it when the canon has that layer (v1.3+), otherwise "not applicable".
# Does NOT commit, does NOT touch the canonical Markdown.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"       # repo root
PY="${PYTHON_HOUSE:-/usr/bin/python3}"
VALIDATE="${VALIDATE_CANON:-/Users/ulissesflores/Developer/research-lab/metodo/tools/validate_canon.py}"
CANON_JSON="/Users/ulissesflores/Developer/research-lab/metodo/templates/codex-hash-canon.json"
[ $# -ge 1 ] || { sed -n 2,6p "$0"; exit 64; }
NOME="$1"; shift
LANG_ED="en"; I18N_SRC=""; EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    --lang) LANG_ED="$2"; shift 2;;
    --i18n-src) I18N_SRC="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"; shift 2;;
    *) EXTRA+=("$1"); shift;;
  esac
done
case "$LANG_ED" in en|pt-BR|es|it) ;; *) echo "[FAIL] --lang must be en|pt-BR|es|it (got $LANG_ED)"; exit 64;; esac
if [ "$LANG_ED" = en ]; then
  TAG="$NOME"
  [ -z "$I18N_SRC" ] || { echo "[FAIL] --i18n-src only makes sense with --lang pt-BR|es|it"; exit 64; }
else
  TAG="$NOME.$LANG_ED"
  [ -n "$I18N_SRC" ] || I18N_SRC="$ROOT/paper/i18n/$NOME.$LANG_ED.md"
  [ -s "$I18N_SRC" ] || { echo "[FAIL] translated source not found: $I18N_SRC (use --i18n-src)"; exit 66; }
fi
BUILD="$ROOT/build/$TAG"
mkdir -p "$BUILD" "$ROOT/docs/paper"
if [ "$LANG_ED" = en ]; then
  "$PY" -I "$ROOT/paper/tools/monta_asp.py" --src "$ROOT/paper/$NOME.md" --out "$BUILD/fonte.md" ${EXTRA[@]+"${EXTRA[@]}"}
else
  "$PY" -I "$ROOT/paper/tools/monta_asp.py" --lang "$LANG_ED" --src "$I18N_SRC" --en-src "$ROOT/paper/$NOME.md" \
    --out "$BUILD/fonte.md" ${EXTRA[@]+"${EXTRA[@]}"}
fi
set +e
bash "$ROOT/paper/tools/build_house.sh" --src "$BUILD/fonte.md" --out "$BUILD" --nome "$TAG" --lang "$LANG_ED"
RC=$?
set -e
[ -s "$BUILD/$TAG.pdf" ] || exit 70
DOCS_NAME="$NOME.$LANG_ED"                          # docs/paper/<nome>.<lang>.{docx,pdf}; en keeps <nome>.en.*
cp "$BUILD/$TAG.docx" "$ROOT/docs/paper/$DOCS_NAME.docx"
cp "$BUILD/$TAG.pdf" "$ROOT/docs/paper/$DOCS_NAME.pdf"
echo "== copied to docs/paper/$DOCS_NAME.{docx,pdf} (crivo exit $RC)"
(cd "$ROOT/docs/paper" && shasum -a 256 *.pdf *.docx) > "$ROOT/paper/PAPER-SHA256.txt"   # outside the chain seal
echo "== paper/PAPER-SHA256.txt refreshed"
if ! "$PY" -I - "$CANON_JSON" "$LANG_ED" <<'PYEOF'
import json, sys
sys.exit(0 if sys.argv[2] in json.load(open(sys.argv[1], encoding="utf-8"))["i18n"]["langs"] else 1)
PYEOF
then
  echo "== canon: no i18n layer for '$LANG_ED' in $CANON_JSON; validate_canon not applicable (crivo only)"
  exit $RC
fi
PASTA="$("$PY" -I "$ROOT/paper/tools/canon_mirror.py" "$NOME" "$LANG_ED")"
python3 "$VALIDATE" "$PASTA" --lang "$LANG_ED" --json "$BUILD/canon.json" | tee "$BUILD/canon.txt" | tail -25 || true
exit $RC
