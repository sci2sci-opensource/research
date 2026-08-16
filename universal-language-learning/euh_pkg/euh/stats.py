"""
Measurement core.  Paper object → statistic.

verdict s∈Σ={E,U,H}   argmax of the 3-vector
C(W)∈Δ(Σ)             verdict marginal
paired joint          3×3 table on shared items
readout coincidence   Stuart–Maxwell marginal homogeneity
revision difference   item disagreement / Bowker symmetry
channel Φ_X           (a) row-stochastic 3×3 on Σ from base→X  (lumpable/Markov predictor)
                      (b) affine map on ALR(Δ²) coordinates      (continuous predictor)
commutator            ‖[Φ_S,Φ_T]‖, ‖[A_S,A_T]‖
prediction of ST/TS   from single passes only (sealed before composites are trained)
non-lumpability       χ² of base→XY rows vs Markov composite
Γ / interaction / carryover   crossover decomposition
join info loss        H(tuple) − H(join) under E≺U≺H
"""
import numpy as np
from scipy import stats

LAB = ["E", "U", "H"]


def verdicts(P): return P.argmax(1)
def marginal(v): return np.bincount(v, minlength=3) / len(v)
def tv(p, q): return 0.5 * float(np.abs(np.asarray(p) - np.asarray(q)).sum())


def joint(v1, v2):
    N = np.zeros((3, 3))
    for a, b in zip(v1, v2): N[a, b] += 1
    return N


def stuart_maxwell(N):
    k = N.shape[0]; d = (N.sum(1) - N.sum(0))[:-1]
    V = np.zeros((k - 1, k - 1))
    for i in range(k - 1):
        for j in range(k - 1):
            V[i, j] = -(N[i, j] + N[j, i]) if i != j else N[i].sum() + N[:, i].sum() - 2 * N[i, i]
    try: s = float(d @ np.linalg.solve(V, d))
    except np.linalg.LinAlgError: return np.nan, k - 1, np.nan
    return s, k - 1, float(1 - stats.chi2.cdf(s, k - 1))


def bowker(N):
    s, df = 0.0, 0
    for i in range(3):
        for j in range(i + 1, 3):
            t = N[i, j] + N[j, i]
            if t > 0: s += (N[i, j] - N[j, i]) ** 2 / t; df += 1
    return s, df, (float(1 - stats.chi2.cdf(s, df)) if df else np.nan)


def channel(v_from, v_to):
    N = joint(v_from, v_to) + 0.5
    return N / N.sum(1, keepdims=True)


def alr(P, eps=1e-6):
    P = np.clip(P, eps, 1); return np.log(P[:, [0, 2]] / P[:, [1]])


def alr_inv(X):
    Z = np.c_[X[:, 0], np.zeros(len(X)), X[:, 1]]; Z = np.exp(Z - Z.max(1, keepdims=True))
    return Z / Z.sum(1, keepdims=True)


def fit_affine(X, Y):
    Xa = np.hstack([X, np.ones((len(X), 1))])
    W, *_ = np.linalg.lstsq(Xa, Y, rcond=None); return W[:-1], W[-1]


def apply_affine(X, A, b): return X @ A + b
def compose_affine(A1, b1, A2, b2): return A1 @ A2, b1 @ A2 + b2



# ------------------------------------------------- item-overlap null (verdict-triple predictor) ---
def overlap_predict(vb, vS, vT, order):
    """Per-item prediction of the composite verdict from the (base, S, T) verdict triple.

    Null: the second pass acts on the verdict the first pass left, with the same per-cell behaviour it
    showed from base — i.e. it is *lumpable at the item level with respect to its own single-pass move*:
        item flipped by first pass only        → keeps first-pass verdict
        item flipped by second pass only       → takes second-pass verdict
        item untouched by both                 → base verdict
        item in the overlap A_1 ∩ A_2          → second pass wins (it acts last on a verdict it also moved
                                                 from base); this is where the two orders differ.
    """
    v1, v2 = (vS, vT) if order == "ST" else (vT, vS)
    f1, f2 = v1 != vb, v2 != vb
    out = vb.copy()
    out[f1] = v1[f1]
    out[f2] = v2[f2]           # second pass wins on overlap
    return out


def overlap_stats(vb, vS, vT):
    fS, fT = vS != vb, vT != vb
    n = len(vb)
    both = fS & fT; disagree = both & (vS != vT)
    pS, pT = fS.mean(), fT.mean()
    return dict(flip_S=float(pS), flip_T=float(pT), overlap=float(both.mean()),
                overlap_indep=float(pS * pT),                    # independence expectation
                overlap_ratio=float(both.mean() / max(pS * pT, 1e-9)),   # >1: co-dependent flip sets
                overlap_disagree=float(disagree.mean()),          # only these items can carry an order effect
                pred_max_disagreement=float(disagree.mean()))


def boundary_dist(X):
    """ALR-plane distance to the nearest verdict boundary.  Coords a=log(pE/pU), b=log(pH/pU);
    regions E: a>0,a>=b (boundaries a=0, a=b) · H: b>0,b>a (b=0, a=b) · U: else (a=0, b=0)."""
    a, b = X[:, 0], X[:, 1]
    d_a0 = np.abs(a); d_b0 = np.abs(b); d_ab = np.abs(a - b) / np.sqrt(2.0)
    v = np.select([(a > 0) & (a >= b), (b > 0) & (b > a)], [0, 2], default=1)
    return np.where(v == 0, np.minimum(d_a0, d_ab),
           np.where(v == 2, np.minimum(d_b0, d_ab), np.minimum(d_a0, d_b0)))


def contested_stats(P_base, P_S, P_T):
    """Susceptibility null: an item is *doubly contested* when both single passes move its ALR
    coordinates farther than its base distance to the nearest verdict boundary.  The contested
    fraction is a sealed scale estimate for order disagreement — it counts items *capable* of
    order dependence, it is not a composite map and predicts no direction.  Pilot evidence
    (quick base_shared): right order of magnitude (0.105 vs 0.089 observed at α=0) but does not
    track the shared-fraction trend, and ~60% of observed flips fall outside the mask —
    enrichment/recall are scored so that insufficiency stays visible."""
    Xb = alr(P_base); dS = alr(P_S) - Xb; dT = alr(P_T) - Xb
    nS = np.linalg.norm(dS, axis=1); nT = np.linalg.norm(dT, axis=1)
    m = boundary_dist(Xb)
    mask = (nS > m) & (nT > m)
    cos = (dS * dT).sum(1) / np.maximum(nS * nT, 1e-9)
    return dict(mask=[bool(x) for x in mask], frac=float(mask.mean()),
                anti_frac=float((mask & (cos < 0.5)).mean()),
                mean_cos_moves=float(cos[mask].mean()) if mask.any() else float("nan"),
                pred_disagreement=float(mask.mean()))


def entropy(counts):
    p = counts / counts.sum(); p = p[p > 0]; return float(-(p * np.log2(p)).sum())


def join_info_loss(v_list):
    tup = list(zip(*v_list)); joined = [max(t) for t in tup]
    _, ct = np.unique([str(t) for t in tup], return_counts=True)
    _, cj = np.unique(joined, return_counts=True)
    return entropy(ct) - entropy(cj)


def lumpability_chi2(v_base, v_comp, M):
    N = joint(v_base, v_comp); chi = 0.0; df = 0
    for i in range(3):
        n = N[i].sum()
        if n < 5: continue
        e = n * M[i]; chi += float(((N[i] - e) ** 2 / np.maximum(e, 1e-9)).sum()); df += 2
    return chi, df, (float(1 - stats.chi2.cdf(chi, df)) if df else np.nan)


def r2(pred, obs):
    return float(1 - ((obs - pred) ** 2).sum() / ((obs - obs.mean(0)) ** 2).sum())


# ---------------------------------------------------------------- noise floors ---
def trace_noise(trace, tail=0.3):
    """Terminal gradient-noise proxy: sd of the detrended loss over the last `tail` fraction of steps."""
    t = np.asarray(trace, float)
    if len(t) < 8: return float("nan")
    k = max(4, int(len(t) * tail)); y = t[-k:]; x = np.arange(k)
    A = np.c_[x, np.ones(k)]; coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(np.std(y - A @ coef, ddof=2))


def logit_jitter_floor(P, sigma, n=200, seed=0):
    """Irreducible band from per-item logit jitter σ: spread of the verdict marginal and the
    self-disagreement rate between two independently jittered copies of the same checkpoint."""
    rng = np.random.default_rng(seed); L = np.log(np.clip(P, 1e-9, 1)); v0 = P.argmax(1)
    margs, dis, flips = [], [], []
    for _ in range(n):
        v1 = (L + rng.normal(0, sigma, L.shape)).argmax(1); v2 = (L + rng.normal(0, sigma, L.shape)).argmax(1)
        margs.append(marginal(v1)); dis.append(float(np.mean(v1 != v2))); flips.append(float(np.mean(v1 != v0)))
    margs = np.array(margs)
    return dict(sigma=float(sigma), tv_sd=float(np.mean([tv(m, marginal(v0)) for m in margs])),
                marg_sd=margs.std(0).tolist(), self_disagreement=float(np.mean(dis)), flip_rate=float(np.mean(flips)))


def item_bootstrap_floor(vA, vB, n=300, seed=0):
    """Eval-set sampling floor: sd of TV between marginals of two checkpoints under item resampling."""
    rng = np.random.default_rng(seed); N = len(vA); tvs = []; dis = []
    for _ in range(n):
        idx = rng.integers(0, N, N); tvs.append(tv(marginal(vA[idx]), marginal(vB[idx]))); dis.append(float(np.mean(vA[idx] != vB[idx])))
    return dict(tv_mean=float(np.mean(tvs)), tv_sd=float(np.std(tvs)), dis_sd=float(np.std(dis)))


def calibrate_sigma(P_ref, target_self_dis, lo=1e-3, hi=5.0, it=25):
    """σ_eff: logit jitter whose two-copy self-disagreement matches the *measured* replicate self-disagreement.
    (The raw loss-trace sd is dominated by batch composition and does not convert to endpoint wander directly;
    it is kept as a covariate — test whether σ_eff tracks it across cells.)"""
    if not np.isfinite(target_self_dis) or target_self_dis <= 0: return float("nan")
    for _ in range(it):
        mid = np.sqrt(lo * hi); d = logit_jitter_floor(P_ref, mid, n=60)["self_disagreement"]
        lo, hi = (mid, hi) if d < target_self_dis else (lo, mid)
    return float(np.sqrt(lo * hi))


# ---------------------------------------------------------------- predictors ---
def predict_composites(P_base, P_S, P_T):
    """From base and the two single passes only.  Three nulls of increasing structure:
       markov  – lumpable 3×3 verdict channel (label-aware, overlap-blind)
       alr     – affine map on log-ratio coordinates (geometry, label-blind)
       overlap – per-item verdict-triple null (label- and overlap-aware)"""
    vb, vS, vT = verdicts(P_base), verdicts(P_S), verdicts(P_T)
    Cb = marginal(vb)
    PhiS, PhiT = channel(vb, vS), channel(vb, vT)
    M_ST, M_TS = PhiS @ PhiT, PhiT @ PhiS
    Xb = alr(P_base)
    AS, bS = fit_affine(Xb, alr(P_S)); AT, bT = fit_affine(Xb, alr(P_T))
    A_ST, b_ST = compose_affine(AS, bS, AT, bT); A_TS, b_TS = compose_affine(AT, bT, AS, bS)
    P_ST_alr = alr_inv(apply_affine(Xb, A_ST, b_ST)); P_TS_alr = alr_inv(apply_affine(Xb, A_TS, b_TS))
    vST_alr, vTS_alr = verdicts(P_ST_alr), verdicts(P_TS_alr)
    vST_ov, vTS_ov = overlap_predict(vb, vS, vT, "ST"), overlap_predict(vb, vS, vT, "TS")
    ov = overlap_stats(vb, vS, vT)
    srt = np.sort(P_base, 1); margin = srt[:, -1] - srt[:, -2]
    return dict(
        PhiS=PhiS.tolist(), PhiT=PhiT.tolist(),
        comm_discrete=float(np.linalg.norm(PhiS @ PhiT - PhiT @ PhiS)),
        AS=AS.tolist(), AT=AT.tolist(), comm_alr=float(np.linalg.norm(AS @ AT - AT @ AS)),
        markov=dict(C_ST=(Cb @ M_ST).tolist(), C_TS=(Cb @ M_TS).tolist(), M_ST=M_ST.tolist(), M_TS=M_TS.tolist()),
        alr=dict(C_ST=marginal(vST_alr).tolist(), C_TS=marginal(vTS_alr).tolist(),
                 v_ST=vST_alr.tolist(), v_TS=vTS_alr.tolist(), P_ST=P_ST_alr.tolist(), P_TS=P_TS_alr.tolist(),
                 pred_disagreement=float(np.mean(vST_alr != vTS_alr))),
        overlap=dict(**ov, C_ST=marginal(vST_ov).tolist(), C_TS=marginal(vTS_ov).tolist(),
                     v_ST=vST_ov.tolist(), v_TS=vTS_ov.tolist(),
                     pred_disagreement=float(np.mean(vST_ov != vTS_ov))),
        contested=contested_stats(P_base, P_S, P_T),
        margin=margin.tolist(),
        Gamma_markov=(Cb @ M_ST - Cb @ M_TS).tolist(),
        Gamma_alr=(marginal(vST_alr) - marginal(vTS_alr)).tolist(),
        Gamma_overlap=(marginal(vST_ov) - marginal(vTS_ov)).tolist(),
    )


def _pred_block(Cpred_ST, Cpred_TS, vpred_ST, vpred_TS, Gpred, C, vST, vTS, Gamma):
    return dict(ST=tv(Cpred_ST, C["ST"]), TS=tv(Cpred_TS, C["TS"]),
                item_agree_ST=float(np.mean(np.array(vpred_ST) == vST)),
                item_agree_TS=float(np.mean(np.array(vpred_TS) == vTS)),
                Gamma_pred=list(Gpred), Gamma_err=float(np.abs(np.array(Gpred) - Gamma).sum() / 2),
                Gamma_sign_agree=float(np.mean(np.sign(Gpred) == np.sign(Gamma))),
                pred_disagreement=float(np.mean(np.array(vpred_ST) != np.array(vpred_TS))))


def score(P_base, P_S, P_T, P_ST, P_TS, pred, traces=None, bs=32, replicates=None):
    vb, vS, vT, vST, vTS = map(verdicts, (P_base, P_S, P_T, P_ST, P_TS))
    C = dict(base=marginal(vb), S=marginal(vS), T=marginal(vT), ST=marginal(vST), TS=marginal(vTS))
    N = joint(vST, vTS); sm = stuart_maxwell(N); bk = bowker(N)
    Gamma = C["ST"] - C["TS"]
    inter = 0.5 * (C["ST"] + C["TS"]) - C["S"] - C["T"] + C["base"]
    pa, pm, po = pred["alr"], pred["markov"], pred["overlap"]
    Cb = C["base"]
    lump = dict(ST=lumpability_chi2(vb, vST, np.array(pm["M_ST"])), TS=lumpability_chi2(vb, vTS, np.array(pm["M_TS"])))
    margin = np.array(pred["margin"]); dis = (vST != vTS)
    ov_dis = np.array(po["v_ST"]) != np.array(po["v_TS"])
    # markov has no per-item verdicts; use its row-composite applied to base verdict as a hard prediction
    vST_m = np.array(pm["M_ST"]).argmax(1)[vb]; vTS_m = np.array(pm["M_TS"]).argmax(1)[vb]
    pe = dict(
        markov=_pred_block(pm["C_ST"], pm["C_TS"], vST_m, vTS_m, pred["Gamma_markov"], C, vST, vTS, Gamma),
        alr=_pred_block(pa["C_ST"], pa["C_TS"], pa["v_ST"], pa["v_TS"], pred["Gamma_alr"], C, vST, vTS, Gamma),
        overlap=_pred_block(po["C_ST"], po["C_TS"], po["v_ST"], po["v_TS"], pred["Gamma_overlap"], C, vST, vTS, Gamma),
    )
    pe["alr"].update(r2_ST=r2(alr(np.array(pa["P_ST"])), alr(P_ST)), r2_TS=r2(alr(np.array(pa["P_TS"])), alr(P_TS)))
    if "contested" in pred:  # guard: absent in ledgers sealed before this null existed
        cm = np.array(pred["contested"]["mask"], bool)
        pe["contested"] = dict(
            pred_disagreement=pred["contested"]["frac"],
            dis_in=float(dis[cm].mean()) if cm.any() else np.nan,
            dis_out=float(dis[~cm].mean()) if (~cm).any() else np.nan,
            recall=float(dis[cm].sum() / max(dis.sum(), 1)),
            enrichment=float(dis[cm].mean() / max(dis[~cm].mean(), 1e-9)) if cm.any() and (~cm).any() else np.nan)
    pe["overlap"].update(disagree_in_overlap=float(np.mean(dis & ov_dis)), disagree_outside_overlap=float(np.mean(dis & ~ov_dis)),
                         overlap_recall=float(dis[ov_dis].mean()) if ov_dis.any() else np.nan)
    # ---- noise floors ----
    floors = dict(item_bootstrap=item_bootstrap_floor(vST, vTS))
    if traces:
        floors["loss_noise_sd"] = {k: trace_noise(traces[k]) for k in traces if traces[k]}
    if replicates and replicates.get("ST"):
        Pk = dict(ST=P_ST, TS=P_TS); rep = {}
        for k in ["ST", "TS"]:
            vk = verdicts(Pk[k]); rv = [verdicts(np.array(x)) for x in replicates[k]]
            sdis = [float(np.mean(v != vk)) for v in rv]; tvs = [tv(marginal(v), marginal(vk)) for v in rv]
            # pairwise between replicates too (unbiased two-copy estimate)
            allv = [vk] + rv; pair = [float(np.mean(allv[i] != allv[j])) for i in range(len(allv)) for j in range(i + 1, len(allv))]
            rep[k] = dict(self_dis=sdis, tv=tvs, pair_dis_mean=float(np.mean(pair)), tv_mean=float(np.mean(tvs)),
                          sigma_eff=calibrate_sigma(Pk[k], float(np.mean(pair))))
        floors["replicates"] = rep
        floors["order_disagreement_floor"] = float(0.5 * (rep["ST"]["pair_dis_mean"] + rep["TS"]["pair_dis_mean"]))
        floors["marginal_tv_floor"] = float(0.5 * (rep["ST"]["tv_mean"] + rep["TS"]["tv_mean"]))
        floors["excess_disagreement"] = float(dis.mean() - floors["order_disagreement_floor"])
        floors["disagreement_over_floor"] = float(dis.mean() / max(floors["order_disagreement_floor"], 1e-6))
    return dict(
        floors=floors,
        C={k: v.tolist() for k, v in C.items()},
        joint_ST_TS=N.tolist(), disagreement=float(dis.mean()),
        stuart_maxwell=sm, bowker=bk,
        Gamma=Gamma.tolist(), interaction=inter.tolist(), carryover=(0.5 * Gamma).tolist(),
        tv_ST_TS=tv(C["ST"], C["TS"]),
        pred_err=pe,
        lumpability={k: dict(chi2=v[0], df=v[1], p=v[2]) for k, v in lump.items()},
        disagree_margin=dict(mean_margin_disagree=float(margin[dis].mean()) if dis.any() else np.nan,
                             mean_margin_agree=float(margin[~dis].mean()) if (~dis).any() else np.nan,
                             auc=float(stats.mannwhitneyu(-margin[dis], -margin[~dis]).statistic / (dis.sum() * (~dis).sum()))
                             if dis.any() and (~dis).any() else np.nan),
        join_bits_lost=join_info_loss([vST, vTS]),
    )
