"""Interference grid: the commutative closure theta(a,b) = theta_base + a*tau_S + b*tau_T
(lab notes §3; REQUIRES CHECKPOINTS + GPU).

Evaluates a 6x6 grid of weight-space superpositions on the euh eval set and projects the
true sequential composites onto the {tau_S, tau_T} plane (explicit normal equations).

    python interference_grid.py <ckpt_dir> <out_dir> [alpha] [seed]
Run from euh_pkg/ (imports euh.model); eval set is rebuilt deterministically from config.
"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np, torch
from euh.model import NLI, load_data, evaluate, device
from euh import stats as S
from transformers import BertTokenizerFast

CK, OUT = sys.argv[1], sys.argv[2]
A = sys.argv[3] if len(sys.argv) > 3 else "1.0"
SEED = sys.argv[4] if len(sys.argv) > 4 else "0"
os.makedirs(OUT, exist_ok=True)
dev = device(); print("device", dev, flush=True)

tok = BertTokenizerFast.from_pretrained("bert-base-uncased")
_, _, ev = load_data(60000, 3 * 6000 + 2000, 4000, 1234)

def sd(path): return {k: (v.float() if v.is_floating_point() else v)
                      for k, v in torch.load(os.path.join(CK, path), map_location="cpu").items()}
base_sd = sd("base.pt")
tau_S = {k: sd(f"a{A}_s{SEED}_S.pt")[k] - base_sd[k] for k in base_sd if base_sd[k].is_floating_point()}
tau_T = {k: sd(f"a{A}_s{SEED}_T.pt")[k] - base_sd[k] for k in base_sd if base_sd[k].is_floating_point()}

m = NLI("bert-base-uncased").to(dev)

def eval_at(a, b):
    new = {k: (base_sd[k] + a * tau_S[k] + b * tau_T[k]) if k in tau_S else base_sd[k] for k in base_sd}
    m.load_state_dict(new); m.to(dev)
    return evaluate(m, tok, ev, 64)

grid_ab = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25]
G = {}
t0 = time.time()
for a in grid_ab:
    for b in grid_ab:
        P = eval_at(a, b)
        G[f"{a}_{b}"] = dict(C=S.marginal(S.verdicts(P)).tolist(), v=S.verdicts(P).astype(int).tolist())
        print(f"grid ({a},{b}) done  {time.time()-t0:.0f}s", flush=True)

def flat(d): return torch.cat([v.flatten() for v in d.values()])
uS, uT = flat(tau_S), flat(tau_T)
Gm = torch.tensor([[uS @ uS, uS @ uT], [uS @ uT, uT @ uT]], dtype=torch.float64)
res = {}
for tag in ["ST", "TS"]:
    comp = sd(f"a{A}_s{SEED}_{tag}.pt")
    x = flat({k: comp[k] - base_sd[k] for k in tau_S})
    rhs = torch.tensor([x @ uS, x @ uT], dtype=torch.float64)
    c = torch.linalg.solve(Gm, rhs)
    proj = c[0].float() * uS + c[1].float() * uT
    res[tag] = dict(coef=[float(v) for v in c], resid_frac=float((x - proj).norm() / x.norm()))
    print(tag, res[tag], flush=True)

json.dump(dict(grid=G, grid_ab=grid_ab, proj=res), open(os.path.join(OUT, "grid.json"), "w"))
print("written", os.path.join(OUT, "grid.json"))
