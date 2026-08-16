# Notes for coding agents

This is a personal research repository. If you are an AI agent working here on the owner's behalf,
follow these rules; they are not optional.

## Commits and pushes

- Commits are authored by the repository owner (`Valerii Kremnev <v@sci2sci.com>`). Do **not** add
  `Co-Authored-By` trailers, "generated with" footers, or any other agent attribution to commits.
- **Never push to `master`.** Work on a feature branch and let the owner review and merge.
  Confirm every push with the owner before it happens: exact ref, target branch, content.
- Never commit: `runs/`, checkpoints (`ckpt/`, `*.pt`), `results_*.zip`, `__pycache__/`, venvs,
  IDE folders.

## Windows checkout hazard

The directory `critical-volatility-and-v*/` has an asterisk in its name, which is an invalid path
on Windows. A full checkout, `reset --hard`, or `read-tree -u` on Windows will fail — and can
leave **phantom staged deletions of that directory in the index. Never commit an index in that
state.** Use a sparse checkout that excludes it (e.g. `git sparse-checkout set <your-dirs>`), or
build commits at the object level (`write-tree` / `mktree` / `commit-tree`) so untouched
directories are preserved by hash.

## Layout

- `universal-language-learning/` — the language-learning trilogy:
  - `papers/` — *On Learning Languages*, *Perfect Theory*, *Universal Language Learning Machine*,
    plus lab notes for the sealed-prediction experiments.
  - `euh_pkg/` — revision-order experiment (SNLI/BERT): sealed composite predictions, replicate
    noise floors, negative control. Entry point: `run.bat` / `run.sh` (profiles: `experiment`,
    `smoke`, `tiny`, `base`).
  - `ner_enrich_pkg/` — language-enrichment order experiment (CoNLL NER): conflict sets,
    retraction/conservativity, capacity-graded improvement flips. Entry point: `run.bat`.
  - Both packages resume at cell level from `ledger.json` + checkpoints; predictions are sealed
    with SHA-256 before composites are trained — do not regenerate sealed files retroactively.
- `two-board-problem/`, `oracles-axioms-paper/`, `critical-volatility-and-v*/` — earlier projects;
  leave them untouched unless explicitly asked.
