"""
Run the whole enrichment battery unattended.

    python experiment.py            # full battery (bert-base)
    python experiment.py --quick    # reduced grid
    python experiment.py --only base_strength

Batteries live in runs/exp_<label>_<timestamp>/; an interrupted battery is auto-resumed
(stage-level here, cell-level inside sweep.py). Checkpoints excluded from the results zip.
"""
import argparse, glob, os, re, subprocess, sys, time, zipfile

STAGES = {
    "tiny_strength": ["--alphas", "0.25", "0.5", "1.0", "2.0", "--seeds", "0", "1", "2",
                      "--n_replicate", "2", "--n_base", "6000", "--epochs_base", "2",
                      "--n_pass", "1500", "--n_eval", "1500"],
    "base_strength": ["--model", "bert-base-uncased", "--alphas", "0.25", "0.5", "1.0", "2.0",
                      "--seeds", "0", "1", "2", "--n_replicate", "3", "--n_base", "10000",
                      "--epochs_base", "2", "--n_pass", "2500", "--n_eval", "2500",
                      "--lr", "3e-5", "--kl_beta", "0.2"],
    # ablation for the sealed anchor-causality hypothesis (N5): identical grid, no KL anchor
    "base_klzero":   ["--model", "bert-base-uncased", "--alphas", "0.25", "0.5", "1.0", "2.0",
                      "--seeds", "0", "1", "2", "--n_replicate", "3", "--n_base", "10000",
                      "--epochs_base", "2", "--n_pass", "2500", "--n_eval", "2500",
                      "--lr", "3e-5", "--kl_beta", "0.0"],
}
# ---------------------------------------------------------------- control battery ---
# Does the enrichment order effect need the two added distinctions to be DIFFERENT?
#
# The euh null-swap arm (2026-08-17) showed that experiment's order effect survives intact when
# the second operator is replaced by a second instance of the first (19% vs 17% systematic), so
# it is not caused by the operators differing. NER has never faced that control, and NER is where
# the project's positive result lives (sealed N1 = E, 2.02x). This battery supplies it.
#
#   ctrl_treat     two genuinely different categories (+ORG, +MISC)      — the treatment
#   ctrl_nullswap  two arbitrary halves of ONE category (+ORG#1, +ORG#2) — the matched control
#
# Both arms are run fresh rather than comparing ctrl_nullswap against the recorded base_strength,
# so the contrast is single-factor: only the identity of the second added distinction changes.
# Settings match base_strength exactly (n_pass 2500, n_base 10000, lr 3e-5, kl_beta 0.2,
# n_replicate 3) at its alpha=1.0 slice, so ctrl_treat doubles as a replication check on that
# stage. The ORG entity split leaves 3185/3169 sentences per sub-category, comfortably above
# n_pass -- pools are drawn independently per category, exactly as ORG and MISC are.
_CTRL = ["--model", "bert-base-uncased", "--alphas", "1.0", "--seeds", "0", "1", "2",
         "--n_replicate", "3", "--n_base", "10000", "--epochs_base", "2",
         "--n_pass", "2500", "--n_eval", "2500", "--lr", "3e-5", "--kl_beta", "0.2"]
CONTROL = {
    "ctrl_treat":    _CTRL,
    "ctrl_nullswap": _CTRL + ["--mode", "nullswap"],
}

QUICK = {
    "tiny_strength": ["--alphas", "0.5", "1.0", "--seeds", "0", "1", "--n_replicate", "2",
                      "--n_base", "6000", "--epochs_base", "2", "--n_pass", "1500", "--n_eval", "1500"],
    "base_strength": ["--model", "bert-base-uncased", "--alphas", "0.5", "1.0", "--seeds", "0", "1",
                      "--n_replicate", "2", "--n_base", "8000", "--epochs_base", "1",
                      "--n_pass", "2000", "--n_eval", "1500", "--lr", "3e-5", "--kl_beta", "0.2"],
}


def pick_battery(here, label, stages):
    pat = re.compile(rf"^exp_{label}_\d{{8}}_\d{{6}}$")
    for b in sorted(glob.glob(os.path.join(here, "runs", f"exp_{label}_*")), reverse=True):
        name = os.path.basename(b)
        if pat.match(name) and any(not os.path.exists(os.path.join(b, st, "summary.json")) for st in stages):
            return name, True
    return f"exp_{label}_{time.strftime('%Y%m%d_%H%M%S')}", False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--control", action="store_true",
                    help="matched treatment/null-swap pair: does the order effect need the two "
                         "added distinctions to differ?")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--force", action="store_true", help="start a fresh battery even if an incomplete one exists")
    args = ap.parse_args()
    grid = CONTROL if args.control else (QUICK if args.quick else STAGES)
    stages = args.only or list(grid)
    here = os.path.dirname(os.path.abspath(__file__)); t0 = time.time()
    label = "control" if args.control else ("quick" if args.quick else "full")
    if args.force:
        battery, resumed = f"exp_{label}_{time.strftime('%Y%m%d_%H%M%S')}", False
    else:
        battery, resumed = pick_battery(here, label, stages)
    bdir = os.path.join(here, "runs", battery)
    print(f"[experiment] battery: runs/{battery}" + (" (resuming)" if resumed else ""), flush=True)
    for st in stages:
        out = os.path.join(bdir, st)
        if os.path.exists(os.path.join(out, "summary.json")):
            print(f"[experiment] {st}: already finished, skipping"); continue
        print(f"[experiment] === stage {st} ===  ({(time.time()-t0)/60:.1f} min elapsed)", flush=True)
        cmd = [sys.executable, os.path.join(here, "sweep.py"), "--name", f"{battery}/{st}",
               "--exact_name", "--no_zip"] + grid[st]
        r = subprocess.run(cmd, cwd=here)
        if r.returncode != 0:
            print(f"[experiment] stage {st} FAILED (rc={r.returncode}); continuing with the rest", flush=True)
    print(f"[experiment] battery done in {(time.time()-t0)/60:.1f} min; evaluating sealed hypotheses", flush=True)
    subprocess.run([sys.executable, os.path.join(here, "hypotheses.py"), bdir], cwd=here)
    print("[experiment] packaging", flush=True)
    z = os.path.join(here, f"results_{battery}.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(bdir):
            dirs[:] = [d for d in dirs if d != "ckpt"]
            for f in files:
                zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), os.path.join(here, "runs")))
    print(f"[experiment] result package: {z}")


if __name__ == "__main__":
    main()
