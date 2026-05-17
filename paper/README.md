# ASP Preprint

LaTeX source for the ASP methodology preprint:

> **Anticipating Shadow Points: A 13-Phase Protocol for LLM Agent Pre-Mortem Planning, with an Empirical Finding on `claude -p /goal` Subprocess Error Routing**

## Files

| File | Purpose |
|---|---|
| `asp-preprint.tex` | Main paper source (LaTeX, `article` class, ~10 pages) |
| `references.bib` | BibTeX bibliography (Klein, MAST, Plan-and-Act, Reflexion, Anthropic docs) |
| `README.md` | This file |

## Build locally

Requires a TeX distribution (TeX Live, MacTeX, or MiKTeX) with `pdflatex` and `bibtex`.

```bash
cd paper
pdflatex asp-preprint.tex
bibtex   asp-preprint
pdflatex asp-preprint.tex
pdflatex asp-preprint.tex   # second run resolves cross-refs
```

Output: `asp-preprint.pdf`.

Alternatively, use [Overleaf](https://www.overleaf.com): create a new project, upload both files, and compile. Overleaf handles bibtex automatically.

## arXiv submission checklist

When ready to submit:

1. **Polish content**
   - [ ] Replace `{\relax{et al.}}` author placeholders in `references.bib` with full author lists once papers are formally cited.
   - [ ] Fill in actual ORCID iD in the title page (currently absent; add `\thanks{ORCID: https://orcid.org/...}` after the corresponding-author thanks).
   - [ ] Verify all URLs in `references.bib` still resolve.
   - [ ] Verify the empirical numbers (47%, 100%, 53pp delta) against the latest `tests/evals-summary.md` in the parent repo.
   - [ ] Consider adding 1-2 figures: (a) RED/GREEN coverage chart, (b) timeline of the 13 phases. Use `figures/` subdirectory; reference with `\includegraphics{figures/coverage-chart}`.

2. **Build the final PDF** locally; ensure no LaTeX errors and the PDF renders correctly.

3. **Create an arXiv submission package** (tarball with `.tex`, `.bib`, any figure files).

4. **Submit** via [arxiv.org/submit](https://arxiv.org/submit):
   - Primary category: `cs.AI` (Artificial Intelligence)
   - Cross-list: `cs.SE` (Software Engineering)
   - Optional cross-list: `cs.HC` (Human-Computer Interaction) if framing the human-in-the-loop angle.
   - Comments field: `10 pages, 2 tables. Independent research preprint. Companion software (MIT) at <github URL>; software DOI (Zenodo) and form-submitted Anthropic plugin directory listing referenced in CITATION.cff.`

5. **After arXiv assigns an ID**:
   - Update `CITATION.cff` in the repo root: uncomment the `arXiv:` identifier and fill in the actual ID.
   - Update `README.md` and `index.md` with the arXiv badge: `[![arXiv](https://img.shields.io/badge/arXiv-XXXX.XXXXX-b31b1b.svg)](https://arxiv.org/abs/XXXX.XXXXX)`.
   - Cross-post on Hugging Face Papers (https://hf.co/papers/submit) using the arXiv ID.

## License

Paper source is licensed under **CC BY 4.0** (Creative Commons Attribution 4.0 International). Software in the parent repository is **MIT**. The two licenses are compatible; the BY 4.0 requirement is attribution to the original author when reusing or adapting the methodology text or figures.

When reusing methodology figures or significant passages, please cite:

> Flores, U. (2026). *Anticipating Shadow Points: A 13-Phase Protocol for LLM Agent Pre-Mortem Planning, with an Empirical Finding on `claude -p /goal` Subprocess Error Routing.* Independent research preprint. https://github.com/ulissesflores/anticipating-shadow-points
