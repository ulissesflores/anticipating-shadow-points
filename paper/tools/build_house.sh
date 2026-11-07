#!/usr/bin/env bash
# Core of the ASP house build (fork of build_v04.sh from lgbt-indicador-violencia, English labels, no POS_DOCX step):
#   fonte.md -> export_house.py -> DOCX -> PDF EXPORTED BY MICROSOFT WORD (AppleScript) -> crivo_docx.py
#
#   paper/tools/build_house.sh --src build/<nome>/fonte.md --out build/<nome> --nome <nome> [--fig-cm auto|14]
#
# Needs pandoc, qpdf, poppler (pdffonts/pdfinfo/pdftoppm), Microsoft Word and /usr/bin/python3 (lxml, Pillow, PyMuPDF).
# Word is NOT quit if it already had documents open; only the exported document is closed.
# The Word sandbox asks "Grant File Access" the first time it opens a new path, so the DOCX is always copied to the
# same exchange file (WORD_IO, default = the path already authorised in the LGBT repo) and the PDF is born beside it.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"          # paper/
PY="${PYTHON_HOUSE:-/usr/bin/python3}"
SRC=""; OUT=""; NOME=""; FIG="auto"
while [ $# -gt 0 ]; do
  case "$1" in
    --src) SRC="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"; shift 2;;
    --out) mkdir -p "$2"; OUT="$(cd "$2" && pwd)"; shift 2;;
    --nome) NOME="$2"; shift 2;;
    --fig-cm) FIG="$2"; shift 2;;
    *) echo "usage: $0 --src md --out dir --nome base [--fig-cm auto|N]"; exit 64;;
  esac
done
[ -n "$SRC" ] && [ -n "$OUT" ] && [ -n "$NOME" ] || { echo "usage: $0 --src md --out dir --nome base"; exit 64; }
case "$OUT" in /private/tmp/*|/tmp/*) echo "[FAIL] output under /tmp: Word opens it in protected mode and the house rule forbids project trees there"; exit 65;; esac
TETO=$((4*1024*1024))
PXS=(${PX_LIST:-850 700 600 500})
DOCX="$OUT/$NOME.docx"; PDF="$OUT/$NOME.pdf"
WORD_IO="${WORD_IO:-/Users/ulissesflores/Developer/lgbt-indicador-violencia/paper/build/v04/word-io/entrada-word.docx}"

word_pdf() {  # $1 docx, $2 final pdf
  mkdir -p "$(dirname "$WORD_IO")"
  cp "$1" "$WORD_IO"
  local pdf_io="${WORD_IO%.docx}.pdf"
  rm -f "$pdf_io"
  osascript - "$WORD_IO" "$pdf_io" <<'APPLESCRIPT'
on run argv
  set docPath to item 1 of argv
  set pdfPath to item 2 of argv
  set docName to do shell script "basename " & quoted form of docPath
  with timeout of 900 seconds
    tell application "Microsoft Word"
      set n0 to count of documents
      open POSIX file docPath
      set t to 0
      repeat until (exists document docName) or t > 120
        delay 1
        set t to t + 1
      end repeat
      if not (exists document docName) then
        if n0 = 0 then quit saving no
        error "Word did not open " & docName & " in 120 s (probably 'Grant File Access': approve the path once, or use WORD_IO=<authorised path>)"
      end if
      set d to document docName
      save as d file name pdfPath file format format PDF
      close d saving no
      if n0 = 0 then quit saving no
    end tell
  end timeout
end run
APPLESCRIPT
  mv "$pdf_io" "$2"
}

for PX in "${PXS[@]}"; do
  echo "== exporting DOCX (images ${PX}px)"
  "$PY" "$ROOT/tools/export_house.py" --src "$SRC" --work "$OUT/work" --out "$DOCX" --fig-cm "$FIG" --img-px "$PX"
  echo "== Word -> PDF"
  word_pdf "$DOCX" "$PDF"
  [ -s "$PDF" ] || { echo "[FAIL] Word did not produce $PDF"; exit 70; }
  TAM=$(stat -f%z "$PDF")
  echo "   PDF: $TAM bytes ($(pdfinfo "$PDF" | awk '/^Pages:/{print $2}') pages)"
  [ "$TAM" -le "$TETO" ] && break
  echo "   > 4 MB: recompressing images only"
done
[ "$TAM" -le "$TETO" ] || { echo "[FAIL] PDF above 4 MB even at ${PX}px images"; exit 71; }
qpdf --check "$PDF" >/dev/null && echo "[OK] qpdf --check"
echo "== crivo"
set +e
"$PY" "$ROOT/tools/crivo_docx.py" "$DOCX" --pdf "$PDF" --render "$OUT/render"
RC=$?
set -e
mkdir -p "$OUT/render"
for old in "$OUT/render"/p-*.png; do [ -e "$old" ] && rm -f "$old"; done
pdftoppm -r 100 -png "$PDF" "$OUT/render/p" && echo "== $(ls "$OUT/render"/p-*.png | wc -l | tr -d ' ') pages rendered in $OUT/render (read ALL of them)"
echo "crivo_docx exit $RC (0 = clean; 1 = FORM violation; 2 = content pending only)"
exit $RC
