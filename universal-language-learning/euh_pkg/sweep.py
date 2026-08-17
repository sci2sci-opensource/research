"""
Blinded control-slider protocol.

For each α (strength of the neutral objective T; S fixed) and each seed:
  1. train S and T from base (single passes)
  2. PREDICT S→T and T→S from base, S, T only; write predictions + SHA-256 to a sealed file
  3. train S→T and T→S
  4. score observed composites against the sealed predictions

Everything (probabilities per item per checkpoint, predictions, scores, config, hashes) is written to
runs/<name>/ and packed into results_<name>.zip at the end.
"""
import argparse, hashlib, json, os, shutil, sys, time, zipfile
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Windows consoles default to a legacy codepage that can't encode α/Γ/‖ — force UTF-8, degrade gracefully
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"): _s.reconfigure(encoding="utf-8", errors="replace")
from euh.model import NLI, load_data, train_pass, evaluate, clone, set_seed, device, load_ckpt, hf_rev
from euh import stats as S
from transformers import BertTokenizerFast


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def w_T(alpha):   # neutral emphasis grows with α
    return [max(0.05, 1 - 0.5 * alpha), 1 + 2.0 * alpha, max(0.05, 1 - 0.5 * alpha)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="run")
    ap.add_argument("--exact_name", action="store_true", help="use --name as-is (no timestamp suffix)")
    ap.add_argument("--model", default="google/bert_uncased_L-2_H-128_A-2")
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.25, 0.5, 0.75, 1.0, 1.25])
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--mode", choices=["disjoint", "weighted"], default="disjoint",
                    help="disjoint: S = binary E/H loss on E/H-labelled items, T = U-vs-notU loss on its own items; "
                         "data split into disjoint S and T pools with a controllable shared fraction. "
                         "weighted: legacy — both objectives are class-weighted 3-way CE on the SAME pool (mostly one operator).")
    ap.add_argument("--shared_frac", type=float, default=0.0, help="fraction of each pass's items shared with the other pass (disjoint mode)")
    ap.add_argument("--slider", choices=["strength", "shared"], default="strength",
                    help="what α controls in disjoint mode: 'strength' = T-pass LR multiplier; 'shared' = shared item fraction ∈[0,1]")
    ap.add_argument("--w_S", type=float, nargs=3, default=[1.0, 0.4, 1.0])
    ap.add_argument("--kl_beta", type=float, default=0.2)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--n_base", type=int, default=12000)
    ap.add_argument("--epochs_base", type=int, default=2)
    ap.add_argument("--n_pass", type=int, default=1500)
    ap.add_argument("--epochs_pass", type=int, default=1)
    ap.add_argument("--n_eval", type=int, default=1000)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--max_len", type=int, default=64)
    ap.add_argument("--base_seed", type=int, default=1234)
    ap.add_argument("--no_zip", action="store_true")
    ap.add_argument("--save_ckpt", choices=["fp16", "fp32", "none"], default="fp16",
                    help="save every checkpoint's weights (base, S, T, S→T, T→S, replicates) under runs/<name>/ckpt/ "
                         "for post-hoc weight-space hypothesis tests (task-vector merges, HVP commutators, embeddings); "
                         "fp16 halves disk (~220 MB/checkpoint for bert-base); excluded from results zips")
    ap.add_argument("--ckpt_dir", default=os.environ.get("CKPT_DIR", ""),
                    help="root dir for checkpoint storage (e.g. another drive); a runs/<name>/ckpt junction is "
                         "created so existing paths keep working; default: env CKPT_DIR, else runs/<name>/ckpt")
    ap.add_argument("--n_replicate", type=int, default=1, help="extra composite reruns per order (composite seed variance)")
    args = ap.parse_args()
    if not args.exact_name:
        args.name = f"{args.name}_{time.strftime('%Y%m%d_%H%M%S')}"  # run folders carry config name + timestamp

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
        sd = model.state_dict()
        if args.save_ckpt == "fp16" and not force_fp32:
            sd = {k: (v.half() if v.is_floating_point() else v) for k, v in sd.items()}
        torch.save(sd, os.path.join(ckdir, f"{tag}.pt"))

    # ---------- resume: a crash or kill costs only the in-flight cell ----------
    ledger_path = os.path.join(out, "ledger.json")
    prev = None
    if os.path.exists(ledger_path):
        CRIT = ["model", "mode", "slider", "shared_frac", "w_S", "kl_beta", "lr", "n_base", "epochs_base",
                "n_pass", "epochs_pass", "n_eval", "bs", "max_len", "base_seed"]
        try:
            cand = json.load(open(ledger_path)); pm = cand.get("meta", {})
            if all(pm.get(k) == getattr(args, k) for k in CRIT):
                prev = cand; log(f"resume: found ledger with {len(prev.get('cells', {}))} finished cells")
            else:
                log("resume: existing ledger has a different config — starting fresh (it will be overwritten)")
        except Exception as e:
            log(f"resume: could not read existing ledger ({e}) — starting fresh")

    dev = device(); log(f"device={dev}  model={args.model}")
    tok = BertTokenizerFast.from_pretrained(args.model, revision=hf_rev(args.model))
    base_rows, pass_rows, ev = load_data(args.n_base, 3 * args.n_pass + 2000, args.n_eval, args.base_seed)
    gold = [r["label"] for r in ev]
    def build_pools(shared_frac):
        if args.mode == "disjoint":
            # S pool: E/H items only, binary E/H loss.  T pool: label mix held FIXED (its own U items
            # + E/H items), U-vs-notU loss.  α shares a slice of T's E/H sub-pool with S — the
            # co-dependence dial moves item overlap without changing what T is (label-matched sharing;
            # the pilot's unmatched version let T degenerate into a pure U-suppressor at high α).
            EH = [r for r in pass_rows if r["label"] in (0, 2)]; ALL = list(pass_rows)
            rng = np.random.default_rng(args.base_seed); rng.shuffle(EH); rng.shuffle(ALL)
            S_rows = EH[: args.n_pass]; S_ids = {id(r) for r in S_rows}
            rest = [r for r in ALL if id(r) not in S_ids]
            U_own = [r for r in rest if r["label"] == 1]
            EH_own = [r for r in rest if r["label"] != 1]
            fU = sum(1 for r in ALL if r["label"] == 1) / max(len(ALL), 1)
            n_U = int(round(fU * args.n_pass)); n_EH = args.n_pass - n_U
            n_sh = int(round(shared_frac * n_EH))
            if len(U_own) < n_U or len(EH_own) < n_EH - n_sh:
                raise RuntimeError(f"pool too small for label-matched T pool: need U={n_U}, own-EH={n_EH - n_sh}; "
                                   f"have U={len(U_own)}, own-EH={len(EH_own)}")
            T_rows = U_own[:n_U] + S_rows[:n_sh] + EH_own[: n_EH - n_sh]
            return S_rows, T_rows, "binEH", "binU", None, n_sh
        S_rows = T_rows = pass_rows[: args.n_pass]
        return S_rows, T_rows, "ce3", "ce3", args.w_S, len(S_rows)
    S_rows, T_rows, kind_S, kind_T, wS_used, n_sh = build_pools(args.shared_frac)
    log(f"pools: base={len(base_rows)} S={len(S_rows)} [{kind_S}] T={len(T_rows)} [{kind_T}, U={sum(1 for r in T_rows if r['label'] == 1)}] shared={n_sh} eval={len(ev)}  mode={args.mode} slider={args.slider}")

    # ---------- base ----------
    ck_base = os.path.join(ckdir, "base.pt")
    if prev is not None and os.path.exists(ck_base):
        log("resume: loading base from checkpoint")
        base = load_ckpt(ck_base, args.model, "cpu")
        P_base = np.array(prev["base"])
    else:
        set_seed(args.base_seed); base = NLI(args.model).to(dev)
        log("training base"); train_pass(base, tok, base_rows, args.epochs_base, args.lr, args.bs, args.max_len, args.base_seed, log=log)
        P_base = evaluate(base, tok, ev, args.max_len)
        save_ckpt(base, "base", force_fp32=True)  # fp32 so a resumed run continues from bit-identical base
        base.cpu()
        if dev == "cuda": torch.cuda.empty_cache()
    log(f"base acc {np.mean(S.verdicts(P_base)==np.array(gold)):.3f}  C={np.round(S.marginal(S.verdicts(P_base)),3)}")

    ledger = dict(meta=vars(args), gold=gold, labels=S.LAB, base=P_base.tolist(), cells={})
    if prev is not None:
        ledger["cells"].update(prev.get("cells", {}))
    def dump():
        json.dump(ledger, open(os.path.join(out, "ledger.json"), "w"))

    def run(start, seed, cw, ref, tag, rows, kind):
        # idle checkpoints are parked on CPU between passes: on an 8 GB card, keeping base/S/T/composites
        # all resident overflows into WDDM shared memory and slows training >10×
        start.to(dev)
        m = clone(start, args.model); log(f"    pass {tag} [{kind}, n={len(rows)}]")
        train_pass(m, tok, rows, args.epochs_pass, args.lr, args.bs, args.max_len, seed,
                   cw=cw, kl_beta=args.kl_beta, ref=ref, log=log, kind=kind)
        start.cpu()
        if dev == "cuda": torch.cuda.empty_cache()
        return m

    for alpha in args.alphas:
        wT = w_T(alpha) if args.mode == "weighted" else None
        if args.mode == "disjoint" and args.slider == "shared":
            S_rows, T_rows, kind_S, kind_T, wS_used, n_sh = build_pools(alpha); lrT = args.lr
            log(f"   α={alpha}: shared items = {n_sh}")
        else:
            lrT = args.lr * (alpha if args.mode == "disjoint" else 1.0)
        for seed in args.seeds:
            key = f"a{alpha}_s{seed}"
            if prev is not None and key in ledger["cells"]:
                log(f"== α={alpha} seed={seed}: already in ledger — skipped (resume)"); continue
            log(f"== α={alpha} seed={seed}  mode={args.mode} " + (f"w_S={args.w_S} w_T={np.round(wT,3)}" if wT else f"lr_S={args.lr:g} lr_T={lrT:g} shared={n_sh}"))
            # 1. single passes
            mS = run(base, seed, wS_used, base, "S", S_rows, kind_S)
            _lr = args.lr; args.lr = lrT; mT = run(base, seed, wT, base, "T", T_rows, kind_T); args.lr = _lr
            P_S, P_T = evaluate(mS, tok, ev, args.max_len), evaluate(mT, tok, ev, args.max_len)
            save_ckpt(mS, f"{key}_S"); save_ckpt(mT, f"{key}_T")
            mS.cpu(); mT.cpu()
            if dev == "cuda": torch.cuda.empty_cache()
            # 2. sealed prediction — append-only: an existing seal is NEVER overwritten.
            # A pre-existing seal means an earlier (aborted) attempt already ran composites
            # for this cell; the new seal is written alongside and the cell marked resealed,
            # excluding it from sealed-prediction claims.
            pred = S.predict_composites(P_base, P_S, P_T)
            sealed = dict(alpha=alpha, seed=seed, time=time.time(), prediction=pred)
            h = sha(sealed); sealed["sha256"] = h
            sealed_path = os.path.join(out, f"sealed_{key}.json")
            resealed = os.path.exists(sealed_path)
            if resealed:
                sealed_path = os.path.join(out, f"sealed_{key}.reseal{int(time.time())}.json")
                log(f"    WARNING: seal for {key} already exists — writing {os.path.basename(sealed_path)}; "
                    f"cell marked resealed (excluded from sealed-prediction claims)")
            json.dump(sealed, open(sealed_path, "w"))
            log(f"    SEALED prediction {h[:16]}…  Γ(alr)={np.round(pred['Gamma_alr'],3)} Γ(overlap)={np.round(pred['Gamma_overlap'],3)} "
                f"pred-dis alr={pred['alr']['pred_disagreement']:.3f} overlap={pred['overlap']['pred_disagreement']:.3f} "
                f"| flipS={pred['overlap']['flip_S']:.2f} flipT={pred['overlap']['flip_T']:.2f} overlap-ratio={pred['overlap']['overlap_ratio']:.2f} "
                f"| ‖[Φ]‖={pred['comm_discrete']:.3f} ‖[A]‖={pred['comm_alr']:.4f}")
            # 3. composites (+ optional replicates from the same S/T checkpoints)
            _lr = args.lr; args.lr = lrT; mST = run(mS, seed + 100, wT, mS, "S→T", T_rows, kind_T); args.lr = _lr
            mTS = run(mT, seed + 100, wS_used, mT, "T→S", S_rows, kind_S)
            P_ST, P_TS = evaluate(mST, tok, ev, args.max_len), evaluate(mTS, tok, ev, args.max_len)
            save_ckpt(mST, f"{key}_ST"); save_ckpt(mTS, f"{key}_TS")
            mST.cpu(); mTS.cpu()
            if dev == "cuda": torch.cuda.empty_cache()
            traces = dict(S=mS.loss_trace, T=mT.loss_trace, ST=mST.loss_trace, TS=mTS.loss_trace)
            reps = dict(ST=[], TS=[])
            for r in range(1, args.n_replicate):
                _lr = args.lr; args.lr = lrT; mSTr = run(mS, seed + 100 + 1000 * r, wT, mS, f"S→T rep{r}", T_rows, kind_T); args.lr = _lr
                reps["ST"].append(evaluate(mSTr, tok, ev, args.max_len).tolist()); save_ckpt(mSTr, f"{key}_ST_rep{r}"); del mSTr
                mTSr = run(mT, seed + 100 + 1000 * r, wS_used, mT, f"T→S rep{r}", S_rows, kind_S)
                reps["TS"].append(evaluate(mTSr, tok, ev, args.max_len).tolist()); save_ckpt(mTSr, f"{key}_TS_rep{r}"); del mTSr
            # 4. score
            sc = S.score(P_base, P_S, P_T, P_ST, P_TS, pred, traces=traces, bs=args.bs, replicates=reps if reps["ST"] else None)
            log(f"    OBSERVED Γ={np.round(sc['Gamma'],3)} disagreement={sc['disagreement']:.3f} SM p={sc['stuart_maxwell'][2]:.3g} "
                f"| overlap err {sc['pred_err']['overlap']['ST']:.3f}/{sc['pred_err']['overlap']['TS']:.3f} agree {sc['pred_err']['overlap']['item_agree_ST']:.2f}/{sc['pred_err']['overlap']['item_agree_TS']:.2f} "
                f"Γ-sign {sc['pred_err']['overlap']['Gamma_sign_agree']:.2f} in/out {sc['pred_err']['overlap']['disagree_in_overlap']:.3f}/{sc['pred_err']['overlap']['disagree_outside_overlap']:.3f} "
                f"| alr err {sc['pred_err']['alr']['ST']:.3f}/{sc['pred_err']['alr']['TS']:.3f} | markov err {sc['pred_err']['markov']['ST']:.3f}/{sc['pred_err']['markov']['TS']:.3f}")
            if "replicates" in sc["floors"]:
                f = sc["floors"]
                log(f"    FLOOR replicates: pair-dis ST={f['replicates']['ST']['pair_dis_mean']:.3f} TS={f['replicates']['TS']['pair_dis_mean']:.3f} "
                    f"σ_eff={f['replicates']['ST']['sigma_eff']:.3f}/{f['replicates']['TS']['sigma_eff']:.3f} "
                    f"| order-dis {sc['disagreement']:.3f} = {f['disagreement_over_floor']:.1f}× floor | loss-sd {np.round(list(f['loss_noise_sd'].values()),3)}")
            ledger["cells"][key] = dict(alpha=alpha, seed=seed, w_T=wT, lr_T=lrT, shared_items=n_sh, mode=args.mode, slider=args.slider, resealed=resealed,
                                       P=dict(S=P_S.tolist(), T=P_T.tolist(), ST=P_ST.tolist(), TS=P_TS.tolist()),
                                       replicates=reps, traces=traces,
                                       sealed_sha=h, prediction=pred, score=sc)
            dump()
    if args.save_ckpt != "none" and os.path.isdir(ckdir):
        fs = os.listdir(ckdir)
        log(f"checkpoints: {len(fs)} files, {sum(os.path.getsize(os.path.join(ckdir, f)) for f in fs) / 1e9:.2f} GB in {ckdir} (excluded from zip)")
    log("sweep done")

    # ---------- summary + figures + package ----------
    from viz import make_all
    summary = make_all(os.path.join(out, "ledger.json"), out)
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)
    if not args.no_zip:
        z = f"results_{args.name}.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(out):
                dirs[:] = [d for d in dirs if d != "ckpt"]
                for f in files: zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), "runs"))
        log(f"result package: {z}")


if __name__ == "__main__":
    main()
