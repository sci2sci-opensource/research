# Notes for coding agents

## Windows checkout hazard

The directory `critical-volatility-and-v*/` has an asterisk in its name, which is an invalid path
on Windows. A full checkout, `reset --hard`, or `read-tree -u` on Windows will fail — and can
leave **phantom staged deletions of that directory in the index. Never commit an index in that
state.** Use a sparse checkout that excludes it (e.g. `git sparse-checkout set <your-dirs>`), or
build commits at the object level (`write-tree` / `mktree` / `commit-tree`) so untouched
directories are preserved by hash. Full worktrees are fine inside WSL's own filesystem.

## Do not commit

Run outputs (`runs/`), model checkpoints (`ckpt/`, `*.pt`), `results_*.zip`, `__pycache__/`,
venvs, IDE folders, and build artifacts produced by paper-tools (`*.html`, `*.pdf`).

## Layout

- `paper-tools/` — the single markdown build pipeline (PDF/HTML/arXiv) for every paper in the
  repo. Extend its shared assets (`header-extra.tex` next to a paper); never fork per-paper
  copies of the tooling. See `paper-tools/README.md`.
- `universal-language-learning/` — the language-learning trilogy:
  - `papers/` — *On Learning Languages*, *Perfect Theory*, *Universal Language Learning Machine*,
    plus lab notes for the sealed-prediction experiments.
  - `euh_pkg/` — revision-order experiment (SNLI/BERT): sealed composite predictions, replicate
    noise floors, negative control. Entry point: `run.bat` / `run.sh` (profiles: `experiment`,
    `smoke`, `tiny`, `base`).
  - `ner_enrich_pkg/` — language-enrichment order experiment (CoNLL NER): conflict sets,
    retraction/conservativity, capacity-graded improvement flips. Entry point: `run.bat`.
  - Both packages resume at cell level from `ledger.json` + checkpoints; predictions are sealed
    with SHA-256 before composites are trained — **do not regenerate sealed files retroactively.**
- `two-board-problem/`, `oracles-axioms-paper/`, `critical-volatility-and-v*/` — earlier projects;
  leave them untouched unless explicitly asked.
