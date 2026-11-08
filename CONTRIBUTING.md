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

- **Carlos Ulisses Flores** — [@ulissesflores on GitHub](https://github.com/ulissesflores) — [ulissesflores.com](https://ulissesflores.com)

## Code of conduct

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md) (Contributor Covenant 2.1).

## Rebuilding the whitepaper PDFs

The Markdown sources in `paper/*.md` are canonical; the PDF and DOCX editions
are derived. They follow the Codex Hash house norm (cover with logo, Times New
Roman 12, double spacing, APA 7 references) and are produced by
`paper/tools/build_paper.sh`, which exports a DOCX and has **Microsoft Word**
(macOS, through AppleScript) print the PDF:

```bash
python run_all.py                           # regenerate the figures first
paper/tools/build_paper.sh graceful-refusals      # -> docs/paper/graceful-refusals.en.{pdf,docx}
paper/tools/build_paper.sh asp-preprint     # -> docs/paper/asp-preprint.en.{pdf,docx}
```

Requirements: pandoc, qpdf, poppler and Microsoft Word, plus a Python with
`lxml` and `Pillow`. The script also runs the house checker on the DOCX and the
PDF, copies both to `docs/paper/` (tracked) and refreshes their SHA-256 in
`paper/PAPER-SHA256.txt`, which `tests/test_paper_pdf_hashes.py` checks. Pass
`--lang pt-BR|es|it` for a translated edition; every edition opens with the
English Abstract. For the citable artefact, always use the files archived under
the [Zenodo DOI](https://doi.org/10.5281/zenodo.20276631), not a local rebuild.
