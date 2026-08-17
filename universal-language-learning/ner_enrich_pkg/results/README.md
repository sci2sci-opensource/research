# Committed run results

Materials from completed sealed-prediction batteries, committed as paper source: figures,
`summary.json`, `sealed_*.json` (SHA-256-hashed predictions written **before** the composites were
trained — never regenerate these), `log.txt`, and the full per-token ledgers (gzipped).

One ledger exceeds GitHub's 100 MB file limit and is split; reassemble with:

    cat base_strength/ledger.json.gz.part* | gunzip > base_strength/ledger.json

Everything here is regenerable *from* the ledger without retraining (`viz.py <ledger>`), except
the sealed files and logs, which are the primary record. Weight checkpoints are not in git;
they are archived offline.

Layout: `results/<battery>/<stage>/…` matching the structure `run.bat experiment` produces
under `runs/`.
