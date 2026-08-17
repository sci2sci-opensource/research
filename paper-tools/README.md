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
Horizontal rules become page breaks in PDF. Figures are auto-discovered from image references —
no hardcoded lists; missing figures are reported.

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
- [ ] `oracles-axioms-paper/` — still on its local `compile_paper.py` fork
- [ ] `critical-volatility-and-v*/` — still on its local fork (edit from WSL/Linux only)

When migrating the older projects: build with both pipelines, compare outputs, then delete the
local fork (`compile_paper.py`, `latex-header.tex`, `paper-style.css`, `*-filter.lua`).
