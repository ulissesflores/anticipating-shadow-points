#!/usr/bin/env bash
# Rebuild the two whitepaper PDFs from their canonical Markdown sources.
# Requires pandoc and tectonic (brew install pandoc tectonic). No network beyond
# tectonic's first-run package cache. Figures are read from ../output/figures/.
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
    -o "${SRC%.md}.pdf"
  echo "built paper/${SRC%.md}.pdf ($(du -k "${SRC%.md}.pdf" | cut -f1) KB)"
done
