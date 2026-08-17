"""BCH/HVP direction test (lab notes §3; REQUIRES CHECKPOINTS + GPU).

To second order, theta_ST - theta_TS ~ eta*(H_S tau_T - H_T tau_S). Measures the cosine
between the observed weight-space order gap and that prediction, with reference cosines.
Reproduces the pre-registered failure (cos ~ 0.005 on the recorded battery).

    python bch_hvp.py <ckpt_dir> [alpha] [seed]
Run from euh_pkg/ (imports euh.model); pools rebuilt deterministically from config.
"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np, torch
from euh.model import NLI, load_data, encode, objective_loss, set_seed, device
from transformers import BertTokenizerFast

CK = sys.argv[1]
A = sys.argv[2] if len(sys.argv) > 2 else "1.0"
SEED = sys.argv[3] if len(sys.argv) > 3 else "0"
dev = device(); print("device", dev, flush=True)
tok = BertTokenizerFast.from_pretrained("bert-base-uncased")
base_rows, pass_rows, ev = load_data(60000, 3 * 6000 + 2000, 4000, 1234)

# reconstruct the deterministic pools exactly as sweep.py (disjoint, shared_frac=0, label-matched)
rng = np.random.default_rng(1234)
EH = [r for r in pass_rows if r["label"] in (0, 2)]; ALL = list(pass_rows)
rng.shuffle(EH); rng.shuffle(ALL)
S_rows = EH[:6000]; S_ids = {id(r) for r in S_rows}
rest = [r for r in ALL if id(r) not in S_ids]
U_own = [r for r in rest if r["label"] == 1]; EH_own = [r for r in rest if r["label"] != 1]
fU = sum(1 for r in ALL if r["label"] == 1) / len(ALL)
n_U = int(round(fU * 6000)); n_EH = 6000 - n_U
T_rows = U_own[:n_U] + EH_own[:n_EH]

def sd(p): return {k: (v.float() if v.is_floating_point() else v)
                   for k, v in torch.load(os.path.join(CK, p), map_location="cpu").items()}
base_sd = sd("base.pt")
tau = {}
for tag in ["S", "T", "ST", "TS"]:
    s = sd(f"a{A}_s{SEED}_{tag}.pt")
    tau[tag] = {k: s[k] - base_sd[k] for k in base_sd if base_sd[k].is_floating_point()}

m = NLI("bert-base-uncased").to(dev)
m.load_state_dict(base_sd)
params = [p for p in m.parameters() if p.requires_grad]
names = [k for k, p in m.named_parameters() if p.requires_grad]

def flat(d, keys): return torch.cat([d[k].flatten() for k in keys])

def hvp(rows, kind, vdict, n_batches=12, bs=16):
    vs = [vdict[k].to(dev) for k in names]
    acc = [torch.zeros_like(p) for p in params]
    set_seed(0)
    idx = np.random.permutation(len(rows))
    from torch.nn.attention import sdpa_kernel, SDPBackend
    for bi in range(n_batches):
        batch = [rows[j] for j in idx[bi * bs:(bi + 1) * bs]]
        b = encode(tok, batch, 64, dev)
        y = torch.tensor([r["label"] for r in batch], device=dev)
        with sdpa_kernel(SDPBackend.MATH):   # fused attention kernels lack double-backward
            loss = objective_loss(m(**b).float(), y, kind)
            g = torch.autograd.grad(loss, params, create_graph=True, allow_unused=True)
            gv = sum((gi * vi).sum() for gi, vi in zip(g, vs) if gi is not None)
            h = torch.autograd.grad(gv, params, allow_unused=True)
        for a, hi in zip(acc, h):
            if hi is not None: a += hi.detach() / n_batches
        m.zero_grad(set_to_none=True)
    return {k: a.cpu() for k, a in zip(names, acc)}

t0 = time.time()
HS_tT = hvp(S_rows, "binEH", tau["T"])
HT_tS = hvp(T_rows, "binU", tau["S"])
print(f"HVPs done {time.time()-t0:.0f}s", flush=True)

D = flat({k: tau["ST"][k] - tau["TS"][k] for k in names}, names)
P = flat(HS_tT, names) - flat(HT_tS, names)
tS, tT = flat(tau["S"], names), flat(tau["T"], names)
cos = lambda a, b: float((a @ b) / (a.norm() * b.norm()))
print(f"cos(D_obs, BCH pred) = {cos(D, P):+.4f}")
print(f"cos(D_obs, tau_S)    = {cos(D, tS):+.4f}")
print(f"cos(D_obs, tau_T)    = {cos(D, tT):+.4f}")
print(f"cos(tau_S, tau_T)    = {cos(tS, tT):+.4f}")
print(f"|D_obs| = {float(D.norm()):.3f}   |BCH dir| = {float(P.norm()):.3e}")
