"""Margin-stratified lumpability with a null that can fail (lab notes; ledger-only).

H3/H11 ask whether the verdict alphabet {E,U,H} is a closed description: predict the
composite's base->XY transition matrix as the product of the two single-pass channels
(Phi_S Phi_T) and test the observed transitions against it.  This script changes two
things about how that question is asked.

1.  A null that can actually fail.  H11 calibrates the observed chi2 against the SAME
    chi2 with a same-order *replicate* substituted for the observed composite.  The
    replicate is another run of the same composite, so it carries the same systematic
    non-lumpability as the observation; the two are exchangeable and the ratio sits at
    ~1 whether or not the lumpable model is wrong.  H11 therefore cannot return E
    except by fluctuation, and its H verdict does not license "non-lumpability is at
    noise level".  The null used here is a parametric bootstrap *under* the lumpable
    model: resample items, re-estimate both channels on the resample (so channel
    estimation error is inside the null), draw each item's composite verdict from
    M[v_base(item)], recompute chi2.  That is what chi2 looks like when lumpability
    holds exactly, at this n, with these estimates.

2.  Stratification by base margin.  One 3x3 applied to every item asserts that all
    items sharing a verdict move alike.  That is false here -- base top-2 margin
    predicts flips with AUC ~0.89 -- so the pooled test is guaranteed to reject on
    item heterogeneity alone, independently of any order or context effect.
    Estimating the channels within margin strata removes that heterogeneity.  If the
    excess over the null collapses under stratification, the pooled non-lumpability
    was heterogeneity; if it survives, that residual is the part worth calling
    structure.

Both statistics are reported as excess over their own null (obs / median null), so the
pooled and stratified numbers are comparable even though stratifying changes df and n.

    python stratified_lumpability.py <battery_dir> [stage ...] [--bins 4] [--boot 200]
    # gunzip <stage>/ledger.json.gz first if reading a packaged battery
"""
import argparse
import json
import os

import numpy as np

K = 3


def channel(vf, vt):
    """Row-stochastic 3x3 with the package's +0.5 smoothing."""
    N = np.zeros((K, K))
    np.add.at(N, (vf, vt), 1.0)
    N += 0.5
    return N / N.sum(1, keepdims=True)


def chi2_lump(vb, vc, M):
    """Same statistic as euh.stats.lumpability_chi2 (rows with <5 items skipped)."""
    N = np.zeros((K, K))
    np.add.at(N, (vb, vc), 1.0)
    chi = 0.0
    for i in range(K):
        n = N[i].sum()
        if n < 5:
            continue
        e = n * M[i]
        chi += float(((N[i] - e) ** 2 / np.maximum(e, 1e-9)).sum())
    return chi


def compose(vb, vS, vT, order):
    Ps, Pt = channel(vb, vS), channel(vb, vT)
    return Ps @ Pt if order == "ST" else Pt @ Ps


def draw(M_rows, rng):
    """One categorical draw per row of an (n,3) probability matrix."""
    c = M_rows.cumsum(1)
    return (rng.random((len(M_rows), 1)) > c).sum(1)


def stat(vb, vS, vT, vc, order, sid=None, nb=0):
    """chi2 of the observed composite against the composed channels; summed over strata."""
    if sid is None:
        return chi2_lump(vb, vc, compose(vb, vS, vT, order))
    tot = 0.0
    for b in range(nb):
        m = sid == b
        if m.sum() < 10:
            continue
        tot += chi2_lump(vb[m], vc[m], compose(vb[m], vS[m], vT[m], order))
    return tot


def null_dist(vb, vS, vT, order, rng, boot, sid=None, nb=0):
    """chi2 under the lumpable model: resample items, re-estimate channels, simulate."""
    n, out = len(vb), []
    for _ in range(boot):
        i = rng.integers(0, n, n)
        b_, s_, t_ = vb[i], vS[i], vT[i]
        g_ = sid[i] if sid is not None else None
        vc = np.empty(n, dtype=int)
        if sid is None:
            vc = draw(compose(b_, s_, t_, order)[b_], rng)
        else:
            for bn in range(nb):
                m = g_ == bn
                if m.sum() < 10:
                    vc[m] = b_[m]
                    continue
                vc[m] = draw(compose(b_[m], s_[m], t_[m], order)[b_[m]], rng)
        out.append(stat(b_, s_, t_, vc, order, g_, nb))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("battery")
    ap.add_argument("stages", nargs="*", default=None)
    ap.add_argument("--bins", type=int, default=4, help="base-margin quantile strata")
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--shuffle-strata", action="store_true",
                    help="control: permute the stratum labels, so the strata carry the same "
                         "sizes and count but no information about the margin. If the excess "
                         "falls here too, stratification is shrinking chi2 mechanically rather "
                         "than because margin is the covariate that explains it.")
    a = ap.parse_args()
    stages = a.stages or ["base_shared", "base_strength"]

    for st in stages:
        path = os.path.join(a.battery, st, "ledger.json")
        if not os.path.exists(path):
            print(f"=== {st}: no ledger.json (gunzip the packaged one first)")
            continue
        L = json.load(open(path, encoding="utf-8"))
        Pb = np.array(L["base"])
        vb = Pb.argmax(1)
        srt = np.sort(Pb, 1)
        margin = srt[:, -1] - srt[:, -2]
        edges = np.quantile(margin, np.linspace(0, 1, a.bins + 1)[1:-1])
        sid = np.digitize(margin, edges)
        if a.shuffle_strata:
            sid = np.random.default_rng(a.seed + 991).permutation(sid)

        label = "SHUFFLED (control)" if a.shuffle_strata else "margin"
        print(f"\n=== {st}   ({a.bins} {label} strata, {a.boot} bootstrap draws under lumpability)")
        print("  cell        order |  pooled chi2 / null   |  stratified chi2 / null |  H11 ratio")
        print("  " + "-" * 76)
        rows = []
        for key in sorted(L["cells"]):
            c = L["cells"][key]
            vS, vT = np.array(c["P"]["S"]).argmax(1), np.array(c["P"]["T"]).argmax(1)
            for order in ("ST", "TS"):
                rng = np.random.default_rng(a.seed)
                vc = np.array(c["P"][order]).argmax(1)

                o_p = stat(vb, vS, vT, vc, order)
                n_p = null_dist(vb, vS, vT, order, rng, a.boot)
                o_s = stat(vb, vS, vT, vc, order, sid, a.bins)
                n_s = null_dist(vb, vS, vT, order, rng, a.boot, sid, a.bins)

                r_p = o_p / max(float(np.median(n_p)), 1e-9)
                r_s = o_s / max(float(np.median(n_s)), 1e-9)
                p_p = float(np.mean(n_p >= o_p))
                p_s = float(np.mean(n_s >= o_s))

                # H11's own statistic, for comparison: replicate substituted for observed
                M = compose(vb, vS, vT, order)
                reps = [np.array(p).argmax(1) for p in c["replicates"].get(order, [])]
                h11 = (o_p / max(float(np.median([chi2_lump(vb, vr, M) for vr in reps])), 1e-9)
                       if reps else np.nan)

                print(f"  {key:11} {order:5} | {o_p:8.1f} /{np.median(n_p):7.1f} = {r_p:5.2f}x"
                      f" p={p_p:.3f} | {o_s:8.1f} /{np.median(n_s):7.1f} = {r_s:5.2f}x p={p_s:.3f}"
                      f" | {h11:5.2f}x")
                rows.append((r_p, r_s, h11))

        R = np.array(rows, dtype=float)
        print("  " + "-" * 76)
        print(f"  median over {len(R)} cell-orders:  pooled {np.median(R[:,0]):.2f}x   "
              f"stratified {np.median(R[:,1]):.2f}x   H11 {np.nanmedian(R[:,2]):.2f}x")
        drop = 1 - (np.median(R[:, 1]) - 1) / max(np.median(R[:, 0]) - 1, 1e-9)
        print(f"  excess over null removed by margin stratification: {drop:.0%}")


if __name__ == "__main__":
    main()
