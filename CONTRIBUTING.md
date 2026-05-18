# Contributing to ASP

Thanks for considering a contribution. ASP is a living skill — refinements to the methodology, additional evals from your domain, native-speaker translation review, and bug fixes are all welcome.

## Quick reference

| You want to... | Open this |
|---|---|
| Report a bug or unexpected behavior | [Bug Report issue](.github/ISSUE_TEMPLATE/bug_report.md) |
| Propose a new feature or methodology refinement | [Feature Request issue](.github/ISSUE_TEMPLATE/feature_request.md) |
| Contribute a new eval from your domain | [Eval Contribution issue](.github/ISSUE_TEMPLATE/eval_contribution.md) |
| Submit code/docs changes | PR against `main` — see workflow below |
| Improve a translation (native speaker) | PR editing `docs/README.{es,pt,it,he}.md` |
| Rebuild a whitepaper PDF from its `.md` source | See [§ Rebuilding the whitepaper PDFs](#rebuilding-the-whitepaper-pdfs) |
| Report a security vulnerability | **Do NOT open a public issue.** See [SECURITY.md](SECURITY.md) |

## Workflow

```bash
# 1. Fork on GitHub, then clone your fork
git clone https://github.com/<your-username>/anticipating-shadow-points.git
cd anticipating-shadow-points

# 2. Create a feature branch (descriptive name)
git checkout -b feat/<short-description>
# or fix/<short-description>, docs/<short-description>, eval/<domain>

# 3. Make your changes

# 4. Validate locally
./scripts/verify.sh --pre-install
# (CI also runs this on push; should be 19/20 OK in --pre-install mode)

# 5. Commit with sign-off (DCO-required)
git commit -s -m "feat(<scope>): <imperative summary>"
# -s adds Signed-off-by trailer; required for DCO check to pass

# 6. Push and open a PR
git push origin feat/<short-description>
gh pr create
```

## Commit message conventions

We use **Conventional Commits**:

- `feat(scope): ...` — new feature, methodology addition
- `fix(scope): ...` — bug fix
- `docs(scope): ...` — documentation only
- `eval(domain): ...` — new eval added
- `refactor(scope): ...` — code change without functional impact
- `test(scope): ...` — TDD baseline or eval test changes
- `chore(scope): ...` — tooling, CI, dependencies

Scopes commonly used: `plugin`, `skill`, `kernel`, `runner`, `evals`, `templates`, `i18n`, `ci`, `pages`.

## What we look for in PRs

1. **`scripts/verify.sh --pre-install` passes** — 19/20 OK (criterion 13 skipped pre-install).
2. **CI green** — yaml-lint, shellcheck, markdown-lint, plugin.json + marketplace.json validation.
3. **Signed-off-by trailer** on every commit (DCO).
4. **Conventional commit message** with clear scope.
5. **For methodology changes**: PR description explains the failure mode it addresses + which Iron Law (if any) is affected.
6. **For evals**: input + expected shadow points + acceptance criterion, following the format in `skills/anticipating-shadow-points/evals/01-supabase-migration.md`.
7. **For translations**: structural parallelism with the English source; PR description states "native speaker review" status.

## Iron Laws apply to contributors too

The 12 Iron Laws documented in `skills/anticipating-shadow-points/SKILL.md` apply not only to ASP runtime but to ASP development:

- **Iron Law 4** — for non-trivial PRs, include evidence (verify output, eval results, screenshots).
- **Iron Law 6** — significant methodology changes should be reflected in `docs/ARCHITECTURE.md` + memory write-back guidance in the PR description.
- **Iron Law 11** — if your PR touches any `claude -p` invocation in scripts/CI, you MUST parse JSON, never trust `$?`.

## Translations — native-speaker review welcomed

The English README and ARCHITECTURE.md are canonical. Translations under `docs/README.*.md` are:

| Language | Current state |
|---|---|
| 🇪🇸 Español | AI-assisted, awaiting native-speaker review |
| 🇧🇷 Português | Native (author is PT-BR speaker) |
| 🇮🇹 Italiano | AI-assisted, awaiting native-speaker review |
| 🇮🇱 עברית | AI-assisted (RTL marked), awaiting native-speaker review |

If you're a native speaker, open a PR with attribution — your authorship will be credited in `AUTHORS`.

## Questions?

Open an issue with the question tag, or contact the maintainer:

- **Ulisses Flores** — [@ulissesflores on GitHub](https://github.com/ulissesflores) — [ulissesflores.com](https://ulissesflores.com)

## Code of conduct

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md) (Contributor Covenant 2.1).

## Rebuilding the whitepaper PDFs

The repository ships pre-built whitepaper PDFs (`paper/asp-preprint.pdf`
and `paper/iron-law-11.pdf`). The Markdown sources (`paper/*.md`) are
canonical; the PDFs are derived artefacts. The current PDFs are also
attached to the GitHub Release for v1.0.0 and archived under the
Zenodo DOI for permanent citation.

If you fork the work, change a `.md` source, or want to verify the
PDFs were generated from the published `.md` sources, rebuild from
scratch with **pandoc + tectonic** (a self-contained LaTeX engine that
downloads its packages on demand — no full TeX Live install required).

### One-time setup (macOS)

```bash
brew install pandoc tectonic
```

For Linux, install both via your distribution's package manager (or
download tectonic's static binary from <https://tectonic-typesetting.github.io/>).

### Inline build command

The PDFs were built with the following invocation, applied to each
`paper/*.md` source:

```bash
cd paper

# Write the LaTeX header that maps Unicode → math-mode (keeps the .md
# source human-readable while ensuring portable PDF rendering with
# tectonic's default Latin Modern fonts):
cat > /tmp/asp-pdf-header.tex <<'HEADER_EOF'
\usepackage{newunicodechar}
\newunicodechar{≥}{\ensuremath{\geq}}
\newunicodechar{≤}{\ensuremath{\leq}}
\newunicodechar{≈}{\ensuremath{\approx}}
\newunicodechar{≠}{\ensuremath{\neq}}
\newunicodechar{κ}{\ensuremath{\kappa}}
\newunicodechar{α}{\ensuremath{\alpha}}
\newunicodechar{β}{\ensuremath{\beta}}
\newunicodechar{Δ}{\ensuremath{\Delta}}
\newunicodechar{σ}{\ensuremath{\sigma}}
\newunicodechar{·}{\ensuremath{\cdot}}
\newunicodechar{×}{\ensuremath{\times}}
\newunicodechar{→}{\ensuremath{\to}}
\newunicodechar{←}{\ensuremath{\leftarrow}}
\newunicodechar{⇒}{\ensuremath{\Rightarrow}}
\newunicodechar{∈}{\ensuremath{\in}}
\newunicodechar{"}{``}
\newunicodechar{"}{''}
\newunicodechar{'}{`}
\newunicodechar{'}{'}
HEADER_EOF

# Build each whitepaper:
for SRC in asp-preprint.md iron-law-11.md; do
  pandoc "$SRC" \
    --pdf-engine=tectonic \
    --include-in-header=/tmp/asp-pdf-header.tex \
    --variable=geometry:margin=1in \
    --variable=fontsize:11pt \
    --variable=documentclass:article \
    --variable=linkcolor:NavyBlue \
    --variable=urlcolor:NavyBlue \
    --variable=colorlinks:true \
    --highlight-style=tango \
    -o "${SRC%.md}.pdf"
done

rm /tmp/asp-pdf-header.tex
```

That's it — two files are produced: `asp-preprint.pdf` and `iron-law-11.pdf`.

### Why this build is portable

- **pandoc** is widely packaged (macOS, all major Linux distros).
- **tectonic** is a single static binary with no transitive system
  dependencies; it downloads each LaTeX package the first time you
  need it and caches it for subsequent runs.
- The `newunicodechar` mappings let the canonical `.md` keep real
  Unicode (≥, ≤, κ, ·, ×, etc.) — the source remains grep-able and
  renders correctly on GitHub/Typora/Obsidian, while the PDF renders
  these as proper math symbols.
- Anyone with the same `pandoc` + `tectonic` versions reproduces the
  PDF byte-identically (modulo PDF metadata timestamps).

### Verifying a rebuild matches the published PDF

Per-byte equality across pandoc versions is not guaranteed (pandoc
revisions occasionally tweak typography). To verify your rebuild is
semantically faithful:

```bash
pdftotext asp-preprint.pdf - | head -200       # extract first 200 lines
pdftotext paper/asp-preprint.pdf - | head -200 # compare to shipped PDF
diff <(...) <(...)                              # should be empty
```

For the canonical citable artefact, always reference the PDFs attached
to the [GitHub Release](https://github.com/ulissesflores/anticipating-shadow-points/releases/tag/v1.0.0)
or the [Zenodo deposit](https://doi.org/10.5281/zenodo.20276632), not
a local rebuild.
