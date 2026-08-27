"""Contextuality-by-Default test on the euh order experiment (ledger-only).

Everything measured so far establishes ORDER DEPENDENCE: the composite differs when the two
passes are swapped. That is non-commutativity, and it is not in dispute. Contextuality is a
strictly stronger and logically separate property, and none of the sealed hypotheses test it.
This script does.

The distinction. Order dependence means each pass's outcome distribution shifts depending on
what came before -- in the Contextuality-by-Default (CbD) vocabulary, a *direct influence*
(the system is "inconsistently connected"). Contextuality is what remains when direct
influences are subtracted: it holds when NO joint distribution over all outcomes exists that
reproduces every context's observed joint while coupling each content across contexts as
closely as its own marginals allow. Survey question-order effects are the classic case where
large order effects turn out to be direct influences with no contextuality on top
(Dzhafarov, Zhang & Kujala 2015), so this is the live possibility, not a formality.

The system. Two contents -- q1 = "the S pass's verdict", q2 = "the T pass's verdict" -- each
measured in two contexts:

    context c1 (order S->T):   R_S = verdict after S,        R_T = verdict after S then T
    context c2 (order T->S):   R_T = verdict after T,        R_S = verdict after T then S

That is a cyclic system of rank 2. Verdicts are dichotomised against a target label t
(R = +1 if the verdict is t, else -1), and the test is run for each t in {E, U, H}.

The criterion. For a cyclic system of rank n, CbD gives noncontextuality iff

    s_odd(<R_i R_j>) <= n - 2 + Delta_0,     Delta_0 = sum_i |<R_i^c> - <R_i^c'>|

For n = 2 this reduces to

    CNTX = | <R_S R_T>_c1 - <R_S R_T>_c2 |  -  ( |<R_S>_c1 - <R_S>_c2| + |<R_T>_c1 - <R_T>_c2| )

CNTX > 0 means contextual: the change in the two-way correlation between orders is larger than
the change in the individual marginals can account for. CNTX <= 0 means the order effect is
direct influence only -- real, possibly large, but classically explicable by a hidden variable
plus context-dependent marginals.

Because CNTX is a difference of sampling estimates it is noisy, so the script reports a
replicate-based floor: the same statistic computed with a same-order replicate substituted for
one composite, which contains no order contrast at all and whose CNTX should sit at chance.

    python cbd_contextuality.py <battery_dir> [stage ...] [--boot 400]
"""
import argparse
import json
import os

import numpy as np

LAB = ["E", "U", "H"]


def dich(v, t):
    """+1 where the verdict is the target label, -1 elsewhere."""
    return np.where(v == t, 1.0, -1.0)


def cntx(vS_c1, vT_c1, vT_c2, vS_c2, t):
    """CbD rank-2 contextuality measure for target label t. >0 means contextual."""
    a1, b1 = dich(vS_c1, t), dich(vT_c1, t)
    b2, a2 = dich(vT_c2, t), dich(vS_c2, t)
    corr = abs(float((a1 * b1).mean()) - float((a2 * b2).mean()))
    d0 = abs(float(a1.mean()) - float(a2.mean())) + abs(float(b1.mean()) - float(b2.mean()))
    return corr - d0, corr, d0


def boot_ci(vS_c1, vT_c1, vT_c2, vS_c2, t, boot, rng):
    n = len(vS_c1)
    vals = []
    for _ in range(boot):
        i = rng.integers(0, n, n)
        vals.append(cntx(vS_c1[i], vT_c1[i], vT_c2[i], vS_c2[i], t)[0])
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("battery")
    ap.add_argument("stages", nargs="*", default=None)
    ap.add_argument("--boot", type=int, default=400)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    stages = a.stages or ["power_treat", "power_nullswap"]

    for st in stages:
        p = os.path.join(a.battery, st, "ledger.json")
        if not os.path.exists(p):
            print(f"=== {st}: no ledger.json")
            continue
        L = json.load(open(p, encoding="utf-8"))
        print(f"\n=== {st}   (CNTX > 0 would mean contextual; CbD rank-2)")
        print(f"  {'cell':11} {'t':2} {'|dCorr|':>8} {'Delta0':>8} {'CNTX':>9} {'95% CI':>20} "
              f"{'noise CNTX':>11}")
        any_pos = []
        for key in sorted(L["cells"]):
            c = L["cells"][key]
            v = {k: np.array(c["P"][k]).argmax(1) for k in ("S", "T", "ST", "TS")}
            vS_c1, vT_c1 = np.array(LAB)[v["S"]], np.array(LAB)[v["ST"]]
            vT_c2, vS_c2 = np.array(LAB)[v["T"]], np.array(LAB)[v["TS"]]
            reps = {k: [np.array(LAB)[np.array(x).argmax(1)] for x in c["replicates"].get(k, [])]
                    for k in ("ST", "TS")}
            for t in LAB:
                val, corr, d0 = cntx(vS_c1, vT_c1, vT_c2, vS_c2, t)
                rng = np.random.default_rng(a.seed)
                lo, hi = boot_ci(vS_c1, vT_c1, vT_c2, vS_c2, t, a.boot, rng)
                # floor: replace the c2 composite with a same-order replicate of c1, so the two
                # "contexts" differ by run noise alone and carry no order contrast
                nz = []
                for r in reps["ST"]:
                    nz.append(cntx(vS_c1, vT_c1, vT_c2, r, t)[0])
                nzs = f"{np.median(nz):+.4f}" if nz else "n/a"
                flag = "  <-- CONTEXTUAL" if lo > 0 else ""
                print(f"  {key:11} {t:2} {corr:8.4f} {d0:8.4f} {val:+9.4f} "
                      f"[{lo:+.4f},{hi:+.4f}] {nzs:>11}{flag}")
                any_pos.append(lo > 0)
        n = len(any_pos)
        print(f"  -> {sum(any_pos)}/{n} cell x label tests with CNTX significantly > 0")
        if not any(any_pos):
            print("     No contextuality: every order effect here is accounted for by direct")
            print("     influences (context-dependent marginals), i.e. a classical hidden-variable")
            print("     model with order-dependent readouts reproduces the data.")


if __name__ == "__main__":
    main()
