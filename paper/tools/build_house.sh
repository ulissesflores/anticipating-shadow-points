#!/usr/bin/env bash
# Core of the ASP house build (fork of build_v04.sh from lgbt-indicador-violencia, English labels, no POS_DOCX step):
#   fonte.md -> export_house.py -> DOCX -> PDF EXPORTED BY MICROSOFT WORD (AppleScript) -> crivo_docx.py
#
#   paper/tools/build_house.sh --src build/<nome>/fonte.md --out build/<nome> --nome <nome> [--fig-cm auto|14]
#                              [--lang en|pt-BR|es|it]     (edition language: labels, Word proofing language, breaks)
#
# Needs pandoc, qpdf, poppler (pdffonts/pdfinfo/pdftoppm), Microsoft Word and /usr/bin/python3 (lxml, Pillow, PyMuPDF).
# Word is NOT quit if it already had documents open; only the exported document is closed.
# The Word sandbox asks "Grant File Access" the first time it opens a new path, so the DOCX is always copied to the
# same exchange file (WORD_IO, default = the path already authorised in the LGBT repo) and the PDF is born beside it.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"          # paper/
PY="${PYTHON_HOUSE:-/usr/bin/python3}"
SRC=""; OUT=""; NOME=""; FIG="auto"; LANG_ED="en"
while [ $# -gt 0 ]; do
  case "$1" in
    --src) SRC="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"; shift 2;;
    --out) mkdir -p "$2"; OUT="$(cd "$2" && pwd)"; shift 2;;
    --nome) NOME="$2"; shift 2;;
    --fig-cm) FIG="$2"; shift 2;;
    --lang) LANG_ED="$2"; shift 2;;
    *) echo "usage: $0 --src md --out dir --nome base [--fig-cm auto|N] [--lang en|pt-BR|es|it]"; exit 64;;
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
  # Every edition goes through the same exchange file name. If an earlier export failed, Word may still hold the
  # previous edition open under that name and would save THAT one (an English PDF came out as pt-BR on 2026-11-16).
  # So: the stale PDFs are removed first, a document left open under the name is closed before opening, a failed
  # save closes the document and fails the build, and the caller checks date and language of what came back.
  cp "$1" "$WORD_IO" || return 1
  local pdf_io="${WORD_IO%.docx}.pdf"
  rm -f "$pdf_io" "$2"
  # Contents page (house norm v1.7): a long edition carries a TOC field that only Word fills. Without updating the
  # field before saving, the PDF comes out with an empty contents page; two passes, because the first changes the
  # size of the contents itself and may push the pages it cites. `grep -c`, not `grep -q`: -q leaves at the first
  # hit, unzip dies of SIGPIPE and under pipefail the test is false exactly when there is a field (factory, 2026-11-19).
  local toc=0
  if unzip -p "$1" word/document.xml | grep -c 'TOC \\o' >/dev/null; then toc=1; fi
  osascript - "$WORD_IO" "$pdf_io" "$toc" > "${WORD_IO%.docx}.toc.txt" <<'APPLESCRIPT' || return 1
on run argv
  set docPath to item 1 of argv
  set pdfPath to item 2 of argv
  set hasToc to item 3 of argv
  set tocEntries to ""
  set docName to do shell script "basename " & quoted form of docPath
  -- a Word that is still starting answers "Connection is invalid (-609)" or "Not authorized (-1743)" to
  -- "count of documents" (three failed builds in a row on 2026-11-16): start it and ask until it answers
  if application "Microsoft Word" is not running then
    tell application "Microsoft Word" to launch
  end if
  set pronto to false
  repeat 30 times
    try
      tell application "Microsoft Word" to count of documents
      set pronto to true
      exit repeat
    on error
      delay 2
    end try
  end repeat
  if not pronto then error "Microsoft Word did not answer within 60 s of starting"
  with timeout of 900 seconds
    tell application "Microsoft Word"
      if (exists document docName) then close document docName saving no
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
      if hasToc is "1" then
        try
          if (count of tables of contents of d) = 0 then error "Word did not recognise the contents field"
          repeat 2 times
            update (table of contents 1 of d)
          end repeat
          set tocEntries to content of text object of table of contents 1 of d
        on error msg
          close d saving no
          if n0 = 0 then quit saving no
          error "could not update the contents field: " & msg
        end try
      end if
      try
        save as d file name pdfPath file format format PDF
      on error msg number num
        close d saving no
        if n0 = 0 then quit saving no
        error "Word could not save " & docName & " as PDF: " & msg number num
      end try
      close d saving no
      if n0 = 0 then quit saving no
    end tell
  end timeout
  return tocEntries
end run
APPLESCRIPT
  mv "$pdf_io" "$2" || return 1
  if [ "$toc" = 1 ]; then
    # Word closed without saving: the entries it computed go into the DOCX as the field result; the DOCX keeps the
    # date of the PDF made from it, so that "PDF older than its DOCX" still means a stale export
    "$PY" "$ROOT/tools/export_house.py" --entradas-do-sumario "$1" "${WORD_IO%.docx}.toc.txt" || return 1
    touch -r "$2" "$1"
  fi
}

# first heading of page 2 = the edition's own summary (en: Abstract); proves the PDF is of THIS edition
case "$LANG_ED" in en) P2="Abstract";; pt-BR) P2="Resumo";; es) P2="Resumen";; it) P2="Riassunto";; esac

for PX in "${PXS[@]}"; do
  echo "== exporting DOCX (images ${PX}px)"
  "$PY" "$ROOT/tools/export_house.py" --src "$SRC" --work "$OUT/work" --out "$DOCX" --fig-cm "$FIG" --img-px "$PX" --lang "$LANG_ED"
  echo "== Word -> PDF"
  word_pdf "$DOCX" "$PDF" || { echo "[FAIL] Word export failed; no PDF kept in $OUT"; exit 70; }
  [ -s "$PDF" ] || { echo "[FAIL] Word did not produce $PDF"; exit 70; }
  [ ! "$PDF" -ot "$DOCX" ] || { echo "[FAIL] $PDF is older than its DOCX (stale export)"; rm -f "$PDF"; exit 70; }
  pdftotext -f 2 -l 2 "$PDF" - | grep -v '^[[:space:]]*$' | head -3 | grep -qx "$P2" \
    || { echo "[FAIL] page 2 of $PDF does not open with '$P2': PDF of another edition"; rm -f "$PDF"; exit 72; }
  TAM=$(stat -f%z "$PDF")
  echo "   PDF: $TAM bytes ($(pdfinfo "$PDF" | awk '/^Pages:/{print $2}') pages)"
  [ "$TAM" -le "$TETO" ] && break
  echo "   > 4 MB: recompressing images only"
done
[ "$TAM" -le "$TETO" ] || { echo "[FAIL] PDF above 4 MB even at ${PX}px images"; exit 71; }
qpdf --check "$PDF" >/dev/null && echo "[OK] qpdf --check"
echo "== crivo"
set +e
"$PY" "$ROOT/tools/crivo_docx.py" "$DOCX" --pdf "$PDF" --render "$OUT/render" --lang "$LANG_ED"
RC=$?
set -e
mkdir -p "$OUT/render"
for old in "$OUT/render"/p-*.png; do [ -e "$old" ] && rm -f "$old"; done
pdftoppm -r 100 -png "$PDF" "$OUT/render/p" && echo "== $(ls "$OUT/render"/p-*.png | wc -l | tr -d ' ') pages rendered in $OUT/render (read ALL of them)"
echo "crivo_docx exit $RC (0 = clean; 1 = FORM violation; 2 = content pending only)"
exit $RC
