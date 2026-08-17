# Analysis scripts

The post-hoc analyses behind the lab-note claims (see `papers/labnotes_2026-08-15_order_experiments.md`
§3 and the correction notes). Two classes:

**Ledger-only — fully reproducible from this repository.** Gunzip a ledger from
`../results/<battery>/<stage>/` first.

- `qq_analog.py` — QQ-equality analog (order-invariance of the agreement diagonal); the
  alpha-dependent sign-changing violation.
- `algebra_observables.py` — geometry race (prob vs ALR vs sqrt amplitude composition),
  instrument context-deficiency, channel-commutator null.
- `contested_predictor.py` — doubly-contested susceptibility vs observed disagreement.

**Checkpoint-dependent — require the run checkpoints (not in git; ~40 GB, available on
request; see ../../REPRODUCIBILITY.md).**

- `seed_cosine_null.py` — seed-to-seed vs cross-context task-vector cosines; corrected plane
  projections via explicit normal equations.
- `interference_grid.py` — 6x6 weight-space superposition grid + composite plane projections
  (GPU, ~2 min).
- `bch_hvp.py` — second-order BCH/HVP direction test via Hessian-vector products (GPU).

All scripts take the battery/checkpoint directory as their first argument.
