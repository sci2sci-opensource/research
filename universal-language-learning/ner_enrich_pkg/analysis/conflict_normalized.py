"""Conflict-normalised order effect: comparing the treatment and null-swap arms fairly.

POST-HOC (2026-08-17). The sealed rule for the control battery is N6 in hypotheses.py; this
script does not replace it, it interprets it.

The problem N6 runs into. The null-swap arm adds two arbitrary halves of ORG, partitioned by a
hash of the entity surface form. Nothing semantically distinguishes the halves, so the model
cannot tell which half an unseen entity belongs to and both enrichments claim the same tokens:
the sealed claims null predicts a conflict rate of ~0.036 for the control against ~0.010 for the
ORG/MISC treatment, a 3.7x difference, with overlap ratios of ~19 against ~5.8. Order is decided
precisely on contested tokens (the second pass writes last), so the control is structurally
predisposed to a larger order effect regardless of whether "the two distinctions differ" matters.
A bare N6 = H would therefore mostly restate that asymmetry.

The normalisation. Each arm carries its own sealed prediction of how much order disagreement its
conflict structure implies (`prediction.claims.pred_disagreement`, written before any composite
was trained). Dividing the observed order effect by that per-arm prediction removes the conflict
asymmetry and asks the question N6 was meant to ask:

    does an arm show MORE order dependence than its own conflict structure already predicts,
    and does the treatment exceed its prediction by more than the control exceeds its own?

If the ratios match, the control's larger raw effect is fully explained by having more contested
tokens, and the identity of the added distinctions contributes nothing beyond that. If the
treatment's ratio is higher, the distinctions matter beyond conflict structure.

    python conflict_normalized.py <battery_dir>
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def names(P, lab):
    return np.array(lab)[np.asarray(P).argmax(1)]


def arm_stats(L, boot=300, seed=0):
    """Per-cell observed order effect, its own sealed conflict prediction, and their ratio."""
    gold = np.array(L["gold"])
    out = []
    for key, c in sorted(L["cells"].items()):
        lab = c["labels"]
        AB = [names(c["P"]["AB"], lab["AB"])] + [names(r[0], r[1]) for r in c["replicates"].get("AB", [])]
        BA = [names(c["P"]["BA"], lab["BA"])] + [names(r[0], r[1]) for r in c["replicates"].get("BA", [])]
        if len(AB) < 2 or len(BA) < 2:
            continue
        ent = (gold != "O") | (AB[0] != "O") | (BA[0] != "O")
        W = np.array([(a != b)[ent] for R in (AB, BA) for i, a in enumerate(R) for b in R[i + 1:]])
        C = np.array([(a != b)[ent] for a in AB for b in BA])
        n = W.shape[1]
        rng = np.random.default_rng(seed)
        ex = [float(C[:, i].mean() - W[:, i].mean()) for i in (rng.integers(0, n, n) for _ in range(boot))]
        lo, hi = np.percentile(ex, [2.5, 97.5])
        w, cr = float(W.mean()), float(C.mean())
        excess = cr - w                                   # order effect above run noise
        pred = float(c["prediction"]["claims"]["pred_disagreement"])   # sealed, per arm
        # the sealed prediction is over all tokens; put it on the entity-matched footing
        scale = float(ent.mean())
        pred_ent = pred / max(scale, 1e-9)
        out.append(dict(cell=key, within=w, cross=cr, excess=excess, lo=float(lo), hi=float(hi),
                        sys=excess / max(cr, 1e-9), pred_conflict=pred_ent,
                        normalised=excess / max(pred_ent, 1e-9)))
    return out


def main():
    B = sys.argv[1]
    arms = {}
    for st in sorted(os.listdir(B)):
        p = os.path.join(B, st, "ledger.json")
        if os.path.exists(p):
            arms[st] = arm_stats(json.load(open(p, encoding="utf-8")))

    print(f"{'arm':16} {'within':>8} {'cross':>8} {'excess':>8} {'sys%':>6} "
          f"{'pred confl':>11} {'excess/pred':>12}")
    med = {}
    for st, rows in arms.items():
        if not rows:
            continue
        m = {k: float(np.median([r[k] for r in rows]))
             for k in ("within", "cross", "excess", "sys", "pred_conflict", "normalised")}
        med[st] = m
        print(f"{st:16} {m['within']:8.4f} {m['cross']:8.4f} {m['excess']:8.4f} "
              f"{m['sys']:6.1%} {m['pred_conflict']:11.4f} {m['normalised']:12.2f}")

    t = next((s for s in med if s.endswith("ctrl_treat")), None)
    z = next((s for s in med if s.endswith("ctrl_nullswap")), None)
    if t and z:
        print(f"\nRaw comparison (what N6 scores):")
        print(f"  systematic share      treatment {med[t]['sys']:.1%}   null-swap {med[z]['sys']:.1%}")
        print(f"  -> the control contests {med[z]['pred_conflict'] / max(med[t]['pred_conflict'], 1e-9):.1f}x "
              f"more tokens, so this comparison is not like-for-like")
        r = med[t]["normalised"] / max(med[z]["normalised"], 1e-9)
        print(f"\nConflict-normalised (each arm against its own sealed prediction):")
        print(f"  excess / predicted    treatment {med[t]['normalised']:.2f}   null-swap {med[z]['normalised']:.2f}"
              f"   ratio {r:.2f}")
        if r >= 1.5:
            print("  -> the treatment exceeds its own conflict structure by more than the control does:")
            print("     the identity of the added distinctions matters beyond how much they contest.")
        elif r <= 0.8:
            print("  -> the control exceeds its own conflict structure by MORE than the treatment does;")
            print("     no evidence that distinct distinctions add order dependence.")
        else:
            print("  -> the two arms exceed their own predictions by the same factor: the control's")
            print("     larger raw effect is accounted for by its larger conflict set, and the identity")
            print("     of the added distinctions adds nothing detectable on top.")


if __name__ == "__main__":
    main()
