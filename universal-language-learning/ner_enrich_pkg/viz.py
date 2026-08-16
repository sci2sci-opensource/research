"""Figures + summary from a ledger.  python viz.py runs/<name>/ledger.json"""
import json, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enrich.stats import FINAL


def agg(cells, alphas, f):
    m, sd = [], []
    for a in alphas:
        vals = [f(c) for c in cells if c["alpha"] == a]
        vals = [v for v in vals if v is not None and np.isfinite(v)]
        m.append(np.mean(vals) if vals else np.nan); sd.append(np.std(vals) if vals else np.nan)
    return np.array(m), np.array(sd)


def make_all(ledger_path, outdir):
    L = json.load(open(ledger_path))
    cells = list(L["cells"].values())
    alphas = sorted({c["alpha"] for c in cells})
    figdir = os.path.join(outdir, "figures"); os.makedirs(figdir, exist_ok=True)

    fig, ax = plt.subplots(2, 2, figsize=(11, 8))
    a0 = ax[0, 0]
    m, sd = agg(cells, alphas, lambda c: c["score"]["disagreement"])
    a0.errorbar(alphas, m, sd, marker="o", label="order disagreement (all tokens)", capsize=2)
    m, sd = agg(cells, alphas, lambda c: c["score"]["disagreement_ent"])
    a0.errorbar(alphas, m, sd, marker="s", label="entity-relevant tokens", capsize=2)
    m, sd = agg(cells, alphas, lambda c: c["score"]["floors"].get("order_disagreement_floor"))
    a0.errorbar(alphas, m, sd, marker="^", ls=":", color="gray", label="replicate floor", capsize=2)
    m, sd = agg(cells, alphas, lambda c: c["score"]["pred_err"]["claims"]["pred_disagreement"])
    a0.errorbar(alphas, m, sd, marker="x", ls="--", label="sealed claims-null prediction", capsize=2)
    a0.set_xlabel("α (B-enrichment strength)"); a0.set_ylabel("token disagreement AB vs BA")
    a0.legend(fontsize=7); a0.set_title("Order effect vs floors and sealed null", fontsize=9)

    a1 = ax[0, 1]
    m, sd = agg(cells, alphas, lambda c: c["score"]["pred_err"]["claims"]["dis_in_conflict"])
    a1.errorbar(alphas, m, sd, marker="o", color="tab:orange", label="disagreement inside sealed conflict set", capsize=2)
    m, sd = agg(cells, alphas, lambda c: c["score"]["pred_err"]["claims"]["dis_outside_conflict"])
    a1.errorbar(alphas, m, sd, marker="s", color="tab:red", label="OUTSIDE (null cannot explain)", capsize=2)
    a1.set_xlabel("α"); a1.set_ylabel("disagreement rate"); a1.legend(fontsize=7)
    a1.set_title("Conflict-set localisation", fontsize=9)

    a2 = ax[1, 0]
    for k, lab, mk in [("AB_vs_base", "A→B retracted ~ base", "o"), ("BA_vs_base", "B→A retracted ~ base", "s"),
                       ("AB_vs_BA", "A→B ~ B→A (old language)", "^")]:
        m, sd = agg(cells, alphas, lambda c, k=k: c["score"]["retraction"][k])
        a2.errorbar(alphas, m, sd, marker=mk, label=lab, capsize=2)
    a2.set_xlabel("α"); a2.set_ylabel("agreement on Σ0")
    a2.legend(fontsize=7); a2.set_title("What each path leaves of the old language", fontsize=9)

    a3 = ax[1, 1]
    names = ["base", "A", "B", "AB", "BA"]
    w = 0.35; x = np.arange(len(names))
    for off, key, lab in [(-w / 2, "err_R0", "old readout R0"), (w / 2, "err_R1", "enriched readout R1")]:
        m = [agg(cells, alphas, lambda c, n=n, key=key: c["score"]["improvement"][n][key])[0].mean() for n in names]
        a3.bar(x + off, m, w, label=lab)
    a3.set_xticks(x); a3.set_xticklabels(names); a3.set_ylabel("token error")
    a3.legend(fontsize=7); a3.set_title("Improvement non-monotonicity across readouts (mean over cells)", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(figdir, "01_enrichment_order.png"), dpi=150); plt.close(fig)

    per_alpha = {}
    for a in alphas:
        g = lambda f: [round(float(x), 4) for x in agg(cells, [a], f)]
        per_alpha[str(a)] = dict(
            disagreement=g(lambda c: c["score"]["disagreement"]),
            disagreement_ent=g(lambda c: c["score"]["disagreement_ent"]),
            floor=g(lambda c: c["score"]["floors"].get("order_disagreement_floor")),
            over_floor=g(lambda c: c["score"]["floors"].get("disagreement_over_floor")),
            pred_dis_claims=g(lambda c: c["score"]["pred_err"]["claims"]["pred_disagreement"]),
            dis_in_conflict=g(lambda c: c["score"]["pred_err"]["claims"]["dis_in_conflict"]),
            dis_outside_conflict=g(lambda c: c["score"]["pred_err"]["claims"]["dis_outside_conflict"]),
            retraction_AB_vs_BA=g(lambda c: c["score"]["retraction"]["AB_vs_BA"]),
            old_lang_order_dis=g(lambda c: c["score"]["retraction"]["order_dis_retracted"]),
            conflict_rate=g(lambda c: c["prediction"]["claims"]["conflict"]),
            overlap_ratio=g(lambda c: c["prediction"]["claims"]["overlap_ratio"]),
        )
    return dict(alphas=alphas, seeds=sorted({c["seed"] for c in cells}), per_alpha=per_alpha)


if __name__ == "__main__":
    p = sys.argv[1]; s = make_all(p, os.path.dirname(p))
    json.dump(s, open(os.path.join(os.path.dirname(p), "summary.json"), "w"), indent=1)
    print(json.dumps(s["per_alpha"], indent=1))
