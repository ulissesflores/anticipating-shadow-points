# Build PDFs from the canonical Markdown whitepaper sources.
#
# Stack: pandoc (any 3.x) + tectonic (self-contained LaTeX engine that
# downloads packages on demand). Both available via Homebrew on macOS
# (`brew install pandoc tectonic`) or apt/dnf on Linux.
#
# Outputs:
#   asp-preprint.pdf
#   iron-law-11.pdf
#
# Usage:
#   make           # build both PDFs
#   make pdf       # alias
#   make clean     # remove generated PDFs and tectonic build cache
#   make watch     # rebuild on .md change (requires fswatch on macOS)
#   make print     # show resolved pandoc command for one document

PANDOC      ?= pandoc
PDF_ENGINE  ?= tectonic
SRC_MD       = asp-preprint.md iron-law-11.md
OUT_PDF      = $(SRC_MD:.md=.pdf)

# Pandoc options chosen so the rendered PDF stays readable on screen
# (1 inch margins, 11pt body) AND prints well on A4/Letter. Code blocks
# use the `tango` highlight style which is muted enough for a
# whitepaper. TOC included at depth 2 so the per-§ subsections are
# visible without flooding the contents page.
PANDOC_FLAGS = \
  --pdf-engine=$(PDF_ENGINE) \
  --include-in-header=header.tex \
  --variable=geometry:margin=1in \
  --variable=fontsize:11pt \
  --variable=documentclass:article \
  --variable=linkcolor:NavyBlue \
  --variable=urlcolor:NavyBlue \
  --variable=toccolor:black \
  --variable=colorlinks:true \
  --highlight-style=tango \
  --toc \
  --toc-depth=2 \
  --number-sections

.PHONY: all pdf clean watch print help

all: pdf

pdf: $(OUT_PDF)

%.pdf: %.md
	$(PANDOC) $(PANDOC_FLAGS) -o $@ $<
	@echo "built: $@"

clean:
	rm -f $(OUT_PDF)
	@echo "cleaned PDFs (tectonic cache at ~/Library/Caches/Tectonic/ is preserved across builds)"

watch:
	@command -v fswatch >/dev/null || { \
	  echo "fswatch not found. Install with: brew install fswatch"; \
	  exit 1; \
	}
	@echo "watching .md for changes..."
	@fswatch -o $(SRC_MD) | while read; do $(MAKE) pdf; done

print:
	@echo "$(PANDOC) $(PANDOC_FLAGS) -o asp-preprint.pdf asp-preprint.md"

help:
	@echo "Targets:"
	@echo "  make        — build both whitepaper PDFs"
	@echo "  make pdf    — same as make"
	@echo "  make clean  — remove generated PDFs"
	@echo "  make watch  — auto-rebuild on .md change (needs fswatch)"
	@echo "  make print  — show resolved pandoc command"
