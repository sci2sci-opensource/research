"""Sealed hypothesis ledger for the enrichment-order experiment.

Sealed 2026-08-17, before the battery evaluating it was run (committed and pushed prior to
launch; the git timestamp is the external pre-registration). All floors are ENTITY-MATCHED:
numerator and denominator are computed on the same entity-relevant token set, per the
2026-08-17 audit of the earlier unit mismatch.

    python hypotheses.py <battery_dir>          # writes <battery_dir>/hypotheses.json
"""
import itertools, json, os, sys
import numpy as np

KEEP = ["O", "PER", "LOC"]


def names(P, lab):
    return np.array(lab)[np.asarray(P).argmax(1)]


def cell_ratios(L):
    """Per-cell (entity-matched order/floor, entity-matched retracted order/floor)."""
    gold = np.array(L["gold"]); out = []
    for key, c in sorted(L["cells"].items()):
        vAB = names(c["P"]["AB"], c["labels"]["AB"]); vBA = names(c["P"]["BA"], c["labels"]["BA"])
        ent = (gold != "O") | (vAB != "O") | (vBA != "O")
        dis = float((vAB != vBA)[ent].mean())
        fl, fo = [], []
        rAB = np.where(np.isin(vAB, KEEP), vAB, "O"); rBA = np.where(np.isin(vBA, KEEP), vBA, "O")
        dis_old = float((rAB != rBA)[ent].mean())
        for order, vmain, vmain0 in (("AB", vAB, rAB), ("BA", vBA, rBA)):
            for rp, rl in c["replicates"].get(order, []):
                vr = names(rp, rl)
                e2 = ent | (vr != "O")
                fl.append(float((vmain != vr)[e2].mean()))
                vr0 = np.where(np.isin(vr, KEEP), vr, "O")
                fo.append(float((vmain0 != vr0)[ent].mean()))
        if not fl: continue
        out.append(dict(cell=key, ratio=dis / max(np.mean(fl), 1e-9),
                        ratio_old=dis_old / max(np.mean(fo), 1e-9),
                        recall=c["score"]["pred_err"]["claims"].get("conflict_recall"),
                        enrich=(c["score"]["pred_err"]["claims"].get("dis_in_conflict") or 0)
                               / max(c["score"]["pred_err"]["claims"].get("dis_outside_conflict") or 1e-9, 1e-9)))
    return out


def N1(rows):
    """Entity-matched order effect >= 2x floor in >= 2/3 of cells."""
    r = [x["ratio"] for x in rows]
    if len(r) < 3: return "U", "fewer than 3 cells with floors", {}
    ev = dict(median=float(np.median(r)), frac_ge2=float(np.mean(np.array(r) >= 2)), n=len(r))
    if ev["frac_ge2"] >= 2 / 3: return "E", f"entity-matched order disagreement ≥2× floor in {ev['frac_ge2']:.0%} of cells (median {ev['median']:.2f}×)", ev
    if ev["median"] <= 1.2: return "H", f"at noise level (median {ev['median']:.2f}×)", ev
    return "U", f"median {ev['median']:.2f}×", ev


def N2(rows):
    """Old-language conservativity: retracted order effect stays under 2x in EVERY cell."""
    r = [x["ratio_old"] for x in rows]
    if len(r) < 3: return "U", "fewer than 3 cells", {}
    ev = dict(median=float(np.median(r)), frac_ge2=float(np.mean(np.array(r) >= 2)), n=len(r))
    if ev["frac_ge2"] == 0 and ev["median"] <= 1.5: return "E", f"retracted order effect below the 2× bar in every cell (median {ev['median']:.2f}×)", ev
    if ev["frac_ge2"] >= 1 / 3: return "H", f"retracted order effect ≥2× floor in {ev['frac_ge2']:.0%} of cells", ev
    return "U", f"median {ev['median']:.2f}×, {ev['frac_ge2']:.0%} of cells ≥2×", ev


def N3(rows):
    """Conflict-set localization: >= 10x enrichment in >= 2/3 of cells (localizes, need not account)."""
    e = [x["enrich"] for x in rows if x["enrich"] is not None and np.isfinite(x["enrich"])]
    if len(e) < 3: return "U", "fewer than 3 cells", {}
    ev = dict(median=float(np.median(e)), frac_ge10=float(np.mean(np.array(e) >= 10)),
              median_recall=float(np.median([x["recall"] for x in rows if x["recall"] is not None])))
    if ev["frac_ge10"] >= 2 / 3: return "E", f"conflict-set enrichment ≥10× in {ev['frac_ge10']:.0%} of cells (median {ev['median']:.0f}×; captures median {ev['median_recall']:.0%} of disagreement)", ev
    if ev["median"] <= 2: return "H", f"conflict set barely enriched (median {ev['median']:.1f}×)", ev
    return "U", f"median enrichment {ev['median']:.1f}×", ev


def N4(L):
    """Improvement-verdict flips exceed the replicate-null flip rate (which is ~0 by anti-correlation)."""
    gold = np.array(L["gold"]); gold0 = np.where(np.isin(gold, KEEP), gold, "O")
    T = 0.002

    def errs(P, lab):
        v = names(P, lab); v0 = np.where(np.isin(v, KEEP), v, "O")
        return float((v != gold).mean()), float((v0 != gold0).mean())

    null_flips = null_pairs = obs = checks = 0
    for key, c in L["cells"].items():
        for order in ("AB", "BA"):
            E = [errs(c["P"][order], c["labels"][order])] + [errs(rp, rl) for rp, rl in c["replicates"].get(order, [])]
            for i, j in itertools.permutations(range(len(E)), 2):
                d1 = E[j][0] - E[i][0]; d0 = E[j][1] - E[i][1]
                null_pairs += 1
                if (d1 < -T and d0 > T) or (d0 < -T and d1 > T): null_flips += 1
        imp = c["score"]["improvement"]
        for pair in (("base", "A"), ("base", "B"), ("A", "AB"), ("B", "BA"), ("base", "AB"), ("base", "BA")):
            d1 = imp[pair[1]]["err_R1"] - imp[pair[0]]["err_R1"]; d0 = imp[pair[1]]["err_R0"] - imp[pair[0]]["err_R0"]
            checks += 1
            if (d1 < -T and d0 > T) or (d0 < -T and d1 > T): obs += 1
    rate = null_flips / max(null_pairs, 1); expect = rate * checks
    ev = dict(observed=obs, checks=checks, null_rate=rate, expected_false=expect)
    if obs >= 10 and obs >= 10 * max(expect, 0.5): return "E", f"{obs}/{checks} flip signatures vs {expect:.1f} expected from replicate noise", ev
    if obs <= max(expect, 1): return "H", f"{obs} flips, consistent with noise ({expect:.1f} expected)", ev
    return "U", f"{obs} flips vs {expect:.1f} expected", ev


def N5(rows_kl, rows_zero):
    """Anchor causality: without the KL anchor, retracted order effect rises >= 1.5x vs anchored."""
    if not rows_kl or not rows_zero: return "U", "needs both the anchored and the β=0 stage", {}
    mk = float(np.median([x["ratio_old"] for x in rows_kl])); mz = float(np.median([x["ratio_old"] for x in rows_zero]))
    ev = dict(anchored_median=mk, unanchored_median=mz, ratio=mz / max(mk, 1e-9))
    if ev["ratio"] >= 1.5: return "E", f"removing the anchor raises retracted order effect {ev['ratio']:.1f}× ({mk:.2f}→{mz:.2f})", ev
    if ev["ratio"] <= 1.1: return "H", f"β=0 barely changes retracted order effect ({mk:.2f}→{mz:.2f}) — anchor not the cause", ev
    return "U", f"{mk:.2f}→{mz:.2f} ({ev['ratio']:.1f}×)", ev


def pair_decomp(L, boot=300, seed=0):
    """Per-cell split of entity-matched composite disagreement into within-order and cross-order.

    within = mean pairwise disagreement among runs of the SAME order (run noise)
    cross  = mean pairwise disagreement between runs of DIFFERENT orders (noise + order)
    sys    = (cross - within) / cross, the systematic share, with a bootstrap over tokens

    Uses every run of each order (recorded composite + replicates), so the estimate rests on
    m(m-1) within-order and m^2 cross-order pairs instead of one of each. The ratio is
    m-independent in expectation, so more replicates sharpen it without inflating it.
    """
    gold = np.array(L["gold"]); out = []
    for key, c in sorted(L["cells"].items()):
        lab = c["labels"]
        AB = [names(c["P"]["AB"], lab["AB"])] + [names(r[0], r[1]) for r in c["replicates"].get("AB", [])]
        BA = [names(c["P"]["BA"], lab["BA"])] + [names(r[0], r[1]) for r in c["replicates"].get("BA", [])]
        if len(AB) < 2 or len(BA) < 2: continue
        ent = (gold != "O") | (AB[0] != "O") | (BA[0] != "O")
        W = np.array([(a != b)[ent] for R in (AB, BA) for i, a in enumerate(R) for b in R[i + 1:]])
        C = np.array([(a != b)[ent] for a in AB for b in BA])
        n = W.shape[1]; rng = np.random.default_rng(seed)
        ex = [float(C[:, i].mean() - W[:, i].mean()) for i in (rng.integers(0, n, n) for _ in range(boot))]
        lo, hi = np.percentile(ex, [2.5, 97.5])
        w, cr = float(W.mean()), float(C.mean())
        out.append(dict(cell=key, within=w, cross=cr, ratio=cr / max(w, 1e-9),
                        sys=(cr - w) / max(cr, 1e-9), lo=float(lo), hi=float(hi)))
    return out


def N6(rows_treat, rows_null):
    """Does the enrichment order effect need the two added distinctions to be DIFFERENT?

    Sealed 2026-08-17 before the control battery was launched. The treatment adds ORG and MISC;
    the matched control adds two arbitrary halves of ORG (entity-partitioned, so they are
    consistent and mutually exclusive) with everything else identical. euh's analogous control
    returned H — its order effect survived replacing the second operator with a second instance
    of the first — so this is the same question asked where the project's positive result lives.
    """
    if len(rows_treat) < 3 or len(rows_null) < 3:
        return "U", "needs both ctrl_treat and ctrl_nullswap with >=3 cells", {}
    st = float(np.median([r["sys"] for r in rows_treat])); sz = float(np.median([r["sys"] for r in rows_null]))
    ev = dict(treat_sys=st, nullswap_sys=sz, ratio=st / max(sz, 1e-9),
              treat_ratio=float(np.median([r["ratio"] for r in rows_treat])),
              nullswap_ratio=float(np.median([r["ratio"] for r in rows_null])),
              treat_ci_above_0=float(np.mean([r["lo"] > 0 for r in rows_treat])),
              nullswap_ci_above_0=float(np.mean([r["lo"] > 0 for r in rows_null])))
    if st >= 2 * max(sz, 1e-9) and ev["treat_ci_above_0"] >= 2 / 3:
        return "E", (f"distinct distinctions matter: treatment {st:.0%} vs matched null-swap {sz:.0%} "
                     f"systematic ({ev['ratio']:.1f}×)"), ev
    if st <= sz:
        return "H", (f"null swap shows as much order effect as two distinct enrichments "
                     f"({sz:.0%} vs {st:.0%} systematic) — the effect does not need them to differ"), ev
    return "U", f"treatment {st:.0%} vs null-swap {sz:.0%} systematic — under the 2× bar", ev


def main():
    B = sys.argv[1]
    ledgers = {}
    for st in sorted(os.listdir(B)):
        p = os.path.join(B, st, "ledger.json")
        if os.path.exists(p):
            ledgers[st] = json.load(open(p))
    out = {}
    rows = {st: cell_ratios(L) for st, L in ledgers.items()}
    for st, L in ledgers.items():
        out[st] = {
            "N1_entity_matched_order_effect": N1(rows[st]),
            "N2_old_language_conservativity": N2(rows[st]),
            "N3_conflict_localization": N3(rows[st]),
            "N4_improvement_flips": N4(L),
            "cells": rows[st],
        }
    kl = next((s for s in rows if s == "base_strength"), None)
    z = next((s for s in rows if "klzero" in s), None)
    out["N5_anchor_causality"] = N5(rows.get(kl, []), rows.get(z, []))

    t_st = next((s for s in ledgers if s.endswith("ctrl_treat")), None)
    n_st = next((s for s in ledgers if s.endswith("ctrl_nullswap")), None)
    if t_st and n_st:
        dt, dn = pair_decomp(ledgers[t_st]), pair_decomp(ledgers[n_st])
        out["N6_distinctions_must_differ"] = N6(dt, dn)
        out["N6_cells"] = dict(ctrl_treat=dt, ctrl_nullswap=dn)

    for st, d in out.items():
        if st in ("N5_anchor_causality", "N6_distinctions_must_differ"):
            print(f"{st.split('_')[0]} -> {d[0]} | {d[1]}"); continue
        if st == "N6_cells": continue
        print(f"== {st}")
        for k, v in d.items():
            if k != "cells": print(f"  {k} -> {v[0]} | {v[1]}")
    json.dump(out, open(os.path.join(B, "hypotheses.json"), "w"), indent=1)
    print("written", os.path.join(B, "hypotheses.json"))


if __name__ == "__main__":
    main()
