# Seal disclosure — power_nullswap, cell a1.0_s0

This cell carries **two seals**. Disclosed here in full so the reader can judge it rather than
discover it.

## What happened

The first attempt at this stage died mid-cell when the checkpoint drive (D:) filled up
(`PytorchStreamWriter failed writing file data/0`). Timeline from `log.txt`:

| time | event |
|---|---|
| 18:00:43 | pass S trained |
| 18:01:08 | pass T trained |
| 18:01:41 | **prediction sealed**, hash `142e4d1e2fc0a5dd…` |
| 18:01:42 – 18:03:39 | composites S→T, T→S and replicates trained |
| ~18:04 | process died writing a replicate checkpoint; **no scoring step reached** |

The stage was then re-run with `CKPT_DIR` moved to a drive with free space. Because the run
never completed a cell, no `ledger.json` was written, so the re-run retrains base/S/T from
scratch and seals a second prediction. `sweep.py`'s append-only guard preserves the first seal
and writes the second as `sealed_a1.0_s0.reseal<ts>.json`, marking the ledger cell `resealed`.

## Why this differs from the v1 contamination

In the v1 incident (`base_strength/a0.25_s0`, 2026-08-15) the aborted attempt had **already
produced composite statistics**, which survived in `log.txt` with near-identical headline
numbers — so the rewritten seal could not be certified blind, and that cell was excluded from
sealed-prediction claims.

Here the aborted attempt produced **no `OBSERVED` line and no scoring output of any kind**: it
died between training the composites and evaluating them. No composite marginal, disagreement
rate, Γ, or per-item verdict for this cell was ever computed, logged, or read. Both seals are
therefore predictions made from base/S/T alone, before any composite outcome existed.

## How to treat it

The two seals are independent blind predictions of the same cell from separately trained
base/S/T, and can be compared against each other as a bonus consistency check. Conservative
readers who prefer a uniform rule may still exclude `a1.0_s0` from sealed-prediction claims for
this stage; the stage's hypothesis verdicts should be checked with and without it, since with
only 3 cells per arm one exclusion is not negligible.

## Checkpoint location

The crash was a full disk, so the re-run stages were written to a second drive and this battery's
checkpoints were briefly split across two. They have since been consolidated: all six stages
(186 checkpoints) now live under
`D:\model_checkpoints\euh_pkg\exp_power_20260817_173817\<stage>`, reachable through the per-stage
`ckpt` junctions, each verified loadable after the move. Space was reclaimed by deleting the
superseded 2026-08-15 batteries' checkpoints (euh v1, ner v1, the ner quick pilot and a
smoketest); every one of those batteries retains its results package and ledgers, and both v1
batteries were reproduced by the 2026-08-17 re-runs.
