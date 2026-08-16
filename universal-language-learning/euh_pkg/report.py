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
    json.dump(dict(hypotheses=ledger_json, bayes=bayes_json), open(os.path.join(out, "hypotheses.json"), "w"), indent=1)
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
