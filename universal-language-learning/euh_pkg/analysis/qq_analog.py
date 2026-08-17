"""QQ-equality analog on euh ledgers (lab notes §3; ledger-only, no checkpoints needed).

Quantum question-order models predict the parameter-free identity
P(yes,yes)+P(no,no) is order-invariant (Wang et al., PNAS 2014). Mapping: 'answering
question X' = X's pass leaving its verdict; order S->T gives (v_S, v_ST), order T->S
gives (v_TS, v_T). Reports D per cell with a replicate-substitution noise scale.

    python qq_analog.py <battery_dir> [stage ...]
    # e.g. python qq_analog.py ../results/exp_full_20260815_151503 base_strength base_shared
    # gunzip <stage>/ledger.json.gz first
"""
import json, os, sys
import numpy as np

B = sys.argv[1]
stages = sys.argv[2:] or ["base_strength", "base_shared"]

def v(P): return np.array(P).argmax(1)

def qq(vS, vT, vST, vTS, pos):
    yS_ab, yT_ab = vS == pos, vST == pos
    yT_ba, yS_ba = vT == pos, vTS == pos
    ab = float((yS_ab & yT_ab).mean() + (~yS_ab & ~yT_ab).mean())
    ba = float((yS_ba & yT_ba).mean() + (~yS_ba & ~yT_ba).mean())
    return ab - ba

for st in stages:
    L = json.load(open(os.path.join(B, st, "ledger.json")))
    print("===", st, " (D>0: agreement higher in S->T order; quantum instruments predict D=0)")
    print("  cell        |  D(E)    D(H)   | noise sd(E) | |D|/sd")
    for key, c in sorted(L["cells"].items()):
        vS, vT = v(c["P"]["S"]), v(c["P"]["T"])
        vST, vTS = v(c["P"]["ST"]), v(c["P"]["TS"])
        dE, dH = qq(vS, vT, vST, vTS, 0), qq(vS, vT, vST, vTS, 2)
        noise = [qq(vS, vT, v(rp), vTS, 0) for rp in c["replicates"]["ST"]]
        noise += [qq(vS, vT, vST, v(rp), 0) for rp in c["replicates"]["TS"]]
        sd = float(np.std(noise)) if len(noise) > 1 else np.nan
        print(f"  {key:11} | {dE:+.4f}  {dH:+.4f} |   {sd:.4f}    | {abs(dE)/max(sd,1e-9):5.1f}")
