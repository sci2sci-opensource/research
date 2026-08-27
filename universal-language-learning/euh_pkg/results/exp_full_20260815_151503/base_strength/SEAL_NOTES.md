# Seal integrity notes

**`sealed_a0.25_s0.json` is restart-contaminated and excluded from sealed-prediction claims.**

Timeline (from `log.txt`, which is append-only and preserves both attempts): the cell's original
seal was written 2026-08-17 17:21:25 (hash prefix `63250a6bb0f19f72`) and its composites began
training; the battery was killed ~18:10 (VRAM-spill remediation) and resumed 18:12; because the
cell had not reached the ledger, it was rerun from scratch and its seal **overwritten** at
18:13:15 (hash prefix `7f46da7e7564d79e`) — i.e., written after composites for this cell had
already been trained once. The original full seal is unrecoverable; its hash prefix and headline
statistics survive in `log.txt` (the two seals' printed statistics agree to 3 decimal places,
consistent with benign regeneration, but integrity is defined by ordering, not similarity).

All other seals in this battery precede their composites; `tiny_strength`, `base_shared`, and
`base_weighted` are uncontaminated, as is the ner battery (no mid-battery restarts).

As of the accompanying code change, `sweep.py` refuses to overwrite seals: a rerun writes
`sealed_<cell>.reseal<ts>.json` alongside and marks the cell `resealed` in the ledger.
