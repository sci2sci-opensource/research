"""Contested-susceptibility exploration (lab notes §1.2; ledger-only).

Doubly-contested items: both single passes move the item's ALR logits farther than its
base distance to a verdict boundary — the items *capable* of order dependence. Compares
the contested fraction with observed disagreement and the sealed ALR-null prediction.

    python contested_predictor.py <battery_dir> [stage]
    # gunzip <stage>/ledger.json.gz first
"""
import json, os, sys
import numpy as np

B = sys.argv[1]
st = sys.argv[2] if len(sys.argv) > 2 else "base_shared"

def alr(P, eps=1e-6):
    P = np.clip(P, eps, 1); return np.log(P[:, [0, 2]] / P[:, [1]])

def verdicts(P): return np.array(P).argmax(1)

def boundary_dist(X):
    a, b = X[:, 0], X[:, 1]
    d_a0 = np.abs(a); d_b0 = np.abs(b); d_ab = np.abs(a - b) / np.sqrt(2)
    v = np.select([(a > 0) & (a >= b), (b > 0) & (b > a)], [0, 2], default=1)
    d = np.where(v == 0, np.minimum(d_a0, d_ab),
        np.where(v == 2, np.minimum(d_b0, d_ab), np.minimum(d_a0, d_b0)))
    return d, v

L = json.load(open(os.path.join(B, st, "ledger.json")))
Pb = np.array(L["base"])
print(f"{'cell':>10} | {'obs dis':>8} | {'sealed(alr)':>11} | {'contested':>9} | {'union-both':>10}")
for key, cell in sorted(L["cells"].items()):
    PS, PT = np.array(cell["P"]["S"]), np.array(cell["P"]["T"])
    PST, PTS = np.array(cell["P"]["ST"]), np.array(cell["P"]["TS"])
    vb, vS, vT, vST, vTS = map(verdicts, (Pb, PS, PT, PST, PTS))
    obs = float(np.mean(vST != vTS))
    Xb = alr(Pb)
    nS = np.linalg.norm(alr(PS) - Xb, axis=1); nT = np.linalg.norm(alr(PT) - Xb, axis=1)
    m, _ = boundary_dist(Xb)
    contested = (nS > m) & (nT > m)
    both_flip = (vS != vb) & (vT != vb)
    sealed_alr = cell["prediction"]["alr"]["pred_disagreement"]
    print(f"{key:>10} | {obs:8.4f} | {sealed_alr:11.4f} | {contested.mean():9.4f} | {both_flip.mean():10.4f}")
    dis = vST != vTS
    if contested.any() and (~contested).any():
        print(f"{'':>10}   dis-rate inside contested: {dis[contested].mean():.3f}   "
              f"outside: {dis[~contested].mean():.3f}   recall: {dis[contested].sum()/max(dis.sum(),1):.2f}")
