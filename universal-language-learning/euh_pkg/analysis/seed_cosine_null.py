"""Seed-cosine null for the interference claims (lab notes §3; REQUIRES CHECKPOINTS).

  A. first-position seed null:   cos(tau_X^seed_i, tau_X^seed_j) - same objective/pool/start
  B. second-position seed null:  cos(d_X@ctx across replicate seeds)
  C. cross-context:              cos(d_T@S, tau_T) and cos(d_S@T, tau_S)
Random-vector baseline in n~110M dims: 1/sqrt(n) ~ 1e-4.

    python seed_cosine_null.py <ckpt_dir> [alpha]
    # ckpt_dir: the base_strength ckpt directory of a full battery (fp16 .pt state dicts)
"""
import itertools, os, sys
import torch

CK = sys.argv[1]
A = sys.argv[2] if len(sys.argv) > 2 else "1.0"

def flat(path):
    sd = torch.load(os.path.join(CK, path), map_location="cpu")
    return torch.cat([v.float().flatten() for v in sd.values() if v.is_floating_point()])

def cos(a, b): return float((a @ b) / (a.norm() * b.norm()))

base = flat("base.pt")
tau_S = {s: flat(f"a{A}_s{s}_S.pt") - base for s in (0, 1, 2)}
tau_T = {s: flat(f"a{A}_s{s}_T.pt") - base for s in (0, 1, 2)}
S0 = flat(f"a{A}_s0_S.pt"); T0 = flat(f"a{A}_s0_T.pt")
d_TatS = {0: flat(f"a{A}_s0_ST.pt") - S0, 1: flat(f"a{A}_s0_ST_rep1.pt") - S0, 2: flat(f"a{A}_s0_ST_rep2.pt") - S0}
d_SatT = {0: flat(f"a{A}_s0_TS.pt") - T0, 1: flat(f"a{A}_s0_TS_rep1.pt") - T0, 2: flat(f"a{A}_s0_TS_rep2.pt") - T0}
n = base.numel()
print(f"dim = {n:,}   random-vector cos ~ {n**-0.5:.1e}\n")

def report(name, pairs):
    print(f"{name}: " + "  ".join(f"{cos(a, b):+.3f}" for a, b in pairs))

print("A. first-position seed-to-seed:")
report("  tau_S seed pairs", [(tau_S[i], tau_S[j]) for i, j in itertools.combinations((0, 1, 2), 2)])
report("  tau_T seed pairs", [(tau_T[i], tau_T[j]) for i, j in itertools.combinations((0, 1, 2), 2)])
print("B. second-position seed-to-seed (replicates):")
report("  d_T@S rep pairs ", [(d_TatS[i], d_TatS[j]) for i, j in itertools.combinations((0, 1, 2), 2)])
report("  d_S@T rep pairs ", [(d_SatT[i], d_SatT[j]) for i, j in itertools.combinations((0, 1, 2), 2)])
print("C. cross-context (same objective, different start):")
report("  cos(d_T@S, tau_T)", [(d_TatS[i], tau_T[0]) for i in (0, 1, 2)])
report("  cos(d_S@T, tau_S)", [(d_SatT[i], tau_S[0]) for i in (0, 1, 2)])
print("D. reference cos(tau_S, tau_T):", f"{cos(tau_S[0], tau_T[0]):+.3f}")
print("   norms:", " ".join(f"{v.norm():.2f}" for v in (tau_S[0], tau_T[0], d_TatS[0], d_SatT[0])))

# plane projections via explicit normal equations (float64) - do NOT use large-m lstsq,
# it returned artifact coefficients on this problem
G = torch.tensor([[tau_S[0] @ tau_S[0], tau_S[0] @ tau_T[0]],
                  [tau_S[0] @ tau_T[0], tau_T[0] @ tau_T[0]]], dtype=torch.float64)
for tag, x in [("ST", flat(f"a{A}_s0_ST.pt") - base), ("TS", flat(f"a{A}_s0_TS.pt") - base)]:
    rhs = torch.tensor([x @ tau_S[0], x @ tau_T[0]], dtype=torch.float64)
    c = torch.linalg.solve(G, rhs)
    proj = c[0].float() * tau_S[0] + c[1].float() * tau_T[0]
    print(f"{tag}: coef=({c[0]:.3f}, {c[1]:.3f})  resid_frac={(x-proj).norm()/x.norm():.3f}")
