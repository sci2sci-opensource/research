"""Noise floor for the Prop 6.4 improvement-verdict flips (lab notes §2; ledger-only).

Flip signature between checkpoints X,Y:  err_R1(Y)-err_R1(X) < -t AND err_R0(Y)-err_R0(X) > +t
(or the reverse). Null: ordered pairs of same-order replicates - any flip signature there is
seed jitter. Reports observed flips against the null rate and at jitter-calibrated thresholds.

    python flip_floor.py <battery_dir> [stage ...]
    # gunzip <stage>/ledger.json.gz first (reassemble split parts per results/README.md)
"""
import itertools, json, os, sys
import numpy as np

B = sys.argv[1]
stages = sys.argv[2:] or ["tiny_strength", "base_strength"]
KEEP = ["O", "PER", "LOC"]
T = 0.002

def errs(P, labels, gold, gold0):
    v = np.array(labels)[np.asarray(P).argmax(1)]
    v0 = np.where(np.isin(v, KEEP), v, "O")
    return float((v != gold).mean()), float((v0 != gold0).mean())

for st in stages:
    L = json.load(open(os.path.join(B, st, "ledger.json")))
    gold = np.array(L["gold"]); gold0 = np.where(np.isin(gold, KEEP), gold, "O")
    null_flips = 0; null_pairs = 0; d0s = []; d1s = []
    obs_flips = 0; obs_checks = 0
    for key, c in L["cells"].items():
        for order in ("AB", "BA"):
            variants = [(c["P"][order], c["labels"][order])] + [tuple(r) for r in c["replicates"][order]]
            E = [errs(P, lab, gold, gold0) for P, lab in variants]
            for i, j in itertools.permutations(range(len(E)), 2):
                d1 = E[j][0] - E[i][0]; d0 = E[j][1] - E[i][1]
                null_pairs += 1; d0s.append(abs(d0)); d1s.append(abs(d1))
                if (d1 < -T and d0 > T) or (d0 < -T and d1 > T): null_flips += 1
        imp = c["score"]["improvement"]
        for pair in [("base", "A"), ("base", "B"), ("A", "AB"), ("B", "BA"), ("base", "AB"), ("base", "BA")]:
            p0, p1 = imp[pair[0]], imp[pair[1]]
            d1 = p1["err_R1"] - p0["err_R1"]; d0 = p1["err_R0"] - p0["err_R0"]
            obs_checks += 1
            if (d1 < -T and d0 > T) or (d0 < -T and d1 > T): obs_flips += 1
    rate = null_flips / max(null_pairs, 1)
    q95_0 = float(np.quantile(d0s, 0.95)); q95_1 = float(np.quantile(d1s, 0.95))
    obs_q = 0
    for key, c in L["cells"].items():
        imp = c["score"]["improvement"]
        for pair in [("base", "A"), ("base", "B"), ("A", "AB"), ("B", "BA"), ("base", "AB"), ("base", "BA")]:
            p0, p1 = imp[pair[0]], imp[pair[1]]
            d1 = p1["err_R1"] - p0["err_R1"]; d0 = p1["err_R0"] - p0["err_R0"]
            if (d1 < -q95_1 and d0 > q95_0) or (d0 < -q95_0 and d1 > q95_1): obs_q += 1
    print(f"=== {st}")
    print(f"  null: {null_flips}/{null_pairs} replicate pairs show a flip signature at t={T} (rate {rate:.3f})")
    print(f"  expected false flips in {obs_checks} checks: {rate * obs_checks:.1f}   observed: {obs_flips}")
    print(f"  replicate jitter 95th pct: |dR0|={q95_0:.4f}  |dR1|={q95_1:.4f}")
    print(f"  observed flips at jitter-calibrated thresholds: {obs_q}/{obs_checks}")
