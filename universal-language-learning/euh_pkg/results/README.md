# Committed run results

Materials from completed sealed-prediction batteries, committed as paper source: figures,
`summary.json`, `sealed_*.json` (SHA-256-hashed predictions written **before** the composites were
trained — never regenerate these), `log.txt`, aggregated report, and the full per-item ledgers
(`ledger.json.gz`, gzipped; every per-item probability for every checkpoint).

Everything here is regenerable *from* the ledger without retraining (`rescore.py`,
`viz.py <ledger>`), except the sealed files and logs, which are the primary record.
Weight checkpoints are not in git (~40 GB); they are archived offline.

Layout: `results/<battery>/<stage>/…` matching the structure `run.bat experiment` produces
under `runs/`.
