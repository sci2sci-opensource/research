"""Token-classification model, data, enrichment (head widening), training and evaluation primitives."""
import random, numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from datasets import load_dataset
from transformers import AutoModel, BertTokenizerFast

LABELS0 = ["O", "PER", "LOC"]            # base language Σ0 (ORG/MISC occluded as O)
ENRICH_A, ENRICH_B = "ORG", "MISC"       # the two distinction-adding enrichments
FINAL = ["O", "PER", "LOC", "ORG", "MISC"]   # canonical name order for comparisons


def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s)


def device():
    if torch.cuda.is_available(): return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available(): return "mps"
    return "cpu"


class Tagger(nn.Module):
    def __init__(self, name, labels):
        super().__init__()
        self.enc = AutoModel.from_pretrained(name)
        self.labels = list(labels)
        self.head = nn.Linear(self.enc.config.hidden_size, len(self.labels))

    def forward(self, **b):
        return self.head(self.enc(**b).last_hidden_state)   # [B, T, k]


def widen(model, name, new_label):
    """Enrichment ι: same encoder weights, head gains one fresh row for the new category.
    New row ~0 with bias -2 (new category starts rare); old rows copied verbatim."""
    dev = next(model.parameters()).device
    m = Tagger(name, model.labels + [new_label]).to(dev)
    m.enc.load_state_dict(model.enc.state_dict())
    with torch.no_grad():
        k0 = len(model.labels)
        m.head.weight[:k0] = model.head.weight; m.head.bias[:k0] = model.head.bias
        m.head.weight[k0:].normal_(0, 0.02); m.head.bias[k0:] = -2.0
    m.eval(); return m


def clone(model, name):
    m = Tagger(name, model.labels).to(next(model.parameters()).device)
    m.load_state_dict(model.state_dict()); m.eval(); return m


def save_state(model):  # labels travel with the weights
    return dict(labels=list(model.labels), sd=model.state_dict())


def load_ckpt(path, name, dev="cpu"):
    blob = torch.load(path, map_location=dev)
    m = Tagger(name, blob["labels"]).to(dev)
    m.load_state_dict({k: (v.float() if v.is_floating_point() else v) for k, v in blob["sd"].items()})
    m.eval(); return m


# ---------------------------------------------------------------- data ---
CONLL_TAGS = ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC", "B-MISC", "I-MISC"]


def load_conll():
    """CoNLL-2003 as rows of {tokens, types} with IO type names (O/PER/LOC/ORG/MISC).
    Loaded from the HF parquet-converted branch (datasets>=3 no longer runs dataset scripts)."""
    from huggingface_hub import hf_hub_download
    files = {s: hf_hub_download("eriktks/conll2003", f"conll2003/{s}/0000.parquet",
                                repo_type="dataset", revision="refs/convert/parquet")
             for s in ("train", "validation")}
    ds = load_dataset("parquet", data_files=files)
    try:
        names = ds["train"].features["ner_tags"].feature.names
    except AttributeError:
        names = CONLL_TAGS
    typ = [n.split("-")[-1] if n != "O" else "O" for n in names]
    def rows(split):
        # column-wise extraction: avoids per-row pyarrow formatting, which access-violates
        # on this Windows/py39/pyarrow combination when iterated row by row
        toks, tags = ds[split]["tokens"], ds[split]["ner_tags"]
        return [dict(tokens=t, types=[typ[x] for x in g])
                for t, g in zip(toks, tags) if len(t) > 0]
    return rows("train"), rows("validation")


def project(types, kept):
    """The language's view of the gold: categories outside `kept` are occluded as O."""
    return [t if t in kept else "O" for t in types]


def pool_with(rows, typ, n, rng):
    """n sentences containing at least one token of the given category."""
    cand = [r for r in rows if typ in r["types"]]
    idx = rng.permutation(len(cand))[:n]
    if len(idx) < n: raise RuntimeError(f"only {len(idx)} sentences with {typ}, need {n}")
    return [cand[i] for i in idx]


# ---------------------------------------------------------- encoding ---
def encode_batch(tok, rows, max_len, dev, kept=None):
    """Tokenize; per-sample word_ids; labels (indices into `kept`) at first subtoken, -100 elsewhere.
    kept=None -> no labels (eval encoding)."""
    b = tok([r["tokens"] for r in rows], truncation=True, max_length=max_len,
            padding=True, is_split_into_words=True, return_tensors="pt")
    lab = None
    if kept is not None:
        li = {t: i for i, t in enumerate(kept)}
        lab = torch.full(b["input_ids"].shape, -100, dtype=torch.long)
        for s, r in enumerate(rows):
            proj = project(r["types"], kept); prev = None
            for pos, w in enumerate(b.word_ids(s)):
                if w is not None and w != prev: lab[s, pos] = li[proj[w]]
                prev = w
        lab = lab.to(dev)
    return {k: v.to(dev) for k, v in b.items()}, lab


def build_eval(tok, rows, max_len):
    """Fixed flat token index over the eval set: (sentence, position) per first-subtoken word,
    with full gold names and sentence ids. Identical for every checkpoint (same tokenizer)."""
    b = tok([r["tokens"] for r in rows], truncation=True, max_length=max_len,
            padding=True, is_split_into_words=True, return_tensors="pt")
    where, gold, sent = [], [], []
    for s, r in enumerate(rows):
        prev = None
        for pos, w in enumerate(b.word_ids(s)):
            if w is not None and w != prev:
                where.append((s, pos)); gold.append(r["types"][w]); sent.append(s)
            prev = w
    return dict(rows=rows, gold=np.array(gold), sent=np.array(sent),
                where=(np.array([w[0] for w in where]), np.array([w[1] for w in where])))


def retract_probs(P, labels, keep):
    """r: fold probability mass of categories outside `keep` into O; columns ordered as `keep`."""
    cols = {t: P[:, labels.index(t)] for t in labels}
    out = np.stack([cols[t] if t in keep else np.zeros(len(P)) for t in keep], 1)
    out[:, keep.index("O")] += sum(cols[t] for t in labels if t not in keep)
    return out


def align_probs(P, labels, order):
    """Permute columns into canonical name order (label sets must match)."""
    return P[:, [labels.index(t) for t in order]]


# ---------------------------------------------------------- training ---
def kl_retracted(cur_logits, ref_logits, cur_labels, ref_labels, mask):
    """Conservativity anchor: KL(ref || retract(cur)) on the OLD label space, over labelled tokens.
    Retraction in probability space: new-category mass folds into O."""
    curp = F.softmax(cur_logits.float(), -1)
    idx_old = [cur_labels.index(t) for t in ref_labels]
    fold = [i for i, t in enumerate(cur_labels) if t not in ref_labels]
    p = curp[..., idx_old]
    if fold: p = p.clone(); p[..., ref_labels.index("O")] += curp[..., fold].sum(-1)
    logq = torch.log(p.clamp_min(1e-9))[mask]
    logr = F.log_softmax(ref_logits.float(), -1)[mask]
    return F.kl_div(logr, logq, log_target=True, reduction="batchmean")


def train_pass(model, tok, rows, kept, epochs, lr, bs, max_len, seed,
               kl_beta=0.0, ref=None, log=None):
    dev = next(model.parameters()).device
    set_seed(seed); model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    scaler = torch.amp.GradScaler("cuda") if dev.type == "cuda" else None
    idx = list(range(len(rows))); step = 0; trace = []
    for _ in range(epochs):
        random.shuffle(idx)
        for i in range(0, len(idx), bs):
            batch = [rows[j] for j in idx[i:i + bs]]
            b, y = encode_batch(tok, batch, max_len, dev, kept=kept)
            use_amp = dev.type == "cuda"
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_amp):
                logits = model(**b)
                loss = F.cross_entropy(logits.float().flatten(0, 1), y.flatten(), ignore_index=-100)
                if kl_beta > 0 and ref is not None:
                    with torch.no_grad(): rl = ref(**b)
                    loss = loss + kl_beta * kl_retracted(logits, rl, model.labels, ref.labels, y >= 0)
            opt.zero_grad()
            if use_amp:
                scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
            else:
                loss.backward(); opt.step()
            step += 1; trace.append(float(loss.item()))
            if log and step % 25 == 0: log(f"      step {step} loss {loss.item():.4f}")
    model.eval(); model.loss_trace = trace; return model


@torch.no_grad()
def evaluate(model, tok, ev, max_len, bs=64):
    """Per-token probability matrix [N_flat, k] at the fixed eval token index."""
    dev = next(model.parameters()).device; model.eval()
    rows = ev["rows"]; outs = []
    for i in range(0, len(rows), bs):
        b, _ = encode_batch(tok, rows[i:i + bs], max_len, dev)
        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=(dev.type == "cuda")):
            lg = model(**b)
        outs.append(F.softmax(lg.float(), -1).cpu())
    T = max(o.shape[1] for o in outs)
    full = torch.cat([F.pad(o, (0, 0, 0, T - o.shape[1])) for o in outs])
    return full[ev["where"][0], ev["where"][1]].numpy()
