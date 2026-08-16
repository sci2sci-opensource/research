"""Model, data, training and evaluation primitives (shared by all scripts)."""
import random, numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from datasets import load_dataset
from transformers import AutoModel, BertTokenizerFast

LAB = ["E", "U", "H"]  # SNLI: 0 entail, 1 neutral, 2 contradiction


def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s)


class NLI(nn.Module):
    def __init__(self, name):
        super().__init__()
        self.enc = AutoModel.from_pretrained(name)
        self.head = nn.Linear(self.enc.config.hidden_size, 3)

    def forward(self, **b):
        return self.head(self.enc(**b).last_hidden_state[:, 0])


def device():
    if torch.cuda.is_available(): return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available(): return "mps"
    return "cpu"


def load_data(n_base, n_pass, n_eval, base_seed, pool=None):
    pool = pool or int((n_base + n_pass) * 1.05) + 500
    ds = load_dataset("stanfordnlp/snli")
    tr = [r for r in ds["train"].shuffle(seed=base_seed).select(range(pool)) if r["label"] != -1]
    ev = [r for r in ds["validation"] if r["label"] != -1][:n_eval]
    return tr[:n_base], tr[n_base:n_base + n_pass], ev


def encode(tok, rows, max_len, dev):
    b = tok([r["premise"] for r in rows], [r["hypothesis"] for r in rows],
            truncation=True, max_length=max_len, padding=True, return_tensors="pt")
    return {k: v.to(dev) for k, v in b.items()}


def objective_loss(logits, y, kind, cw=None):
    """kind: 'ce3' full 3-way CE (optionally class-weighted)
             'binEH' E-vs-H binary CE over the E/H logits only — no gradient about U
             'binU'  U-vs-notU binary CE on the marginal p(U) = softmax over 3 then U vs (E+H)"""
    if kind == "ce3":
        return F.cross_entropy(logits, y, weight=cw)
    if kind == "binEH":
        lg = logits[:, [0, 2]]; yy = (y == 2).long()          # 0→E, 1→H
        return F.cross_entropy(lg, yy)
    if kind == "binU":
        lp = F.log_softmax(logits, -1); pU = lp[:, 1]; pnot = torch.logsumexp(lp[:, [0, 2]], -1)
        yy = (y == 1).float()
        return -(yy * pU + (1 - yy) * pnot).mean()
    raise ValueError(kind)


def train_pass(model, tok, rows, epochs, lr, bs, max_len, seed, cw=None, kl_beta=0.0, ref=None, log=None, kind="ce3"):
    dev = next(model.parameters()).device
    set_seed(seed); model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    scaler = torch.amp.GradScaler("cuda") if dev.type == "cuda" else None
    w = torch.tensor(cw, dtype=torch.float, device=dev) if cw is not None else None
    idx = list(range(len(rows))); step = 0; trace = []
    for _ in range(epochs):
        random.shuffle(idx)
        for i in range(0, len(idx), bs):
            batch = [rows[j] for j in idx[i:i + bs]]
            b = encode(tok, batch, max_len, dev)
            y = torch.tensor([r["label"] for r in batch], device=dev)
            use_amp = dev.type == "cuda"
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_amp):
                logits = model(**b)
                loss = objective_loss(logits.float(), y, kind, w)
                if kl_beta > 0 and ref is not None:
                    with torch.no_grad(): rl = ref(**b)
                    loss = loss + kl_beta * F.kl_div(F.log_softmax(rl.float(), -1), F.log_softmax(logits.float(), -1),
                                                     log_target=True, reduction="batchmean")
            opt.zero_grad()
            if use_amp:
                scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
            else:
                loss.backward(); opt.step()
            step += 1; trace.append(float(loss.item()))
            if log and step % 25 == 0: log(f"      step {step} loss {loss.item():.4f}")
    model.eval(); model.loss_trace = trace; return model


@torch.no_grad()
def evaluate(model, tok, rows, max_len, bs=128):
    dev = next(model.parameters()).device; model.eval(); out = []
    for i in range(0, len(rows), bs):
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=(dev.type == "cuda")):
            lg = model(**encode(tok, rows[i:i + bs], max_len, dev))
        out.append(F.softmax(lg.float(), -1).cpu())
    return torch.cat(out).numpy()


def clone(model, name):
    m = NLI(name).to(next(model.parameters()).device); m.load_state_dict(model.state_dict()); m.eval(); return m


def load_ckpt(path, name, dev="cpu"):
    """Rehydrate a checkpoint saved by sweep.py (fp16 or fp32 state dict) into an fp32 NLI model."""
    m = NLI(name).to(dev)
    sd = torch.load(path, map_location=dev)
    m.load_state_dict({k: (v.float() if v.is_floating_point() else v) for k, v in sd.items()})
    m.eval(); return m
