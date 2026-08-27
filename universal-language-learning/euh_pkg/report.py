"""
Hypothesis ledger + Bayesian update over theories of the composite.

Two layers, in the paper's idiom:

1. HYPOTHESES — pre-registered claims with explicit E/U/H rules.  Each is evaluated per dataset (stage)
   and receives a verdict: E (witnessed under the stated rule), H (refuted), U (the data does not resolve
   the rule — insufficient cells, effect inside the noise floor, or the stage the rule needs is absent).
   U is a definite verdict of non-resolution, not a probability over E/H.

2. THEORIES — competing generative accounts of the composite checkpoint, each supplying a per-item
   predictive distribution over Σ = {E,U,H} for S→T and T→S from base, S, T only.  They meet at the common
   packet boundary (the observed per-item verdicts) and are updated by Bayes' rule with a noise model whose
   width is the *measured* replicate floor of that cell.  Posterior mass is tracked sequentially across cells.
     last_writer   composite = the second pass's single-pass verdicts   (overwrite)
     first_writer  composite = the first pass's single-pass verdicts    (freeze)
     markov        lumpable 3×3 verdict channel composed                (benchmark-is-sufficient-statistic)
     tilt          commuting affine map on log-ratio coordinates        (exponential-tilt null)
     overlap       item-overlap null on verdict triples                 (label-aware, "second wins on overlap")
     base          composite = base                                     (nothing happened; sanity anchor)

Usage: python report.py [runs_dir]   → report/report.md, report/report.html, report/hypotheses.json
"""
import glob, json, os, sys, html
import numpy as np
from scipy import stats as sps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from euh import stats as S

LAB = ["E", "U", "H"]


# ------------------------------------------------------------------ helpers ---
def cells_of(L):
    return sorted(L["cells"].values(), key=lambda c: (c["alpha"], c["seed"]))


def floor_of(c):
    f = c["score"].get("floors", {})
    return f.get("order_disagreement_floor", np.nan)


def majority(flags, frac=2 / 3):
    flags = [f for f in flags if f is not None]
    return len(flags) > 0 and np.mean(flags) >= frac


# ------------------------------------------------------------------ hypotheses ---
def H_order_effect(L):
    cs = cells_of(L); r = [c["score"]["floors"].get("disagreement_over_floor") for c in cs]
    r = [x for x in r if x is not None and np.isfinite(x)]
    if len(r) < 2: return "U", "no replicate floor in this stage", {}
    ev = dict(median_ratio=float(np.median(r)), frac_ge2=float(np.mean(np.array(r) >= 2)), frac_le1_2=float(np.mean(np.array(r) <= 1.2)))
    if ev["frac_ge2"] >= 2 / 3: return "E", f"order disagreement ≥2× floor in {ev['frac_ge2']:.0%} of cells (median {ev['median_ratio']:.1f}×)", ev
    if ev["frac_le1_2"] >= 2 / 3: return "H", f"order disagreement ≤1.2× floor in {ev['frac_le1_2']:.0%} of cells", ev
    return "U", f"mixed: median {ev['median_ratio']:.1f}× floor", ev


def H_gamma_sign(L):
    cs = cells_of(L); g = np.array([c["score"]["Gamma"][1] for c in cs])
    if len(g) < 3: return "U", "fewer than 3 cells", {}
    m, sd = g.mean(), g.std(ddof=1); ev = dict(mean=float(m), sd=float(sd), n=len(g), frac_pos=float(np.mean(g > 0)))
    if m > 0 and m > 2 * sd / np.sqrt(len(g)) and ev["frac_pos"] >= 0.8: return "E", f"Γ_U = {m:+.3f} ± {sd:.3f}, positive in {ev['frac_pos']:.0%} of cells", ev
    if m < 0 and -m > 2 * sd / np.sqrt(len(g)) and ev["frac_pos"] <= 0.2: return "H", f"Γ_U = {m:+.3f} ± {sd:.3f}, negative in {1-ev['frac_pos']:.0%} of cells", ev
    return "U", f"Γ_U = {m:+.3f} ± {sd:.3f}, sign not stable", ev


def H_nonlumpable(L):
    cs = cells_of(L); p = [min(c["score"]["lumpability"]["ST"]["p"], c["score"]["lumpability"]["TS"]["p"]) for c in cs]
    ev = dict(frac_reject=float(np.mean(np.array(p) < 0.01)), n=len(p))
    if not p: return "U", "no cells", ev
    if ev["frac_reject"] >= 2 / 3: return "E", f"Markov composite rejected (p<0.01) in {ev['frac_reject']:.0%} of cells", ev
    if ev["frac_reject"] <= 1 / 3: return "H", f"Markov composite not rejected in {1-ev['frac_reject']:.0%} of cells", ev
    return "U", f"rejected in {ev['frac_reject']:.0%} of cells", ev


def H_outside_overlap(L):
    cs = [c for c in cells_of(L) if c["score"]["disagreement"] > 0]
    fr = [c["score"]["pred_err"]["overlap"]["disagree_outside_overlap"] / max(c["score"]["disagreement"], 1e-9) for c in cs]
    if not fr: return "U", "no disagreement observed", {}
    ev = dict(median_frac_outside=float(np.median(fr)), n=len(fr))
    if ev["median_frac_outside"] >= 0.9: return "E", f"{ev['median_frac_outside']:.0%} of order-disagreement lies outside the predicted overlap set", ev
    if ev["median_frac_outside"] <= 0.5: return "H", f"only {ev['median_frac_outside']:.0%} outside the overlap set", ev
    return "U", f"{ev['median_frac_outside']:.0%} outside", ev


def H_overlap_ratio(L):
    cs = cells_of(L); r = [c["prediction"]["overlap"]["overlap_ratio"] for c in cs]
    ev = dict(median=float(np.median(r)), n=len(r), mode=cs[0].get("mode", "?"))
    if not r: return "U", "no cells", ev
    if ev["mode"] == "weighted":
        return ("E" if ev["median"] >= 3 else "U"), f"weighted (shared-pool) mode: overlap ratio {ev['median']:.1f}× — flip sets {'co-dependent (one operator)' if ev['median']>=3 else 'not clearly co-dependent'}", ev
    if 0.7 <= ev["median"] <= 1.5: return "E", f"disjoint mode: overlap ratio {ev['median']:.2f} — flip sets independent (two operators)", ev
    if ev["median"] > 3: return "H", f"disjoint mode but overlap ratio {ev['median']:.1f}× — operators still share a component", ev
    return "U", f"overlap ratio {ev['median']:.2f}", ev


def H_boundary(L):
    cs = cells_of(L); a = [c["score"]["disagree_margin"]["auc"] for c in cs if np.isfinite(c["score"]["disagree_margin"]["auc"])]
    if not a: return "U", "no AUC", {}
    ev = dict(median_auc=float(np.median(a)))
    if ev["median_auc"] >= 0.75: return "E", f"AUC(base margin → flip) = {ev['median_auc']:.2f}: order effect concentrates at verdict boundaries", ev
    if ev["median_auc"] <= 0.6: return "H", f"AUC = {ev['median_auc']:.2f}: order effect not confined to boundaries", ev
    return "U", f"AUC = {ev['median_auc']:.2f}", ev


def H_specimen(L):
    """Prop 6.3 specimen: readouts coincide (Stuart–Maxwell p>0.05) while revision differs (>2× floor)."""
    hits = [c for c in cells_of(L) if c["score"]["stuart_maxwell"][2] > 0.05 and (c["score"]["floors"].get("disagreement_over_floor") or 0) >= 2]
    ev = dict(n_specimen=len(hits), cells=[f"a{c['alpha']}_s{c['seed']}" for c in hits])
    if hits: return "E", f"{len(hits)} cell(s) with homogeneous marginals yet ≥2× floor item disagreement: {ev['cells']}", ev
    return "U", "no cell shows coincident readouts with above-floor revision difference (not refutable by absence)", ev


def H_shared_slider(L):
    cs = cells_of(L)
    if cs[0].get("slider") != "shared": return "U", "needs the shared-fraction slider stage", {}
    a = [c["alpha"] for c in cs]; r = [c["prediction"]["overlap"]["overlap_ratio"] for c in cs]
    if len(set(a)) < 3: return "U", "fewer than 3 slider values", {}
    rho = sps.spearmanr(a, r).correlation; ev = dict(spearman=float(rho))
    if rho >= 0.6: return "E", f"overlap ratio rises with shared fraction (ρ={rho:.2f})", ev
    if rho <= -0.3: return "H", f"overlap ratio falls with shared fraction (ρ={rho:.2f})", ev
    return "U", f"ρ={rho:.2f}", ev


def H_negative_control(L):
    cs = cells_of(L)
    if cs[0].get("mode") != "weighted": return "U", "needs the weighted-mode control stage", {}
    r = [c["score"]["floors"].get("disagreement_over_floor") for c in cs]; r = [x for x in r if x]
    if not r: return "U", "no floor", {}
    ev = dict(median_ratio=float(np.median(r)))
    if ev["median_ratio"] <= 1.5: return "E", f"shared-operator control shows no order effect above floor ({ev['median_ratio']:.1f}×) — design diagnosis confirmed", ev
    if ev["median_ratio"] >= 2.5: return "H", f"shared-operator control still shows {ev['median_ratio']:.1f}× floor", ev
    return "U", f"{ev['median_ratio']:.1f}× floor", ev


def H_join_loss(L):
    b = [c["score"]["join_bits_lost"] for c in cells_of(L)]; ev = dict(median_bits=float(np.median(b)))
    return ("E" if ev["median_bits"] >= 0.2 else "U"), f"publishing join(ST,TS) instead of the tuple destroys {ev['median_bits']:.2f} bits/item (median)", ev


# ---- noise-calibrated hypotheses (sealed 2026-08-17, after the audit showed H3/H4/H6 fire on
# ---- replicate noise; each statistic below is benchmarked against the same statistic computed
# ---- on same-order replicate composites, so pure seed noise reads ~1x by construction)
def _rep_verdicts(c, order):
    return [np.array(p).argmax(1) for p in c["replicates"].get(order, [])]


def H_nonlumpable_cal(L):
    """Observed lumpability chi2 vs the same chi2 with a replicate composite as 'observed'."""
    vb = np.array(L["base"]).argmax(1); ratios = []
    for c in cells_of(L):
        rr = []
        for order in ("ST", "TS"):
            reps = _rep_verdicts(c, order)
            if not reps: continue
            M = np.array(c["prediction"]["markov"][f"M_{order}"])
            obs = c["score"]["lumpability"][order]["chi2"]
            noise = [S.lumpability_chi2(vb, vr, M)[0] for vr in reps]
            rr.append(obs / max(float(np.median(noise)), 1e-9))
        if rr: ratios.append(float(np.mean(rr)))
    if len(ratios) < 3: return "U", "needs replicates in ≥3 cells", {}
    ev = dict(median_ratio=float(np.median(ratios)), frac_ge2=float(np.mean(np.array(ratios) >= 2)), n=len(ratios))
    if ev["frac_ge2"] >= 2 / 3: return "E", f"observed non-lumpability ≥2× the replicate-noise statistic in {ev['frac_ge2']:.0%} of cells (median {ev['median_ratio']:.1f}×)", ev
    if ev["median_ratio"] <= 1.2: return "H", f"observed non-lumpability ≈ noise level (median {ev['median_ratio']:.1f}×)", ev
    return "U", f"median {ev['median_ratio']:.1f}× the noise statistic", ev


def H_outside_overlap_cal(L):
    """Localization of the ABOVE-NOISE excess: excess disagreement rate in/outside the overlap set."""
    vb = np.array(L["base"]).argmax(1); fracs = []
    for c in cells_of(L):
        vS = np.array(c["P"]["S"]).argmax(1); vT = np.array(c["P"]["T"]).argmax(1)
        vST = np.array(c["P"]["ST"]).argmax(1); vTS = np.array(c["P"]["TS"]).argmax(1)
        ov = (vS != vb) & (vT != vb)
        dis = vST != vTS
        o_obs, i_obs = float(dis[~ov].mean()), float(dis[ov].mean()) if ov.any() else 0.0
        no, ni = [], []
        for order, vmain in (("ST", vST), ("TS", vTS)):
            for vr in _rep_verdicts(c, order):
                nd = vmain != vr
                no.append(float(nd[~ov].mean())); ni.append(float(nd[ov].mean()) if ov.any() else 0.0)
        if not no: continue
        ex_out = max(o_obs - float(np.mean(no)), 0.0); ex_in = max(i_obs - float(np.mean(ni)), 0.0)
        if ex_out + ex_in >= 0.005:
            fracs.append(ex_out / (ex_out + ex_in))
    if len(fracs) < 3: return "U", f"above-noise excess ≥0.5% in only {len(fracs)} cell(s) — nothing to localize", dict(n_eligible=len(fracs))
    ev = dict(median_frac_outside=float(np.median(fracs)), n_eligible=len(fracs))
    if ev["median_frac_outside"] >= 0.9: return "E", f"{ev['median_frac_outside']:.0%} of the above-noise excess lies outside the overlap set ({ev['n_eligible']} eligible cells)", ev
    if ev["median_frac_outside"] <= 0.5: return "H", f"above-noise excess mostly inside the overlap set ({ev['median_frac_outside']:.0%} outside)", ev
    return "U", f"{ev['median_frac_outside']:.0%} of excess outside", ev


def H_sign_consistency(L):
    """Weaker magnitude claim than H1: the order/floor ratio exceeds 1 almost everywhere."""
    r = [c["score"]["floors"].get("disagreement_over_floor") for c in cells_of(L)]
    r = [x for x in r if x is not None and np.isfinite(x)]
    if len(r) < 6: return "U", "fewer than 6 cells with floors", {}
    ev = dict(frac_gt1=float(np.mean(np.array(r) > 1)), n=len(r), median=float(np.median(r)))
    if ev["frac_gt1"] >= 0.9: return "E", f"ratio >1× floor in {ev['frac_gt1']:.0%} of {ev['n']} cells (median {ev['median']:.1f}×)", ev
    if ev["frac_gt1"] <= 0.5: return "H", f"ratio >1× floor in only {ev['frac_gt1']:.0%} of cells", ev
    return "U", f">1× in {ev['frac_gt1']:.0%} of cells", ev


# ---- v3 power battery (pre-registered 2026-08-17, before the battery is launched).
# ---- The v2 floor came from a SINGLE replicate pair per cell, so the ratio was badly
# ---- estimated (sibling seeds gave 1.82x and 1.06x at the same alpha). With m runs per
# ---- order the same quantity rests on m(m-1) within-order pairs and m^2 cross-order pairs.
# ---- The pairwise ratio is m-independent in expectation, so raising m sharpens the
# ---- estimate without inflating the statistic — unlike ensemble averaging, which would.
def _order_runs(c, order):
    """Every run of one order: the recorded composite plus its replicates."""
    return [np.array(c["P"][order]).argmax(1)] + _rep_verdicts(c, order)


def _pair_decomp(c, B=400, seed=0):
    """Split item-level composite disagreement into within-order (noise) and cross-order.

    within = mean pairwise disagreement among runs of the SAME order (pure run noise)
    cross  = mean pairwise disagreement between runs of DIFFERENT orders (noise + order)
    excess = cross - within, with a percentile bootstrap over items
    sys_frac = excess / cross, the fraction of cross-order disagreement that is systematic
    """
    ST, TS = _order_runs(c, "ST"), _order_runs(c, "TS")
    if len(ST) < 2 or len(TS) < 2:
        return None
    W = np.array([(a != b) for R in (ST, TS) for i, a in enumerate(R) for b in R[i + 1:]])
    C = np.array([(a != b) for a in ST for b in TS])
    if not len(W) or not len(C):
        return None
    n = W.shape[1]; rng = np.random.default_rng(seed)
    ex = [float(C[:, i].mean() - W[:, i].mean())
          for i in (rng.integers(0, n, n) for _ in range(B))]
    lo, hi = np.percentile(ex, [2.5, 97.5])
    w, cr = float(W.mean()), float(C.mean())
    return dict(within=w, cross=cr, excess=cr - w, lo=float(lo), hi=float(hi),
                ratio=cr / max(w, 1e-9), sys_frac=(cr - w) / max(cr, 1e-9))


def H_systematic_component(L):
    """H14: is any part of the cross-order difference systematic rather than run noise?"""
    ds = [d for d in (_pair_decomp(c) for c in cells_of(L)) if d]
    if len(ds) < 3:
        return "U", "needs ≥3 cells with ≥2 runs per order (n_replicate ≥ 2)", {}
    pos = float(np.mean([d["lo"] > 0 for d in ds]))
    neg = float(np.mean([d["hi"] < 0 for d in ds]))
    ev = dict(frac_ci_above_0=pos, median_sys_frac=float(np.median([d["sys_frac"] for d in ds])),
              median_ratio=float(np.median([d["ratio"] for d in ds])), n=len(ds))
    if pos >= 2 / 3:
        return "E", (f"systematic component >0 (bootstrap CI excludes 0) in {pos:.0%} of cells; "
                     f"{ev['median_sys_frac']:.0%} of cross-order disagreement is systematic "
                     f"(median ratio {ev['median_ratio']:.2f}×)"), ev
    if neg >= 2 / 3:
        return "H", f"cross-order disagreement is BELOW within-order noise in {neg:.0%} of cells", ev
    return "U", f"CI excludes 0 in only {pos:.0%} of cells (median {ev['median_sys_frac']:.0%} systematic)", ev


# ---- battery-level rules: these compare stages, so they take the whole ledger dict ----
PARAMS_M = {"google/bert_uncased_L-2_H-128_A-2": 4.4, "google/bert_uncased_L-4_H-256_A-4": 11.3,
            "google/bert_uncased_L-4_H-512_A-8": 28.8, "google/bert_uncased_L-8_H-512_A-8": 41.4,
            "bert-base-uncased": 110.0, "bert-large-uncased": 335.0}


def _stage_sys(L):
    return [d for d in (_pair_decomp(c) for c in cells_of(L)) if d]


def H_nullswap_matched(ledgers):
    """H15: does operator IDENTITY drive the order difference, against a matched control?

    The null-swap arm runs the same objective on both passes, so its cross-order difference
    is what two passes produce when order is semantically null — a floor matched in
    perturbation structure, unlike a same-order replicate (which re-seeds a whole pass).
    """
    t = next((L for k, L in ledgers.items() if k.endswith("power_treat")), None)
    z = next((L for k, L in ledgers.items() if k.endswith("power_nullswap")), None)
    if t is None or z is None:
        return "U", "needs both power_treat and power_nullswap stages", {}
    dt, dz = _stage_sys(t), _stage_sys(z)
    if len(dt) < 3 or len(dz) < 3:
        return "U", "needs ≥3 cells per arm", {}
    st = float(np.median([d["sys_frac"] for d in dt])); sz = float(np.median([d["sys_frac"] for d in dz]))
    ev = dict(treat_sys_frac=st, nullswap_sys_frac=sz, n_treat=len(dt), n_null=len(dz),
              treat_frac_ci_above_0=float(np.mean([d["lo"] > 0 for d in dt])))
    if st >= 2 * max(sz, 1e-9) and ev["treat_frac_ci_above_0"] >= 2 / 3:
        return "E", (f"two-operator order effect is {st / max(sz, 1e-9):.1f}× the matched null-swap "
                     f"control ({st:.0%} vs {sz:.0%} systematic)"), ev
    if st <= sz:
        return "H", f"null swap shows as much order effect as the two-operator arm ({sz:.0%} vs {st:.0%})", ev
    return "U", f"treatment {st:.0%} vs null-swap {sz:.0%} systematic — under the 2× bar", ev


def H_scale_trend(ledgers):
    """H16: does the order/noise ratio rise with model scale, as tiny→base suggested?"""
    pts = []
    for k, L in ledgers.items():
        p = PARAMS_M.get(L["meta"].get("model"))
        ds = _stage_sys(L)
        if p and len(ds) >= 2 and "scale" in k:
            pts.append((p, float(np.median([d["ratio"] for d in ds]))))
    if len(pts) < 4:
        return "U", f"needs ≥4 scale stages, have {len(pts)}", dict(points=pts)
    x, y = np.log([p for p, _ in pts]), np.array([r for _, r in pts])
    rho = float(sps.spearmanr(x, y).statistic)
    sl, ic = np.polyfit(x, y, 1)
    need = float(np.exp((2.0 - ic) / sl)) if sl > 0 else float("inf")
    ev = dict(spearman=rho, slope_per_e_fold=float(sl), points=pts, params_M_for_2x=need)
    if rho >= 0.6:
        return "E", (f"ratio rises with scale (ρ={rho:+.2f}, {sl:+.2f} per e-fold); "
                     f"extrapolates to 2× at ≈{need:,.0f}M params"), ev
    if rho <= 0:
        return "H", f"ratio does not rise with scale (ρ={rho:+.2f})", ev
    return "U", f"weak scale trend (ρ={rho:+.2f})", ev


BATTERY_HYPS = [
    ("H15", "Operator identity drives the order difference (matched null-swap control)",
     "median systematic fraction in power_treat ≥ 2× power_nullswap, with CI>0 in ≥2/3 of treat cells", H_nullswap_matched),
    ("H16", "Order/noise ratio rises with model scale",
     "Spearman(log params, pairwise ratio) ≥ 0.6 over ≥4 scale stages", H_scale_trend),
]


HYPS = [
    ("H1", "Order effect exceeds the composite's own seed noise", "disagreement(S→T,T→S) ≥ 2× same-order replicate disagreement in ≥2/3 of cells", H_order_effect),
    ("H2", "Γ_U sign: S→T ends more neutral than T→S, seed-stable", "mean Γ_U > 0, |mean| > 2·SE, positive in ≥80% cells", H_gamma_sign),
    ("H3", "Non-lumpability: verdict marginal is not a sufficient statistic", "Markov composite Φ_S·Φ_T rejected (χ² p<0.01) in ≥2/3 of cells", H_nonlumpable),
    ("H4", "Order effect lives OUTSIDE the overlap of the two flip sets", "≥90% of cross-order disagreement on items neither pass flipped or only one flipped", H_outside_overlap),
    ("H5", "Flip-set co-dependence tracks operator identity", "disjoint objectives → overlap ratio ≈1; shared operator → ≫1", H_overlap_ratio),
    ("H6", "Order effect concentrates at verdict boundaries", "AUC(base top-2 margin → flip) ≥ 0.75", H_boundary),
    ("H7", "Prop 6.3 specimen: readouts coincide, revisions differ", "some cell with Stuart–Maxwell p>0.05 AND disagreement ≥2× floor", H_specimen),
    ("H8", "Shared-fraction slider raises co-dependence", "Spearman(α_shared, overlap ratio) ≥ 0.6", H_shared_slider),
    ("H9", "Negative control: one operator ⇒ no order effect", "weighted mode: disagreement ≤ 1.5× floor", H_negative_control),
    ("H10", "The join destroys information", "H(tuple) − H(join) ≥ 0.2 bit/item", H_join_loss),
    ("H11", "Calibrated non-lumpability: exceeds the replicate-noise statistic", "obs χ² ≥ 2× median replicate-composite χ² in ≥2/3 of cells", H_nonlumpable_cal),
    ("H12", "Calibrated localization: above-noise excess lies outside the overlap set", "≥90% of excess (obs − replicate-noise rate) outside, ≥3 cells with ≥0.5% excess", H_outside_overlap_cal),
    ("H13", "Sign consistency: order/floor ratio >1 almost everywhere", "ratio >1× floor in ≥90% of ≥6 cells", H_sign_consistency),
    ("H14", "A systematic (non-noise) order component exists",
     "cross-order minus within-order pairwise disagreement >0, bootstrap CI excluding 0, in ≥2/3 of cells", H_systematic_component),
]


# ------------------------------------------------------------------ theories (Bayes over presentations) ---
def theory_predictions(Pb, P):
    vb, vS, vT = S.verdicts(Pb), S.verdicts(P["S"]), S.verdicts(P["T"])
    pred = S.predict_composites(Pb, P["S"], P["T"])
    M_ST, M_TS = np.array(pred["markov"]["M_ST"]), np.array(pred["markov"]["M_TS"])
    return {
        "last_writer": dict(ST=vT, TS=vS),
        "first_writer": dict(ST=vS, TS=vT),
        "markov": dict(ST=M_ST.argmax(1)[vb], TS=M_TS.argmax(1)[vb]),
        "tilt": dict(ST=np.array(pred["alr"]["v_ST"]), TS=np.array(pred["alr"]["v_TS"])),
        "overlap": dict(ST=np.array(pred["overlap"]["v_ST"]), TS=np.array(pred["overlap"]["v_TS"])),
        "base": dict(ST=vb, TS=vb),
    }


def loglik(vpred, vobs, eps):
    """Noise model: predicted verdict realised w.p. 1−ε, else uniform over the other two.  ε = measured floor."""
    eps = float(np.clip(eps, 0.02, 0.45)); hit = (vpred == vobs)
    return float(np.sum(np.where(hit, np.log(1 - eps), np.log(eps / 2))))


def _norm(logw):
    m = max(logw.values()); w = {n: np.exp(v - m) for n, v in logw.items()}; z = sum(w.values()); return {n: w[n] / z for n in w}


def bayes_over_theories(L, n_eff=200):
    """Two packets, two updates.
    (a) composite packet: per-item verdicts of S→T and T→S.  Tempered: each cell contributes its mean per-item
        log-lik × n_eff (items are not independent; n_eff=200 is a conservative effective sample size).
    (b) order packet: the per-item disagreement indicator d_i = [v_ST ≠ v_TS].  Theory likelihood from its own
        predicted disagreement set with the same ε noise.  This is the statistic the order-effect question is about;
        a theory that predicts every composite well but no order effect loses here."""
    Pb = np.array(L["base"]); names = ["last_writer", "first_writer", "markov", "tilt", "overlap", "base"]
    lp_c = {n: 0.0 for n in names}; lp_o = {n: 0.0 for n in names}; traj_c, traj_o, per_cell = [], [], []
    for c in cells_of(L):
        P = {k: np.array(v) for k, v in c["P"].items()}; th = theory_predictions(Pb, P)
        vST, vTS = S.verdicts(P["ST"]), S.verdicts(P["TS"]); d_obs = (vST != vTS)
        f = c["score"]["floors"]; eps = f.get("order_disagreement_floor", 0.05) or 0.05
        n_items = 2 * len(vST)
        ll_c = {n: (loglik(th[n]["ST"], vST, eps) + loglik(th[n]["TS"], vTS, eps)) / n_items for n in names}
        d_pred = {n: (th[n]["ST"] != th[n]["TS"]) for n in names}
        # class-balanced order log-lik: mean over observed-flip items and over observed-nonflip items, then average.
        def ll_bal(dp):
            m = np.where(dp == d_obs, np.log(1 - eps), np.log(eps))
            parts = [m[d_obs].mean() if d_obs.any() else 0.0, m[~d_obs].mean() if (~d_obs).any() else 0.0]
            return float(np.mean(parts))
        ll_o = {n: ll_bal(d_pred[n]) for n in names}
        for n in names: lp_c[n] += n_eff * ll_c[n]; lp_o[n] += n_eff * ll_o[n]
        traj_c.append(_norm(lp_c)); traj_o.append(_norm(lp_o))
        def f1(a, b):
            tp = np.sum(a & b); return float(2 * tp / max(a.sum() + b.sum(), 1))
        per_cell.append(dict(cell=f"a{c['alpha']}_s{c['seed']}", eps=eps, ll_per_item=ll_c, ll_order=ll_o,
                             acc={n: float(0.5 * (np.mean(th[n]["ST"] == vST) + np.mean(th[n]["TS"] == vTS))) for n in names},
                             flip_f1={n: f1(d_pred[n], d_obs) for n in names},
                             pred_dis={n: float(d_pred[n].mean()) for n in names}, obs_dis=float(d_obs.mean())))
    return names, (traj_c, traj_o), per_cell


# ------------------------------------------------------------------ rendering ---
def badge(v):
    return {"E": "🟢 E", "H": "🔴 H", "U": "⚪ U"}[v]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    runs = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "runs")
    # report goes inside the scanned dir when one is given (battery folders stay self-contained)
    out = os.path.join(runs, "report") if len(sys.argv) > 1 else os.path.join(here, "report")
    os.makedirs(out, exist_ok=True)
    ledgers = {}
    for p in sorted(glob.glob(os.path.join(runs, "*", "ledger.json")) + glob.glob(os.path.join(runs, "*", "*", "ledger.json"))):
        st = os.path.relpath(os.path.dirname(p), runs).replace(os.sep, "/")
        try:
            L = json.load(open(p))
            if L.get("cells"): ledgers[st] = L
        except Exception as e:
            print("skip", p, e)
    if not ledgers: print("no ledgers found"); return
    md = ["# EUH order-dependence — hypothesis ledger\n",
          "Verdicts: **E** witnessed under the pre-registered rule · **H** refuted · **U** not resolved by this data "
          "(a definite verdict of non-resolution, not a probability over E/H).\n"]
    md.append("## Datasets\n\n| stage | model | mode | slider | cells | base acc | replicates |\n|---|---|---|---|---|---|---|")
    for st, L in ledgers.items():
        cs = cells_of(L); gold = np.array(L["gold"]); acc = float(np.mean(S.verdicts(np.array(L["base"])) == gold))
        md.append(f"| {st} | {L['meta']['model']} | {cs[0].get('mode','weighted')} | {cs[0].get('slider','—')} | {len(cs)} | {acc:.3f} | {L['meta'].get('n_replicate',1)} |")
    md.append("\n## Hypotheses × datasets\n")
    hdr = "| # | hypothesis | rule | " + " | ".join(ledgers) + " |"; md.append(hdr); md.append("|" + "---|" * (3 + len(ledgers)))
    ledger_json = {}
    for hid, name, rule, fn in HYPS:
        row = [f"**{hid}**", name, f"<sub>{rule}</sub>"]; ledger_json[hid] = dict(name=name, rule=rule, verdicts={})
        for st, L in ledgers.items():
            try: v, why, ev = fn(L)
            except Exception as e: v, why, ev = "U", f"error: {e}", {}
            row.append(f"{badge(v)}<br><sub>{html.escape(why)}</sub>"); ledger_json[hid]["verdicts"][st] = dict(verdict=v, why=why, evidence=ev)
        md.append("| " + " | ".join(row) + " |")
    battery_json = {}
    rows_b = []
    for hid, name, rule, fn in BATTERY_HYPS:
        try: v, why, ev = fn(ledgers)
        except Exception as e: v, why, ev = "U", f"error: {e}", {}
        battery_json[hid] = dict(name=name, rule=rule, verdict=v, why=why, evidence=ev)
        rows_b.append(f"| **{hid}** | {name} | <sub>{rule}</sub> | {badge(v)}<br><sub>{html.escape(why)}</sub> |")
    if rows_b:
        md.append("\n## Battery-level hypotheses\n")
        md.append("These compare stages against each other rather than scoring one stage, so they carry a "
                  "single verdict per battery.\n")
        md.append("| # | hypothesis | rule | verdict |\n|---|---|---|---|")
        md += rows_b

    md.append("\n## Bayesian update over theories of the composite\n")
    md.append("Each theory predicts every item's verdict for S→T and T→S from base, S, T only; likelihood uses ε = the cell's "
              "measured replicate floor. Uniform prior; posterior after the last cell of each stage.\n")
    names = ["last_writer", "first_writer", "markov", "tilt", "overlap", "base"]
    md.append("**(a) composite packet** — per-item verdicts of S→T and T→S (tempered, n_eff=200 per cell)\n")
    md.append("| stage | " + " | ".join(names) + " | best | verdict acc of best |\n|---|" + "---|" * (len(names) + 2))
    bayes_json = {}; rows_o = []
    for st, L in ledgers.items():
        try:
            nm, (tc, to), per_cell = bayes_over_theories(L); post = tc[-1]; best = max(post, key=post.get)
            acc_best = float(np.mean([pc["acc"][best] for pc in per_cell]))
            md.append(f"| {st} | " + " | ".join(f"{post[n]:.3f}" for n in names) + f" | **{best}** | {acc_best:.3f} |")
            posto = to[-1]; besto = max(posto, key=posto.get); f1b = float(np.mean([pc["flip_f1"][besto] for pc in per_cell]))
            rows_o.append(f"| {st} | " + " | ".join(f"{posto[n]:.3f}" for n in names) + f" | **{besto}** | {f1b:.3f} | {np.mean([pc['obs_dis'] for pc in per_cell]):.3f} |")
            bayes_json[st] = dict(posterior_composite=post, posterior_order=posto, trajectory_composite=tc, trajectory_order=to, per_cell=per_cell)
        except Exception as e:
            md.append(f"| {st} | error: {e} |")
    md.append("\n**(b) order packet** — per-item disagreement indicator [v_ST ≠ v_TS], class-balanced log-lik (a theory that predicts no flips pays log ε on every observed flip); this is the statistic the order question is about\n")
    md.append("| stage | " + " | ".join(names) + " | best | flip-set F1 of best | observed disagreement |\n|---|" + "---|" * (len(names) + 3)); md += rows_o
    md.append("\n<sub>Posterior concentration is relative to the theories entertained; an absent theory cannot acquire mass "
              "(§3.5). Per-item accuracy of the best theory is reported so a 'winner' that is merely least-wrong is visible as such.</sub>\n")
    # per-stage per-cell theory accuracy table
    md.append("\n### Per-cell verdict accuracy of each theory\n")
    for st, bj in bayes_json.items():
        md.append(f"\n**{st}** — verdict accuracy / flip-set F1 (predicted disagreement rate)\n\n| cell | ε (floor) | obs dis | " + " | ".join(names) + " |\n|---|---|---|" + "---|" * len(names))
        for pc in bj["per_cell"]:
            md.append(f"| {pc['cell']} | {pc['eps']:.3f} | {pc['obs_dis']:.3f} | " + " | ".join(f"{pc['acc'][n]:.2f} / {pc['flip_f1'][n]:.2f} ({pc['pred_dis'][n]:.2f})" for n in names) + " |")
    # figures index
    md.append("\n## Figures\n")
    for st in ledgers:
        figs = sorted(glob.glob(os.path.join(runs, st, "figures", "*.png")))
        if figs:
            md.append(f"\n### {st}\n"); md += [f"![{os.path.basename(f)}]({os.path.relpath(f, out).replace(os.sep, '/')})" for f in figs]
    text = "\n".join(md)
    open(os.path.join(out, "report.md"), "w", encoding="utf-8").write(text)
    json.dump(dict(hypotheses=ledger_json, battery_hypotheses=battery_json, bayes=bayes_json),
              open(os.path.join(out, "hypotheses.json"), "w"), indent=1)
    # simple HTML
    try:
        import markdown  # optional
        body = markdown.markdown(text, extensions=["tables"])
    except Exception:
        body = "<pre>" + html.escape(text) + "</pre>"
    open(os.path.join(out, "report.html"), "w", encoding="utf-8").write(f"<html><head><meta charset='utf-8'><style>body{{font-family:sans-serif;max-width:1400px;margin:auto}} table{{border-collapse:collapse}} td,th{{border:1px solid #ccc;padding:4px;vertical-align:top}} img{{max-width:100%}}</style></head><body>{body}</body></html>")
    print(text)
    print("\nwritten:", os.path.join(out, "report.md"), os.path.join(out, "report.html"))


if __name__ == "__main__":
    main()
