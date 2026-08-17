"""
Blinded enrichment-order protocol.

For each α (B-enrichment LR multiplier) and seed:
  1. train base on Σ0 (ORG/MISC occluded as O)          [resumed from ckpt if present]
  2. enrich A (+ORG) and B (+MISC) from base
  3. PREDICT both composites from base/A/B only; seal with SHA-256
  4. train (base+A)+B and (base+B)+A (+ replicates)
  5. score against the sealed predictions

Hardened from day one: cell-level resume (a kill costs the in-flight cell), every checkpoint
saved (base fp32, rest fp16, excluded from zips), idle models parked on CPU (8 GB cards spill
into WDDM shared memory and slow 10×), UTF-8 logging, timestamped run folders.
"""
import argparse, hashlib, json, os, sys, time, zipfile
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"): _s.reconfigure(encoding="utf-8", errors="replace")
from enrich.model import (Tagger, widen, clone, save_state, load_ckpt, load_conll, pool_with,
                          split_pools_same_type, split_type_by_entity,
                          build_eval, train_pass, evaluate, set_seed, device, hf_rev,
                          LABELS0, ENRICH_A, ENRICH_B)
from enrich import stats as S
from transformers import BertTokenizerFast


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="run")
    ap.add_argument("--exact_name", action="store_true", help="use --name as-is (no timestamp suffix)")
    ap.add_argument("--model", default="google/bert_uncased_L-2_H-128_A-2")
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.5, 1.0, 2.0])
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--kl_beta", type=float, default=0.2, help="conservativity anchor (retracted-KL)")
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--n_base", type=int, default=6000)
    ap.add_argument("--epochs_base", type=int, default=2)
    ap.add_argument("--n_pass", type=int, default=1500, help="sentences per enrichment pool")
    ap.add_argument("--epochs_pass", type=int, default=1)
    ap.add_argument("--n_eval", type=int, default=1500)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--max_len", type=int, default=96)
    ap.add_argument("--base_seed", type=int, default=1234)
    ap.add_argument("--no_zip", action="store_true")
    ap.add_argument("--n_replicate", type=int, default=1)
    ap.add_argument("--mode", choices=["enrich", "nullswap"], default="enrich",
                    help="enrich: the two passes add two genuinely different categories (ORG, MISC). "
                         "nullswap: MATCHED CONTROL — both passes add an arbitrary half of ONE category "
                         "(ORG#1, ORG#2) on disjoint sentence pools, so the two enrichments are "
                         "semantically the same operator and swapping them is null, while the structure "
                         "(two widens, two fresh labels, equal disjoint pools, same lr and anchor) is "
                         "unchanged. Isolates whether the order effect needs the distinctions to differ.")
    ap.add_argument("--save_ckpt", choices=["fp16", "fp32", "none"], default="fp16")
    ap.add_argument("--ckpt_dir", default=os.environ.get("CKPT_DIR", ""),
                    help="root dir for checkpoint storage (e.g. another drive); a runs/<name>/ckpt junction is created")
    args = ap.parse_args()
    if not args.exact_name:
        args.name = f"{args.name}_{time.strftime('%Y%m%d_%H%M%S')}"

    out = os.path.join("runs", args.name); os.makedirs(out, exist_ok=True)
    logf = open(os.path.join(out, "log.txt"), "a", encoding="utf-8")
    def log(s):
        line = f"{time.strftime('%H:%M:%S')} {s}"; print(line, flush=True); logf.write(line + "\n"); logf.flush()

    ckdir = os.path.join(args.ckpt_dir, args.name) if args.ckpt_dir else os.path.join(out, "ckpt")
    def _ensure_ckdir():
        os.makedirs(ckdir, exist_ok=True)
        link = os.path.join(out, "ckpt")
        if args.ckpt_dir and not os.path.exists(link):
            try:
                import _winapi; _winapi.CreateJunction(ckdir, link)
            except Exception:
                pass  # junction is a convenience; checkpoints still land in ckdir
    def save_ckpt(model, tag, force_fp32=False):
        if args.save_ckpt == "none": return
        _ensure_ckdir()
        blob = save_state(model)
        if args.save_ckpt == "fp16" and not force_fp32:
            blob["sd"] = {k: (v.half() if v.is_floating_point() else v) for k, v in blob["sd"].items()}
        torch.save(blob, os.path.join(ckdir, f"{tag}.pt"))

    # ---------- resume ----------
    ledger_path = os.path.join(out, "ledger.json")
    prev = None
    if os.path.exists(ledger_path):
        CRIT = ["model", "kl_beta", "lr", "n_base", "epochs_base", "n_pass", "epochs_pass",
                "n_eval", "bs", "max_len", "base_seed"]
        try:
            cand = json.load(open(ledger_path)); pm = cand.get("meta", {})
            if all(pm.get(k) == getattr(args, k) for k in CRIT):
                prev = cand; log(f"resume: found ledger with {len(prev.get('cells', {}))} finished cells")
            else:
                log("resume: existing ledger has a different config — starting fresh")
        except Exception as e:
            log(f"resume: could not read existing ledger ({e}) — starting fresh")

    dev = device(); log(f"device={dev}  model={args.model}")
    tok = BertTokenizerFast.from_pretrained(args.model, revision=hf_rev(args.model))
    train_rows, val_rows = load_conll()
    rng = np.random.default_rng(args.base_seed)
    base_rows = [train_rows[i] for i in rng.permutation(len(train_rows))[:args.n_base]]
    if args.mode == "nullswap":
        NAME_A, NAME_B = f"{ENRICH_A}#1", f"{ENRICH_A}#2"
        A_rows, B_rows, _tagged = split_pools_same_type(train_rows, ENRICH_A, args.n_pass, rng,
                                                        names=(NAME_A, NAME_B))
        # the eval gold must speak the same language as the passes (same deterministic split)
        val_rows = split_type_by_entity(val_rows, ENRICH_A, names=(NAME_A, NAME_B))
        # ...and so must every name-indexed statistic: the final language is O/PER/LOC/ORG#1/ORG#2
        S.set_final(LABELS0 + [NAME_A, NAME_B])
    else:
        NAME_A, NAME_B = ENRICH_A, ENRICH_B
        A_rows = pool_with(train_rows, ENRICH_A, args.n_pass, rng)
        B_rows = pool_with(train_rows, ENRICH_B, args.n_pass, rng)
    both = sum(1 for r in A_rows if NAME_B in r["types"]) + sum(1 for r in B_rows if NAME_A in r["types"])
    ev = build_eval(tok, val_rows[:args.n_eval], args.max_len)
    log(f"pools: base={len(base_rows)} A(+{NAME_A})={len(A_rows)} B(+{NAME_B})={len(B_rows)} "
        f"cross-category sentences={both}  eval tokens={len(ev['gold'])}  mode={args.mode}")

    LA, LB = LABELS0 + [NAME_A], LABELS0 + [NAME_B]

    # ---------- base ----------
    ck_base = os.path.join(ckdir, "base.pt")
    if prev is not None and os.path.exists(ck_base):
        log("resume: loading base from checkpoint")
        base = load_ckpt(ck_base, args.model, "cpu")
        P_base = np.array(prev["base"])
    else:
        set_seed(args.base_seed); base = Tagger(args.model, LABELS0).to(dev)
        log("training base (ORG/MISC occluded as O)")
        train_pass(base, tok, base_rows, LABELS0, args.epochs_base, args.lr, args.bs, args.max_len,
                   args.base_seed, log=log)
        P_base = evaluate(base, tok, ev, args.max_len)
        save_ckpt(base, "base", force_fp32=True)
        base.cpu()
        if dev == "cuda": torch.cuda.empty_cache()
    vb = S.verdict_names(P_base, base.labels)
    gold0 = S.retract_names(S.ev_gold(ev), LABELS0)
    log(f"base acc(R0) {float((vb == gold0).mean()):.3f}  C={np.round(S.marginal(vb), 3)}")

    ledger = dict(meta=vars(args), gold=S.ev_gold(ev).tolist(), sent=S.ev_sent(ev).tolist(),
                  labels0=LABELS0, base=P_base.tolist(), base_labels=list(base.labels), cells={})
    if prev is not None:
        ledger["cells"].update(prev.get("cells", {}))
    def dump():
        json.dump(ledger, open(ledger_path, "w"))

    def enrich(start, new_label, rows, kept, lr, seed, tag):
        """One enrichment pass: widen + train, KL-anchored to the start checkpoint (retracted)."""
        start.to(dev)
        m = widen(start, args.model, new_label)
        log(f"    pass {tag} [+{new_label}, n={len(rows)}, lr={lr:g}]")
        train_pass(m, tok, rows, kept, args.epochs_pass, lr, args.bs, args.max_len, seed,
                   kl_beta=args.kl_beta, ref=start, log=log)
        start.cpu()
        if dev == "cuda": torch.cuda.empty_cache()
        return m

    for alpha in args.alphas:
        lrB = args.lr * alpha
        for seed in args.seeds:
            key = f"a{alpha}_s{seed}"
            if prev is not None and key in ledger["cells"]:
                log(f"== α={alpha} seed={seed}: already in ledger — skipped (resume)"); continue
            log(f"== α={alpha} seed={seed}  lr_A={args.lr:g} lr_B={lrB:g}")
            # 1. single enrichments
            mA = enrich(base, NAME_A, A_rows, LA, args.lr, seed, "A")
            P_A = evaluate(mA, tok, ev, args.max_len); save_ckpt(mA, f"{key}_A"); mA.cpu()
            mB = enrich(base, NAME_B, B_rows, LB, lrB, seed, "B")
            P_B = evaluate(mB, tok, ev, args.max_len); save_ckpt(mB, f"{key}_B"); mB.cpu()
            if dev == "cuda": torch.cuda.empty_cache()
            # 2. sealed prediction — append-only: never overwrite an existing seal (a prior
            # aborted attempt may already have run composites for this cell); write alongside
            # and mark the cell resealed, excluding it from sealed-prediction claims.
            pred = S.predict_composites(P_base, list(base.labels), P_A, list(mA.labels), P_B, list(mB.labels))
            sealed = dict(alpha=alpha, seed=seed, time=time.time(), prediction=pred)
            h = sha(sealed); sealed["sha256"] = h
            sealed_path = os.path.join(out, f"sealed_{key}.json")
            resealed = os.path.exists(sealed_path)
            if resealed:
                sealed_path = os.path.join(out, f"sealed_{key}.reseal{int(time.time())}.json")
                log(f"    WARNING: seal for {key} already exists — writing {os.path.basename(sealed_path)}; "
                    f"cell marked resealed (excluded from sealed-prediction claims)")
            json.dump(sealed, open(sealed_path, "w"))
            cl = pred["claims"]
            log(f"    SEALED {h[:16]}…  claims A={cl['claim_A']:.3f} B={cl['claim_B']:.3f} "
                f"overlap={cl['overlap']:.3f} (ratio {cl['overlap_ratio']:.2f}) conflict={cl['conflict']:.4f} "
                f"pred-dis claims={cl['pred_disagreement']:.4f} markov={pred['markov']['pred_disagreement']:.4f} "
                f"‖[Φ]‖={pred['comm_markov']:.3f}")
            # 3. composites (+ replicates)
            mAB = enrich(mA, NAME_B, B_rows, LA + [NAME_B], lrB, seed + 100, "A→B")
            P_AB = evaluate(mAB, tok, ev, args.max_len); save_ckpt(mAB, f"{key}_AB"); lab_AB = list(mAB.labels); mAB.cpu()
            mBA = enrich(mB, NAME_A, A_rows, LB + [NAME_A], args.lr, seed + 100, "B→A")
            P_BA = evaluate(mBA, tok, ev, args.max_len); save_ckpt(mBA, f"{key}_BA"); lab_BA = list(mBA.labels); mBA.cpu()
            if dev == "cuda": torch.cuda.empty_cache()
            reps = dict(AB=[], BA=[])
            for r in range(1, args.n_replicate):
                mr = enrich(mA, NAME_B, B_rows, LA + [NAME_B], lrB, seed + 100 + 1000 * r, f"A→B rep{r}")
                reps["AB"].append((evaluate(mr, tok, ev, args.max_len).tolist(), list(mr.labels)))
                save_ckpt(mr, f"{key}_AB_rep{r}"); del mr
                mr = enrich(mB, NAME_A, A_rows, LB + [NAME_A], args.lr, seed + 100 + 1000 * r, f"B→A rep{r}")
                reps["BA"].append((evaluate(mr, tok, ev, args.max_len).tolist(), list(mr.labels)))
                save_ckpt(mr, f"{key}_BA_rep{r}"); del mr
                if dev == "cuda": torch.cuda.empty_cache()
            # 4. score
            sc = S.score(P_base, list(base.labels), P_A, list(mA.labels), P_B, list(mB.labels),
                         P_AB, lab_AB, P_BA, lab_BA, pred, ev,
                         replicates=reps if reps["AB"] else None)
            rt = sc["retraction"]; pe = sc["pred_err"]["claims"]
            log(f"    OBSERVED dis={sc['disagreement']:.4f} (ent {sc['disagreement_ent']:.4f}) "
                f"SM p={sc['stuart_maxwell'][2]:.3g} | claims agree {pe['agree_AB']:.3f}/{pe['agree_BA']:.3f} "
                f"in/out conflict {pe['dis_in_conflict']:.3f}/{pe['dis_outside_conflict']:.3f} "
                f"| retraction: AB~base {rt['AB_vs_base']:.3f} BA~base {rt['BA_vs_base']:.3f} "
                f"AB~BA {rt['AB_vs_BA']:.3f} old-lang order-dis {rt['order_dis_retracted']:.4f}")
            if "replicates" in sc["floors"]:
                f = sc["floors"]
                log(f"    FLOOR pair-dis AB={f['replicates']['AB']['pair_dis_mean']:.4f} "
                    f"BA={f['replicates']['BA']['pair_dis_mean']:.4f} | order-dis = {f['disagreement_over_floor']:.1f}× floor")
            imp = sc["improvement"]
            log("    IMPROVE " + "  ".join(f"{k}: R0err={v['err_R0']:.3f} R1err={v['err_R1']:.3f}"
                                           for k, v in imp.items()))
            ledger["cells"][key] = dict(alpha=alpha, seed=seed, lr_B=lrB, resealed=resealed,
                                        P=dict(A=P_A.tolist(), B=P_B.tolist(), AB=P_AB.tolist(), BA=P_BA.tolist()),
                                        labels=dict(A=list(mA.labels), B=list(mB.labels), AB=lab_AB, BA=lab_BA),
                                        replicates=reps, sealed_sha=h, prediction=pred, score=sc)
            dump()
            del mA, mB, mAB, mBA
            if dev == "cuda": torch.cuda.empty_cache()
    if args.save_ckpt != "none" and os.path.isdir(ckdir):
        fs = os.listdir(ckdir)
        log(f"checkpoints: {len(fs)} files, {sum(os.path.getsize(os.path.join(ckdir, f)) for f in fs) / 1e9:.2f} GB (excluded from zip)")
    log("sweep done")

    from viz import make_all
    summary = make_all(ledger_path, out)
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)
    if not args.no_zip:
        z = f"results_{args.name.replace('/', '_')}.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(out):
                dirs[:] = [d for d in dirs if d != "ckpt"]
                for f in files: zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), "runs"))
        log(f"result package: {z}")


if __name__ == "__main__":
    main()
