"""
Measurement core for language-enrichment order dependence.  All verdicts are label NAMES
(np arrays of str) so checkpoints with different head orders compare safely.

claims_X        tokens where single enrichment X changed the verdict vs base
conflict set    claims_A ∩ claims_B with different labels — the only place the claims null
                allows an order effect
retraction r    new-category verdicts fold to O — the composite's residue in the old language
R0 / R1         old readout (retracted preds, occluded gold) / enriched readout (full gold)
"""
import numpy as np
from scipy import stats

FINAL = ["O", "PER", "LOC", "ORG", "MISC"]


def verdict_names(P, labels):
    return np.array(labels)[P.argmax(1)]


def marginal(v, order=FINAL):
    return np.array([(v == t).mean() for t in order])


def joint(v1, v2, order=FINAL):
    k = len(order); li = {t: i for i, t in enumerate(order)}
    N = np.zeros((k, k))
    for a, b in zip(v1, v2): N[li[a], li[b]] += 1
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
    for i in range(N.shape[0]):
        for j in range(i + 1, N.shape[0]):
            t = N[i, j] + N[j, i]
            if t > 0: s += (N[i, j] - N[j, i]) ** 2 / t; df += 1
    return s, df, (float(1 - stats.chi2.cdf(s, df)) if df else np.nan)


def retract_names(v, keep):
    return np.where(np.isin(v, list(keep)), v, "O")


def channel(v_from, v_to, order=FINAL):
    N = joint(v_from, v_to, order) + 0.5
    return N / N.sum(1, keepdims=True)


def token_f1(v, gold, types):
    """Token-level one-vs-rest F1 per type + macro over entity types (span F1 is a TODO)."""
    out = {}
    for t in types:
        tp = float(((v == t) & (gold == t)).sum()); fp = float(((v == t) & (gold != t)).sum())
        fn = float(((v != t) & (gold == t)).sum())
        out[t] = 2 * tp / max(2 * tp + fp + fn, 1e-9)
    ent = [t for t in types if t != "O"]
    out["macro_ent"] = float(np.mean([out[t] for t in ent])) if ent else np.nan
    return out


# ---------------------------------------------------------------- sealed predictors ---
def claims_null(vb, vA, vB):
    """Per-token composite prediction: base overwritten by first pass's claims, then second's.
    Orders differ only on the conflict set (both claim, different labels)."""
    cA, cB = vA != vb, vB != vb
    conflict = cA & cB & (vA != vB)
    vAB = vb.copy(); vAB[cA] = vA[cA]; vAB[cB] = vB[cB]      # B (second) wins conflicts
    vBA = vb.copy(); vBA[cB] = vB[cB]; vBA[cA] = vA[cA]      # A (second) wins conflicts
    return dict(v_AB=vAB.tolist(), v_BA=vBA.tolist(),
                claim_A=float(cA.mean()), claim_B=float(cB.mean()),
                overlap=float((cA & cB).mean()), conflict=float(conflict.mean()),
                conflict_mask=[bool(x) for x in conflict],
                overlap_indep=float(cA.mean() * cB.mean()),
                overlap_ratio=float((cA & cB).mean() / max(cA.mean() * cB.mean(), 1e-9)),
                pred_disagreement=float(conflict.mean()))


def predict_composites(P_base, lab_base, P_A, lab_A, P_B, lab_B):
    """From base and the two single enrichments only.  All in name space."""
    vb, vA, vB = (verdict_names(P_base, lab_base), verdict_names(P_A, lab_A),
                  verdict_names(P_B, lab_B))
    cl = claims_null(vb, vA, vB)
    PhiA, PhiB = channel(vb, vA), channel(vb, vB)
    M_AB, M_BA = PhiA @ PhiB, PhiB @ PhiA
    Cb = marginal(vb)
    idx = {t: i for i, t in enumerate(FINAL)}
    vb_i = np.array([idx[t] for t in vb])
    v_AB_m = np.array(FINAL)[M_AB.argmax(1)[vb_i]]
    v_BA_m = np.array(FINAL)[M_BA.argmax(1)[vb_i]]
    return dict(
        claims=cl,
        markov=dict(C_AB=(Cb @ M_AB).tolist(), C_BA=(Cb @ M_BA).tolist(),
                    v_AB=v_AB_m.tolist(), v_BA=v_BA_m.tolist(),
                    pred_disagreement=float((v_AB_m != v_BA_m).mean())),
        last_writer=dict(v_AB=vB.tolist(), v_BA=vA.tolist()),
        base=dict(v=vb.tolist()),
        comm_markov=float(np.linalg.norm(PhiA @ PhiB - PhiB @ PhiA)),
        v_singles=dict(base=vb.tolist(), A=vA.tolist(), B=vB.tolist()),
    )


# ---------------------------------------------------------------- floors ---
def sentence_bootstrap_floor(vX, vY, sent, n=300, seed=0):
    """Sentence-level resampling floor for the disagreement rate (tokens correlate within entities)."""
    rng = np.random.default_rng(seed); sids = np.unique(sent); tvs, dis = [], []
    for _ in range(n):
        pick = rng.choice(sids, len(sids), replace=True)
        m = np.concatenate([np.flatnonzero(sent == s) for s in pick])
        dis.append(float((vX[m] != vY[m]).mean()))
        tvs.append(0.5 * float(np.abs(marginal(vX[m]) - marginal(vY[m])).sum()))
    return dict(dis_mean=float(np.mean(dis)), dis_sd=float(np.std(dis)),
                tv_mean=float(np.mean(tvs)), tv_sd=float(np.std(tvs)))


# ---------------------------------------------------------------- scoring ---
def _agree(pred, obs): return float((np.asarray(pred) == obs).mean())


def improvement_table(preds, gold):
    """PT Prop 6.4 empirically: per checkpoint, error under the old readout R0 (retracted
    predictions, occluded gold) and the enriched readout R1 (full gold)."""
    keep = ["O", "PER", "LOC"]
    gold0 = retract_names(gold, keep)
    out = {}
    for name, v in preds.items():
        v = np.asarray(v)
        out[name] = dict(err_R1=float((v != gold).mean()),
                         err_R0=float((retract_names(v, keep) != gold0).mean()),
                         f1_R1=token_f1(v, gold, FINAL)["macro_ent"])
    return out


def score(P_base, lab_base, P_A, lab_A, P_B, lab_B, P_AB, lab_AB, P_BA, lab_BA,
          pred, ev, replicates=None):
    gold, sent = ev_gold(ev), ev_sent(ev)
    vb = verdict_names(P_base, lab_base)
    vA, vB = verdict_names(P_A, lab_A), verdict_names(P_B, lab_B)
    vAB, vBA = verdict_names(P_AB, lab_AB), verdict_names(P_BA, lab_BA)
    dis = vAB != vBA
    ent = (gold != "O") | (vAB != "O") | (vBA != "O")        # entity-relevant tokens
    N = joint(vAB, vBA)
    cl = pred["claims"]; cmask = np.array(cl["conflict_mask"], bool)
    pe = {}
    for name, pr in [("claims", cl), ("markov", pred["markov"]), ("last_writer", pred["last_writer"])]:
        pe[name] = dict(agree_AB=_agree(pr["v_AB"], vAB), agree_BA=_agree(pr["v_BA"], vBA))
    pe["base"] = dict(agree_AB=_agree(pred["base"]["v"], vAB), agree_BA=_agree(pred["base"]["v"], vBA))
    pe["claims"].update(
        pred_disagreement=cl["pred_disagreement"],
        dis_in_conflict=float(dis[cmask].mean()) if cmask.any() else np.nan,
        dis_outside_conflict=float(dis[~cmask].mean()) if (~cmask).any() else np.nan,
        conflict_recall=float(dis[cmask].sum() / max(dis.sum(), 1)))
    # ---- retraction: what each path leaves of the old language ----
    keep = ["O", "PER", "LOC"]
    rAB, rBA, rb = retract_names(vAB, keep), retract_names(vBA, keep), retract_names(vb, keep)
    retr = dict(AB_vs_base=_agree(rAB, rb), BA_vs_base=_agree(rBA, rb),
                AB_vs_BA=_agree(rAB, rBA),
                order_dis_retracted=float((rAB != rBA).mean()),
                order_dis_full=float(dis.mean()))
    # ---- floors ----
    floors = dict(bootstrap=sentence_bootstrap_floor(vAB, vBA, sent))
    if replicates and replicates.get("AB"):
        rep = {}
        for key, (Pk, labk) in dict(AB=(P_AB, lab_AB), BA=(P_BA, lab_BA)).items():
            vk = verdict_names(Pk, labk)
            rv = [verdict_names(np.array(p), l) for p, l in replicates[key]]
            allv = [vk] + rv
            pair = [float((allv[i] != allv[j]).mean()) for i in range(len(allv)) for j in range(i + 1, len(allv))]
            rep[key] = dict(pair_dis_mean=float(np.mean(pair)))
        floors["replicates"] = rep
        floors["order_disagreement_floor"] = 0.5 * (rep["AB"]["pair_dis_mean"] + rep["BA"]["pair_dis_mean"])
        floors["disagreement_over_floor"] = float(dis.mean() / max(floors["order_disagreement_floor"], 1e-6))
    sm, bk = stuart_maxwell(N), bowker(N)
    return dict(
        C=dict(base=marginal(vb).tolist(), A=marginal(vA).tolist(), B=marginal(vB).tolist(),
               AB=marginal(vAB).tolist(), BA=marginal(vBA).tolist()),
        joint_AB_BA=N.tolist(), disagreement=float(dis.mean()),
        disagreement_ent=float(dis[ent].mean()) if ent.any() else np.nan,
        stuart_maxwell=sm, bowker=bk,
        tv_AB_BA=0.5 * float(np.abs(marginal(vAB) - marginal(vBA)).sum()),
        pred_err=pe, retraction=retr, floors=floors,
        improvement=improvement_table(
            dict(base=vb, A=vA, B=vB, AB=vAB, BA=vBA), gold),
    )


def ev_gold(ev): return np.asarray(ev["gold"])
def ev_sent(ev): return np.asarray(ev["sent"])
