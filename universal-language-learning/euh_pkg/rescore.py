"""Recompute predictions + scores + figures + summary from an existing ledger (no training).
    python rescore.py runs/<name>/ledger.json
Predictions recomputed here are retrodictions unless the ledger's sealed_sha matches (it won't for new predictors)."""
import json, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from euh import stats as S
from viz import make_all
p = sys.argv[1]; L = json.load(open(p)); Pb = np.array(L["base"])
for key, c in L["cells"].items():
    P = {k: np.array(v) for k, v in c["P"].items()}
    pred = S.predict_composites(Pb, P["S"], P["T"])
    reps = c.get("replicates") if c.get("replicates", {}).get("ST") else None
    sc = S.score(Pb, P["S"], P["T"], P["ST"], P["TS"], pred, traces=c.get("traces"), bs=L["meta"].get("bs", 32), replicates=reps)
    c["prediction"] = pred; c["score"] = sc; c["rescored"] = True
    print(f"{key}: Γ={np.round(sc['Gamma'],3)} dis={sc['disagreement']:.3f} | overlap: err {sc['pred_err']['overlap']['ST']:.3f}/{sc['pred_err']['overlap']['TS']:.3f} "
          f"agree {sc['pred_err']['overlap']['item_agree_ST']:.2f}/{sc['pred_err']['overlap']['item_agree_TS']:.2f} sign {sc['pred_err']['overlap']['Gamma_sign_agree']:.2f} "
          f"in/out {sc['pred_err']['overlap']['disagree_in_overlap']:.3f}/{sc['pred_err']['overlap']['disagree_outside_overlap']:.3f} "
          f"| alr err {sc['pred_err']['alr']['ST']:.3f}/{sc['pred_err']['alr']['TS']:.3f} | markov err {sc['pred_err']['markov']['ST']:.3f}/{sc['pred_err']['markov']['TS']:.3f}"
          + (f" | FLOOR pair-dis {sc['floors']['replicates']['ST']['pair_dis_mean']:.3f}/{sc['floors']['replicates']['TS']['pair_dis_mean']:.3f} → order-dis = {sc['floors']['disagreement_over_floor']:.1f}× floor" if 'replicates' in sc['floors'] else " | (no replicates → no floor)"))
out = os.path.dirname(p); json.dump(L, open(os.path.join(out, "ledger_rescored.json"), "w"))
s = make_all(os.path.join(out, "ledger_rescored.json"), out); json.dump(s, open(os.path.join(out, "summary.json"), "w"), indent=1)
print("figures + summary regenerated in", out)
