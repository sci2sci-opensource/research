"""Ledger-only algebra observables (lab notes §3): geometry race, instrument deficiency,
channel-commutator null.

1. GEOMETRY RACE: fit per-geometry affine channels base->S and base->T, compose both orders,
   score per-item verdict agreement with observed composites. Geometries: probability simplex
   (linear), ALR (log), Hellinger (sqrt amplitudes).
2. INSTRUMENT DEFICIENCY: verdict channel for T fitted at base vs fitted in context S,
   Frobenius distance over an item-bootstrap fit-noise floor.
3. COMMUTATOR NULL: ||[Phi_S, Phi_T]|| z-scored against its item-bootstrap null.

    python algebra_observables.py <battery_dir> [stage ...]
    # gunzip <stage>/ledger.json.gz first
"""
import json, os, sys
import numpy as np

B = sys.argv[1]
stages = sys.argv[2:] or ["base_strength", "base_shared"]
rng = np.random.default_rng(0)

def verd(P): return np.asarray(P).argmax(1)

def channel(vf, vt, k=3):
    N = np.zeros((k, k))
    for a, b in zip(vf, vt): N[a, b] += 1
    N += 0.5
    return N / N.sum(1, keepdims=True)

def fit_affine(X, Y):
    Xa = np.hstack([X, np.ones((len(X), 1))])
    W, *_ = np.linalg.lstsq(Xa, Y, rcond=None)
    return W

def apply_aff(X, W): return np.hstack([X, np.ones((len(X), 1))]) @ W

def to_geom(P, g):
    P = np.clip(np.asarray(P, float), 1e-6, 1)
    if g == "prob": return P
    if g == "alr":  return np.log(P[:, [0, 2]] / P[:, [1]])
    if g == "sqrt": return np.sqrt(P)

def from_geom(X, g):
    if g == "prob":
        P = np.clip(X, 1e-9, None); return P / P.sum(1, keepdims=True)
    if g == "alr":
        Z = np.c_[X[:, 0], np.zeros(len(X)), X[:, 1]]; Z = np.exp(Z - Z.max(1, keepdims=True))
        return Z / Z.sum(1, keepdims=True)
    if g == "sqrt":
        A = np.clip(X, 1e-9, None) ** 2; return A / A.sum(1, keepdims=True)

for st in stages:
    L = json.load(open(os.path.join(B, st, "ledger.json")))
    Pb = np.array(L["base"]); vb = verd(Pb)
    geo = {g: [] for g in ("prob", "alr", "sqrt")}
    rows_def, rows_comm = {}, {}
    wins = {"sqrt>prob": 0, "sqrt>alr": 0, "n": 0}
    for key, c in sorted(L["cells"].items()):
        PS, PT = np.array(c["P"]["S"]), np.array(c["P"]["T"])
        vS, vT = verd(PS), verd(PT)
        vST, vTS = verd(np.array(c["P"]["ST"])), verd(np.array(c["P"]["TS"]))
        acc = {}
        for g in geo:
            Xb = to_geom(Pb, g)
            WS = fit_affine(Xb, to_geom(PS, g)); WT = fit_affine(Xb, to_geom(PT, g))
            pST = verd(from_geom(apply_aff(apply_aff(Xb, WS), WT), g))
            pTS = verd(from_geom(apply_aff(apply_aff(Xb, WT), WS), g))
            acc[g] = 0.5 * ((pST == vST).mean() + (pTS == vTS).mean())
            geo[g].append(acc[g])
        wins["n"] += 1
        wins["sqrt>prob"] += acc["sqrt"] > acc["prob"]; wins["sqrt>alr"] += acc["sqrt"] > acc["alr"]
        PhiT_base = channel(vb, vT); PhiT_ctxS = channel(vS, vST)
        d_obs = float(np.linalg.norm(PhiT_base - PhiT_ctxS))
        n = len(vb); dn = []
        for _ in range(60):
            i = rng.integers(0, n, n); j = rng.integers(0, n, n)
            dn.append(np.linalg.norm(channel(vb[i], vT[i]) - channel(vb[j], vT[j])))
        rows_def.setdefault(c["alpha"], []).append(d_obs / max(np.mean(dn), 1e-9))
        PhiS = channel(vb, vS)
        c_obs = float(np.linalg.norm(PhiS @ PhiT_base - PhiT_base @ PhiS))
        cn = []
        for _ in range(60):
            i = rng.integers(0, n, n)
            A, Bm = channel(vb[i], vS[i]), channel(vb[i], vT[i])
            cn.append(np.linalg.norm(A @ Bm - Bm @ A))
        rows_comm.setdefault(c["alpha"], []).append((c_obs - np.mean(cn)) / max(np.std(cn), 1e-9))
    print("===", st)
    print("  geometry race (mean per-item agreement of composed channel with observed composite):")
    for g, s in geo.items():
        print(f"    {g:5}: {np.mean(s):.4f}")
    print(f"  per-cell wins: {wins}")
    print("  instrument deficiency Phi_T(base) vs Phi_T(ctx S), ratio over bootstrap fit noise:")
    for a in sorted(rows_def): print(f"    a={a}: {np.mean(rows_def[a]):.1f}x")
    print("  commutator z-score vs item-bootstrap null:")
    for a in sorted(rows_comm): print(f"    a={a}: z={np.mean(rows_comm[a]):+.1f}")
