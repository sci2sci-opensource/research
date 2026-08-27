"""Figures for the blinded sweep.  Called by sweep.py; also usable standalone:
    python viz.py runs/<name>/ledger.json
"""
import json, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from euh import stats as S

LAB = ["E", "U", "H"]; COL = {"E": "#2a9d8f", "U": "#8d99ae", "H": "#e76f51"}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def tern(p):
    """Δ² → 2D: E left, H right, U top."""
    p = np.asarray(p); return np.array([p[..., 2] + 0.5 * p[..., 1], p[..., 1] * np.sqrt(3) / 2]).T


def draw_simplex(ax):
    tri = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3) / 2], [0, 0]])
    ax.plot(tri[:, 0], tri[:, 1], color="k", lw=0.8)
    ax.text(-0.03, -0.03, "E", ha="right"); ax.text(1.03, -0.03, "H", ha="left"); ax.text(0.5, np.sqrt(3) / 2 + 0.03, "U", ha="center")
    ax.set_aspect("equal"); ax.axis("off")


def load(ledger_path):
    L = json.load(open(ledger_path))
    cells = L["cells"]; alphas = sorted({c["alpha"] for c in cells.values()}); seeds = sorted({c["seed"] for c in cells.values()})
    return L, cells, alphas, seeds


def agg(cells, alphas, f):
    """f(cell)->array; returns mean, sd over seeds per α."""
    M, Sd = [], []
    for a in alphas:
        x = np.array([f(c) for c in cells.values() if c["alpha"] == a]); M.append(x.mean(0)); Sd.append(x.std(0, ddof=1) if len(x) > 1 else 0 * x.mean(0))
    return np.array(M), np.array(Sd)


def make_all(ledger_path, out):
    L, cells, alphas, seeds = load(ledger_path)
    figdir = os.path.join(out, "figures"); os.makedirs(figdir, exist_ok=True)
    Pb = np.array(L["base"]); Cb = S.marginal(S.verdicts(Pb))
    summary = dict(alphas=alphas, seeds=seeds, base_C=Cb.tolist(), per_alpha={})

    # ---------- Fig 1: prediction vs empirical across α ----------
    fig, axs = plt.subplots(2, 3, figsize=(12, 6.5)); fig.suptitle("Blinded prediction vs empirical, across control α (neutral-objective strength)", fontsize=11)
    for k, lab in enumerate(LAB):
        ax = axs[0, k]
        for pth, ls in [("ST", "-"), ("TS", "--")]:
            m, sd = agg(cells, alphas, lambda c: c["score"]["C"][pth][k]); ax.errorbar(alphas, m, sd, ls=ls, marker="o", color=COL[lab], label=f"observed {pth}", capsize=2)
            m, _ = agg(cells, alphas, lambda c: c["prediction"]["alr"]["C_" + pth][k]); ax.plot(alphas, m, ls=ls, marker="x", color="k", alpha=0.7, label=f"ALR-pred {pth}")
            m, _ = agg(cells, alphas, lambda c: c["prediction"]["markov"]["C_" + pth][k]); ax.plot(alphas, m, ls=ls, marker="^", color="tab:purple", alpha=0.6, ms=4, label=f"Markov-pred {pth}")
            m, _ = agg(cells, alphas, lambda c: c["prediction"]["overlap"]["C_" + pth][k]); ax.plot(alphas, m, ls=ls, marker="D", color="tab:orange", alpha=0.8, ms=4, label=f"overlap-pred {pth}")
        ax.set_title(f"C(W)[{lab}]"); ax.set_xlabel("α")
        if k == 0: ax.legend(fontsize=6, ncol=2)
    ax = axs[1, 0]
    for k, lab in enumerate(LAB):
        m, sd = agg(cells, alphas, lambda c: c["score"]["Gamma"][k]); ax.errorbar(alphas, m, sd, marker="o", color=COL[lab], label=f"observed Γ[{lab}]", capsize=2)
        m, _ = agg(cells, alphas, lambda c: c["prediction"]["Gamma_alr"][k]); ax.plot(alphas, m, "x:", color=COL[lab], alpha=0.8)
        m, _ = agg(cells, alphas, lambda c: c["prediction"]["Gamma_overlap"][k]); ax.plot(alphas, m, "D--", color=COL[lab], alpha=0.8, ms=4, mfc="none")
    ax.axhline(0, color="k", lw=0.5); ax.set_title("Γ = C(ST)−C(TS): observed (o), sealed ALR (x), sealed overlap-null (◇)"); ax.set_xlabel("α"); ax.legend(fontsize=6)
    ax = axs[1, 1]
    m, sd = agg(cells, alphas, lambda c: c["score"]["disagreement"]); ax.errorbar(alphas, m, sd, marker="o", color="k", label="observed item disagreement", capsize=2)
    m, _ = agg(cells, alphas, lambda c: c["prediction"]["alr"]["pred_disagreement"]); ax.plot(alphas, m, "x:", color="k", label="predicted (ALR)")
    m, _ = agg(cells, alphas, lambda c: c["prediction"]["overlap"]["pred_disagreement"]); ax.plot(alphas, m, "D--", color="tab:orange", mfc="none", label="predicted (overlap null)")
    m, sd = agg(cells, alphas, lambda c: c["score"]["tv_ST_TS"]); ax.errorbar(alphas, m, sd, marker="s", color="tab:red", label="d_TV(C(ST),C(TS))", capsize=2)
    if all("order_disagreement_floor" in c["score"]["floors"] for c in cells.values()):
        m, sd = agg(cells, alphas, lambda c: c["score"]["floors"]["order_disagreement_floor"]); ax.fill_between(alphas, 0, m, color="gray", alpha=0.3, label="replicate floor: same-order pair disagreement")
    ax.set_title("readout distance vs revision distance"); ax.set_xlabel("α"); ax.legend(fontsize=7)
    ax = axs[1, 2]
    for name, key, c in [("ALR err ST", ("alr", "ST"), "k"), ("ALR err TS", ("alr", "TS"), "gray"), ("Markov err ST", ("markov", "ST"), "tab:purple"), ("Markov err TS", ("markov", "TS"), "orchid"), ("overlap err ST", ("overlap", "ST"), "tab:orange"), ("overlap err TS", ("overlap", "TS"), "gold")]:
        m, sd = agg(cells, alphas, lambda c, key=key: c["score"]["pred_err"][key[0]][key[1]]); ax.errorbar(alphas, m, sd, marker="o", color=c, label=name, capsize=2, ms=4)
    if all(c["score"]["floors"].get("replicates") for c in cells.values()):
        m, sd = agg(cells, alphas, lambda c: c["score"]["floors"]["marginal_tv_floor"]); ax.fill_between(alphas, 0, m, color="gray", alpha=0.3, label="replicate floor (composite seed noise)")
    ax.set_title("prediction error TV(pred, obs) vs noise floors"); ax.set_xlabel("α"); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(figdir, "01_prediction_vs_empirical.png"), dpi=150); plt.close(fig)

    # ---------- Fig 2: simplex trajectories ----------
    n = len(alphas); fig, axs = plt.subplots(1, n, figsize=(3.2 * n, 3.4)); axs = np.atleast_1d(axs)
    for ax, a in zip(axs, alphas):
        draw_simplex(ax); ax.set_title(f"α={a}", fontsize=9)
        for c in [c for c in cells.values() if c["alpha"] == a]:
            C = c["score"]["C"]; pr = c["prediction"]["alr"]
            b, s, t, st, ts = tern(Cb), tern(C["S"]), tern(C["T"]), tern(C["ST"]), tern(C["TS"])
            ax.plot(*np.array([b, s, st]).T, "-", color=COL["H"], alpha=0.7, lw=1); ax.plot(*np.array([b, t, ts]).T, "-", color=COL["U"], alpha=0.7, lw=1)
            ax.scatter(*st, marker="o", color=COL["H"], s=25, label="obs S→T"); ax.scatter(*ts, marker="o", color=COL["U"], s=25, label="obs T→S")
            ax.scatter(*tern(pr["C_ST"]), marker="x", color=COL["H"], s=30, label="ALR-pred S→T"); ax.scatter(*tern(pr["C_TS"]), marker="x", color=COL["U"], s=30, label="ALR-pred T→S")
            pb = c["prediction"]["overlap"]; ax.scatter(*tern(pb["C_ST"]), marker="D", facecolors="none", edgecolors=COL["H"], s=30, label="overlap-pred S→T"); ax.scatter(*tern(pb["C_TS"]), marker="D", facecolors="none", edgecolors=COL["U"], s=30, label="overlap-pred T→S")
        ax.scatter(*tern(Cb), marker="*", color="k", s=60, zorder=5)
    h, l = axs[0].get_legend_handles_labels(); axs[0].legend(h[:6], l[:6], fontsize=5.5, loc="upper left")
    fig.suptitle("Trajectories on Δ(Σ): base★ → single pass → composite (o observed, x sealed prediction)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(figdir, "02_simplex_trajectories.png"), dpi=150); plt.close(fig)

    # ---------- Fig 3: paired joint tables ST×TS (pooled over seeds) ----------
    fig, axs = plt.subplots(1, n, figsize=(3.0 * n, 3.2)); axs = np.atleast_1d(axs)
    for ax, a in zip(axs, alphas):
        N = sum(np.array(c["score"]["joint_ST_TS"]) for c in cells.values() if c["alpha"] == a); N = N / N.sum()
        ax.imshow(N, cmap="Blues", vmin=0, vmax=max(0.3, N.max()))
        for i in range(3):
            for j in range(3): ax.text(j, i, f"{N[i,j]:.2f}", ha="center", va="center", fontsize=8, color="k" if N[i, j] < 0.5 else "w")
        ax.set_xticks(range(3)); ax.set_xticklabels([f"TS={l}" for l in LAB]); ax.set_yticks(range(3)); ax.set_yticklabels([f"ST={l}" for l in LAB])
        sm = np.mean([c["score"]["stuart_maxwell"][2] for c in cells.values() if c["alpha"] == a]); ax.set_title(f"α={a}  off-diag={1-np.trace(N):.2f}\nSM p̄={sm:.2g}", fontsize=8)
    fig.suptitle("Paired verdict joint on shared items (rows S→T, cols T→S) — the object the marginals erase", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(figdir, "03_joint_tables.png"), dpi=150); plt.close(fig)

    # ---------- Fig 4: where does the order effect live? base margin ----------
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
    ax = axs[0]
    for a in alphas:
        for c in [c for c in cells.values() if c["alpha"] == a]:
            m = np.array(c["prediction"]["margin"]); dis = S.verdicts(np.array(c["P"]["ST"])) != S.verdicts(np.array(c["P"]["TS"]))
            bins = np.linspace(0, 1, 11); idx = np.digitize(m, bins) - 1
            rate = [dis[idx == i].mean() if (idx == i).sum() > 10 else np.nan for i in range(10)]
            ax.plot(0.5 * (bins[1:] + bins[:-1]), rate, "-o", ms=3, alpha=0.6, label=f"α={a}" if c["seed"] == min(seeds) else None)
    ax.set_xlabel("base top-2 probability margin (item)"); ax.set_ylabel("P(order flips verdict)"); ax.set_title("Prediction: order effect concentrates at verdict boundaries"); ax.legend(fontsize=7)
    ax = axs[1]
    m, sd = agg(cells, alphas, lambda c: c["score"]["disagree_margin"]["auc"]); ax.errorbar(alphas, m, sd, marker="o", color="k", capsize=2)
    ax.axhline(0.5, color="gray", ls=":"); ax.set_ylim(0.4, 1); ax.set_xlabel("α"); ax.set_title("AUC: low base-margin → flip"); 
    fig.tight_layout(); fig.savefig(os.path.join(figdir, "04_boundary_concentration.png"), dpi=150); plt.close(fig)

    # ---------- Fig 5: crossover decomposition + commutators + join loss ----------
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.4))
    ax = axs[0]; w = 0.25
    for k, lab in enumerate(LAB):
        mI, sI = agg(cells, alphas, lambda c: c["score"]["interaction"][k]); mC, sC = agg(cells, alphas, lambda c: c["score"]["carryover"][k])
        x = np.arange(len(alphas)) + (k - 1) * w
        ax.bar(x, mI, w, yerr=sI, color=COL[lab], alpha=0.5, label=f"sym. interaction [{lab}]"); ax.bar(x, mC, w, yerr=sC, color=COL[lab], alpha=1, hatch="//", label=f"antisym. carryover [{lab}]", bottom=0)
    ax.set_xticks(range(len(alphas))); ax.set_xticklabels(alphas); ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("α"); ax.set_title("Crossover decomposition of order effect"); ax.legend(fontsize=5.5, ncol=2)
    ax = axs[1]
    m, sd = agg(cells, alphas, lambda c: c["prediction"]["comm_discrete"]); ax.errorbar(alphas, m, sd, marker="o", color="tab:purple", label="‖[Φ_S,Φ_T]‖ (verdict channels)", capsize=2)
    ax2 = ax.twinx(); m, sd = agg(cells, alphas, lambda c: c["prediction"]["comm_alr"]); ax2.errorbar(alphas, m, sd, marker="x", color="k", label="‖[A_S,A_T]‖ (ALR channels)", capsize=2)
    ax.set_xlabel("α"); ax.set_title("Commutators: discrete vs continuous"); ax.legend(fontsize=7, loc="upper left"); ax2.legend(fontsize=7, loc="upper right"); ax2.spines["right"].set_visible(True)
    ax = axs[2]
    m, sd = agg(cells, alphas, lambda c: c["score"]["join_bits_lost"]); ax.errorbar(alphas, m, sd, marker="o", color="k", capsize=2)
    ax.set_xlabel("α"); ax.set_title("bits destroyed by publishing join(ST,TS)\ninstead of the verdict tuple")
    fig.tight_layout(); fig.savefig(os.path.join(figdir, "05_decomposition_commutators.png"), dpi=150); plt.close(fig)

    # ---------- Fig 6: item-level predicted vs observed ALR (first seed, each α) ----------
    fig, axs = plt.subplots(2, n, figsize=(3.0 * n, 6)); axs = np.array(axs).reshape(2, n)
    for j, a in enumerate(alphas):
        c = [c for c in cells.values() if c["alpha"] == a and c["seed"] == min(seeds)][0]
        for i, pth in enumerate(["ST", "TS"]):
            ax = axs[i, j]; pred = S.alr(np.array(c["prediction"]["alr"]["P_" + pth])); obs = S.alr(np.array(c["P"][pth]))
            flip = S.verdicts(np.array(c["P"]["ST"])) != S.verdicts(np.array(c["P"]["TS"]))
            ax.scatter(pred[~flip, 0], obs[~flip, 0], s=3, alpha=0.4, color="gray"); ax.scatter(pred[flip, 0], obs[flip, 0], s=4, alpha=0.7, color=COL["H"], label="order-flipped items")
            lim = [min(pred[:, 0].min(), obs[:, 0].min()), max(pred[:, 0].max(), obs[:, 0].max())]; ax.plot(lim, lim, "k:", lw=0.7)
            ax.set_title(f"α={a} {pth}: log(E/U) pred vs obs  R²={c['score']['pred_err']['alr']['r2_'+pth]:.2f}", fontsize=7)
            if i == 1: ax.set_xlabel("sealed prediction");
            if j == 0: ax.set_ylabel("observed"); ax.legend(fontsize=6)
    fig.suptitle("Item-level: composed-channel prediction vs observation (seed 0)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(figdir, "06_item_level_pred_vs_obs.png"), dpi=150); plt.close(fig)

    # ---------- Fig 7: overlap null — flip sets, co-dependence, where disagreement lives ----------
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.6))
    ax = axs[0]
    for nm, key, col in [("flip rate S", "flip_S", COL["H"]), ("flip rate T", "flip_T", COL["U"]), ("observed overlap", "overlap", "k"), ("indep. expectation", "overlap_indep", "gray")]:
        m, sd = agg(cells, alphas, lambda c, key=key: c["prediction"]["overlap"][key]); ax.errorbar(alphas, m, sd, marker="o", color=col, capsize=2, label=nm, ls=":" if "indep" in nm else "-")
    ax.set_xlabel("α"); ax.set_title("single-pass flip sets and their overlap", fontsize=9); ax.legend(fontsize=6)
    ax = axs[1]
    m, sd = agg(cells, alphas, lambda c: c["prediction"]["overlap"]["overlap_ratio"]); ax.errorbar(alphas, m, sd, marker="D", color="k", capsize=2, label="|A_S∩A_T| / (|A_S||A_T|/n)")
    ax.axhline(1, color="gray", ls=":"); ax.set_xlabel("α"); ax.set_title("co-dependence of the two flip sets (1 = independent)", fontsize=9); ax.legend(fontsize=6)
    ax = axs[2]
    m, sd = agg(cells, alphas, lambda c: c["score"]["pred_err"]["overlap"]["disagree_in_overlap"]); ax.errorbar(alphas, m, sd, marker="o", color="tab:orange", capsize=2, label="observed disagreement inside predicted overlap")
    m, sd = agg(cells, alphas, lambda c: c["score"]["pred_err"]["overlap"]["disagree_outside_overlap"]); ax.errorbar(alphas, m, sd, marker="s", color="tab:red", capsize=2, label="observed disagreement OUTSIDE (null cannot explain)")
    m, sd = agg(cells, alphas, lambda c: c["prediction"]["overlap"]["pred_disagreement"]); ax.plot(alphas, m, "D--", color="k", mfc="none", label="predicted disagreement (overlap null)")
    ax.set_xlabel("α"); ax.set_title("where the order effect lives", fontsize=9); ax.legend(fontsize=6)
    fig.tight_layout(); fig.savefig(os.path.join(figdir, "07_overlap_null.png"), dpi=150); plt.close(fig)

    # ---------- summary numbers ----------
    for a in alphas:
        cs = [c for c in cells.values() if c["alpha"] == a]
        g = lambda f: (float(np.mean([f(c) for c in cs])), float(np.std([f(c) for c in cs], ddof=1)) if len(cs) > 1 else 0.0)
        summary["per_alpha"][str(a)] = dict(
            Gamma_obs=np.mean([c["score"]["Gamma"] for c in cs], 0).tolist(), Gamma_pred_alr=np.mean([c["prediction"]["Gamma_alr"] for c in cs], 0).tolist(),
            disagreement=g(lambda c: c["score"]["disagreement"]), pred_disagreement=g(lambda c: c["prediction"]["alr"]["pred_disagreement"]),
            tv_ST_TS=g(lambda c: c["score"]["tv_ST_TS"]), stuart_maxwell_p=g(lambda c: c["score"]["stuart_maxwell"][2]),
            alr_err_ST=g(lambda c: c["score"]["pred_err"]["alr"]["ST"]), alr_err_TS=g(lambda c: c["score"]["pred_err"]["alr"]["TS"]),
            markov_err_ST=g(lambda c: c["score"]["pred_err"]["markov"]["ST"]), markov_err_TS=g(lambda c: c["score"]["pred_err"]["markov"]["TS"]),
            item_agree_ST=g(lambda c: c["score"]["pred_err"]["alr"]["item_agree_ST"]), item_agree_TS=g(lambda c: c["score"]["pred_err"]["alr"]["item_agree_TS"]),
            Gamma_pred_overlap=np.mean([c["prediction"]["Gamma_overlap"] for c in cs], 0).tolist(),
            overlap_err_ST=g(lambda c: c["score"]["pred_err"]["overlap"]["ST"]), overlap_err_TS=g(lambda c: c["score"]["pred_err"]["overlap"]["TS"]),
            overlap_item_agree_ST=g(lambda c: c["score"]["pred_err"]["overlap"]["item_agree_ST"]), overlap_item_agree_TS=g(lambda c: c["score"]["pred_err"]["overlap"]["item_agree_TS"]),
            overlap_Gamma_sign_agree=g(lambda c: c["score"]["pred_err"]["overlap"]["Gamma_sign_agree"]),
            overlap_ratio=g(lambda c: c["prediction"]["overlap"]["overlap_ratio"]),
            disagree_in_overlap=g(lambda c: c["score"]["pred_err"]["overlap"]["disagree_in_overlap"]), disagree_outside_overlap=g(lambda c: c["score"]["pred_err"]["overlap"]["disagree_outside_overlap"]),
            sealed_sha=[c["sealed_sha"] for c in cs])
    return summary


if __name__ == "__main__":
    p = sys.argv[1]; s = make_all(p, os.path.dirname(p)); json.dump(s, open(os.path.join(os.path.dirname(p), "summary.json"), "w"), indent=1); print(json.dumps(s["per_alpha"], indent=1))
