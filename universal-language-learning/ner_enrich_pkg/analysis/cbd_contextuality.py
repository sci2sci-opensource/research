"""Contextuality-by-Default test on the enrichment-order experiment (ledger-only).

Companion to euh_pkg/analysis/cbd_contextuality.py; see that file for the full statement of the
criterion. In brief: order dependence means each pass's outcomes shift with what preceded it,
which in CbD terms is a *direct influence*. Contextuality is the stronger property that survives
after direct influences are subtracted -- no joint distribution over all outcomes reproduces
every context's joint while coupling each content across contexts as tightly as its marginals
permit. Order effects can be arbitrarily large and still carry no contextuality
(Dzhafarov, Zhang & Kujala 2015 found exactly that for survey question order).

The system here, a cyclic system of rank 2:

    context c1 (order A->B):   R_A = verdict after A,        R_B = verdict after A then B
    context c2 (order B->A):   R_B = verdict after B,        R_A = verdict after B then A

    CNTX = | <R_A R_B>_c1 - <R_A R_B>_c2 | - ( |<R_A>_c1 - <R_A>_c2| + |<R_B>_c1 - <R_B>_c2| )

CNTX > 0 is contextual. Verdicts are dichotomised against each label in turn, and everything is
computed on the entity-matched token set (gold or either composite non-O), the same population
the sealed N1 floor uses, so the test is not diluted by the ~80% of tokens that are trivially O.

    python cbd_contextuality.py <battery_dir> [stage ...] [--boot 400]
"""
import argparse
import json
import os

import numpy as np


def names(P, lab):
    return np.array(lab)[np.asarray(P).argmax(1)]


def cntx(a_c1, b_c1, b_c2, a_c2, t):
    d = lambda v: np.where(v == t, 1.0, -1.0)
    a1, b1, b2, a2 = d(a_c1), d(b_c1), d(b_c2), d(a_c2)
    corr = abs(float((a1 * b1).mean()) - float((a2 * b2).mean()))
    d0 = abs(float(a1.mean()) - float(a2.mean())) + abs(float(b1.mean()) - float(b2.mean()))
    return corr - d0, corr, d0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("battery")
    ap.add_argument("stages", nargs="*", default=None)
    ap.add_argument("--boot", type=int, default=400)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    stages = a.stages or ["ctrl_treat", "ctrl_nullswap"]

    for st in stages:
        p = os.path.join(a.battery, st, "ledger.json")
        if not os.path.exists(p):
            print(f"=== {st}: no ledger.json")
            continue
        L = json.load(open(p, encoding="utf-8"))
        gold = np.array(L["gold"])
        print(f"\n=== {st}   (CNTX > 0 would mean contextual; CbD rank-2, entity-matched)")
        print(f"  {'cell':11} {'t':7} {'|dCorr|':>8} {'Delta0':>8} {'CNTX':>9} {'95% CI':>20}")
        pos = 0, 0
        npos = ntot = 0
        for key in sorted(L["cells"]):
            c = L["cells"][key]
            lab = c["labels"]
            vA, vB = names(c["P"]["A"], lab["A"]), names(c["P"]["B"], lab["B"])
            vAB, vBA = names(c["P"]["AB"], lab["AB"]), names(c["P"]["BA"], lab["BA"])
            ent = (gold != "O") | (vAB != "O") | (vBA != "O")
            a_c1, b_c1, b_c2, a_c2 = vA[ent], vAB[ent], vB[ent], vBA[ent]
            for t in sorted(set(lab["AB"]) | set(lab["BA"])):
                val, corr, d0 = cntx(a_c1, b_c1, b_c2, a_c2, t)
                rng = np.random.default_rng(a.seed)
                n = len(a_c1)
                vals = [cntx(a_c1[i], b_c1[i], b_c2[i], a_c2[i], t)[0]
                        for i in (rng.integers(0, n, n) for _ in range(a.boot))]
                lo, hi = np.percentile(vals, [2.5, 97.5])
                ntot += 1
                flag = ""
                if lo > 0:
                    npos += 1; flag = "  <-- CONTEXTUAL"
                print(f"  {key:11} {t:7} {corr:8.4f} {d0:8.4f} {val:+9.4f} "
                      f"[{lo:+.4f},{hi:+.4f}]{flag}")
        print(f"  -> {npos}/{ntot} cell x label tests with CNTX significantly > 0")


if __name__ == "__main__":
    main()
