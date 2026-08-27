# Analysis scripts

Ledger-only post-hoc analyses (fully reproducible from this repository; gunzip a ledger from
`../results/<battery>/<stage>/` first — reassemble the split ledger per `../results/README.md`).

- `flip_floor.py` — replicate-pair noise floor for the improvement-verdict (Prop 6.4) flips,
  plus jitter-calibrated re-thresholding. Reproduces the 0-false-flip null and the
  capacity-graded flip counts in the lab notes.
