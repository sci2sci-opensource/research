# Reproducibility map

What each published claim rests on, what is in this repository, and what is not.

## Environment

Python 3.9.5 on Windows 11, single RTX 3070 (8 GB), torch 2.6.0+cu124. Exact package pins in each
package's `requirements.txt`, including the HuggingFace model/dataset snapshot revisions the
recorded runs used. GPU training is not bit-deterministic (fp16 autocast, cuDNN); the replicate
noise floors in every battery exist precisely to bound that nondeterminism — reproduced runs
should match within the recorded floors, not bitwise.

## Claim classes

**1. Battery-level claims** (order disagreement vs floors, conflict-set localisation, retraction,
improvement flips, negative control): reproduce by rerunning `run.bat experiment` in each package
(hours, GPU), or verify the recorded batteries directly — `results/<battery>/` contains figures,
summaries, logs, sealed predictions with SHA-256 hashes, and complete per-item ledgers
(`ledger.json.gz`; one split ledger reassembles with `cat *.part* | gunzip`).

**2. Ledger-only analyses** (QQ-drift, geometry race, instrument deficiency, commutator null,
contested predictor, flip floors): fully reproducible from this repository alone — gunzip a ledger
and run the scripts in `euh_pkg/analysis/` and `ner_enrich_pkg/analysis/`.

**3. Weight-space analyses** (seed-cosine null, interference grid, task-vector projections,
BCH/HVP test): the scripts are in `euh_pkg/analysis/`, but they require the run checkpoints
(~40 GB base/S/T/composite/replicate weights), which are **not in this repository**. They are
archived offline and available on request; a Zenodo deposit of the checkpoint archive is planned.
Until then these claims are auditable in method but not re-executable from public artifacts alone.

## What is deliberately not committed

Weight checkpoints (size), raw `runs/` working directories (superseded by `results/`), and
regenerated build artifacts (CI rebuilds papers per push).
