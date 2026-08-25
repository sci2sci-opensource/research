# paper-tools

One build pipeline for every paper in this repository. No per-project copies: the two older
projects carried diverged 500-line forks of the same compile script plus regenerated-on-every-run
header/css files; this directory replaces all of that with a single parameterized toolchain.

## Usage

```
python paper-tools/compile_paper.py path/to/paper.md              # html (+ pdf when LaTeX present)
python paper-tools/compile_paper.py path/to/paper.md --pdf --twocol
python paper-tools/compile_paper.py path/to/paper.md --arxiv      # arXiv source bundle
python paper-tools/build_all.py --html                            # every paper in the repo
```

## What counts as a paper

Any `*.md` with YAML front matter containing `title:`. Recognized keys: `title` (required),
`subtitle`, `date`, `author`, `institute`, `lang`. Defaults: author `Valerii Kremnev`,
institute `Independent Researcher, sci2sci llc`; date falls back to the current month.
Files without front matter (READMEs, notes) are ignored by `build_all`.

## Markdown dialect

Pandoc markdown with `tex_math_single_backslash` and `tex_math_dollars`: inline math as
`\( ... \)` or `$...$`, display math as `$$ ... $$` (with `\tag{}` supported via MathJax/amsmath).
Horizontal rules become page breaks in PDF; the table of contents occupies its own page or pages,
and each top-level References section starts on a separate page. Figures are auto-discovered from
image references — no hardcoded lists; missing figures are reported.

## Shared assets — extend, don't fork

- `latex-header.tex` — canonical preamble. Per-paper additions: put `header-extra.tex` next to the
  paper; it is appended automatically.
- `paper-style.css` — canonical HTML style (embedded into standalone HTML).
- `filters/` — pagebreak on `---`, bold table headers (PDF only).

Changes to shared assets affect every paper; that is the point. If a paper needs something the
shared assets cannot express additively, raise it rather than forking.

## Dependencies

- `pandoc` (required) — `apt install pandoc` / `brew install pandoc` / `winget install pandoc`
- `pdflatex` (PDF output only) — texlive (`texlive-latex-base texlive-latex-extra`) / MiKTeX.
  Without it, PDF steps are skipped with a notice; HTML always works.

On this project's Windows machine, builds run inside WSL Ubuntu (see repo `CLAUDE.md` for the
Windows checkout caveat about the `critical-volatility-and-v*` directory).

## Migration status

- [x] `universal-language-learning/papers/` — built with paper-tools
- [x] `oracles-axioms-paper/` — front matter added, local fork removed
- [x] `critical-volatility-and-v*/` — front matter added, local fork removed (edit from WSL/Linux only)

Legacy `.latex.md` names are supported: outputs strip the inner `.latex` so historical artifact
names are preserved.
