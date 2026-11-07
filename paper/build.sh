#!/usr/bin/env bash
# Rebuild the two whitepaper PDFs from their canonical Markdown sources.
# Requires pandoc and tectonic (brew install pandoc tectonic). No network beyond
# tectonic's first-run package cache. Figures are read from ../output/figures/.
# Each paper is written as PDF and as DOCX (the house pattern keeps both beside
# the Markdown source); refs-hanging.lua gives the reference list a hanging indent.
set -euo pipefail
cd "$(dirname "$0")"
for SRC in asp-preprint.md iron-law-11.md; do
  pandoc "$SRC" \
    --resource-path=.:.. \
    --pdf-engine=tectonic \
    --include-in-header=pdf-header.tex \
    --variable=geometry:margin=1in \
    --variable=fontsize:11pt \
    --variable=documentclass:article \
    --variable=linkcolor:NavyBlue \
    --variable=urlcolor:NavyBlue \
    --variable=colorlinks:true \
    --highlight-style=tango \
    --lua-filter=refs-hanging.lua \
    -o "${SRC%.md}.pdf"
  pandoc "$SRC" \
    --resource-path=.:.. \
    --lua-filter=refs-hanging.lua \
    -o "${SRC%.md}.docx"
  for OUT in "${SRC%.md}.pdf" "${SRC%.md}.docx"; do
    echo "built paper/$OUT ($(du -k "$OUT" | cut -f1) KB)"
  done
done
