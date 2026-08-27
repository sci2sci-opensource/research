"""
Run the whole battery unattended, then build the report.

    python experiment.py            # full battery (≈1.5–2 h on an RTX 3070)
    python experiment.py --quick    # reduced grid (≈25 min)
    python experiment.py --only base_strength base_shared   # subset

Stages (each is a sweep.py run; a stage is skipped if runs/<stage>/summary.json already exists):
  base_strength   bert-base, disjoint objectives, α = T-pass strength (incl. low α so T is a tilt, not an overwrite)
  base_shared     bert-base, disjoint objectives, α = shared-item fraction between passes (co-dependence dial)
  base_weighted   bert-base, legacy weighted mode on a shared pool — NEGATIVE CONTROL (one operator; expect no order effect)
  tiny_strength   bert-tiny, disjoint, same α grid — scale contrast
Then report.py aggregates every runs/*/ledger.json into report/ and packs results_experiment.zip.
"""
import argparse, glob, os, re, subprocess, sys, time, zipfile

STAGES = {
    "base_strength": ["--model", "bert-base-uncased", "--alphas", "0.1", "0.25", "0.5", "1.0", "2.0", "--seeds", "0", "1", "2",
                      "--n_replicate", "3", "--n_base", "60000", "--epochs_base", "1", "--n_pass", "6000", "--n_eval", "4000",
                      "--lr", "3e-5", "--kl_beta", "0.2"],
    "base_shared":   ["--model", "bert-base-uncased", "--slider", "shared", "--alphas", "0.0", "0.25", "0.5", "1.0", "--seeds", "0", "1",
                      "--n_replicate", "2", "--n_base", "60000", "--epochs_base", "1", "--n_pass", "6000", "--n_eval", "4000",
                      "--lr", "3e-5", "--kl_beta", "0.2"],
    "base_weighted": ["--model", "bert-base-uncased", "--mode", "weighted", "--alphas", "0.5", "1.0", "--seeds", "0", "1",
                      "--n_replicate", "2", "--n_base", "60000", "--epochs_base", "1", "--n_pass", "6000", "--n_eval", "4000",
                      "--lr", "2e-5", "--kl_beta", "2.0"],
    "tiny_strength": ["--alphas", "0.1", "0.25", "0.5", "1.0", "--seeds", "0", "1", "2", "--n_replicate", "2",
                      "--n_base", "12000", "--epochs_base", "2", "--n_pass", "1500", "--n_eval", "1000"],
}
# ---------------------------------------------------------------- power battery (v3) ---
# Motivation (from the v2 dose-response): across a 20x lr range in base_strength the order
# disagreement and the replicate floor grow together, so the ratio is flat-to-declining
# (1.47x at alpha=0.1 down to 1.20x at alpha=2.0). Escalating displacement cannot clear the
# 2x bar. This battery holds displacement fixed at alpha=1.0 and attacks the measurement
# instead, on three fronts:
#
#   power_treat     m=4 runs per order, so the floor rests on 12 within-order pairs and the
#                   effect on 16 cross-order pairs instead of a single pair each (the v2
#                   floor came from ONE replicate pair, which is why sibling seeds gave
#                   1.82x and 1.06x at the same alpha).
#   power_nullswap  the matched control: same objective on both passes, so order is
#                   semantically null while the perturbation structure is identical. This is
#                   the denominator the treatment should be compared against; a same-order
#                   replicate re-seeds a whole pass and is arguably a larger perturbation
#                   than the swap itself.
#   scale_*         a scale curve at matched settings (11M / 29M / 41M) joining bert-tiny
#                   (4.4M) and bert-base (110M). v2 showed tiny->base moved the ratio 0.85 ->
#                   1.35 by halving the floor; the curve tests whether that trend is real and
#                   how far it would have to extrapolate to reach 2x.
#
# Pre-registered rules for this battery are H14-H16 in report.py; push them BEFORE launching.
_POWER_COMMON = ["--alphas", "1.0", "--seeds", "0", "1", "2", "--n_replicate", "4",
                 "--n_eval", "4000", "--kl_beta", "0.2"]
_SCALE_COMMON = _POWER_COMMON + ["--n_base", "30000", "--epochs_base", "1",
                                 "--n_pass", "6000", "--lr", "3e-5"]
POWER = {
    "power_treat":    ["--model", "bert-base-uncased", "--n_base", "60000", "--epochs_base", "1",
                       "--n_pass", "6000", "--lr", "3e-5"] + _POWER_COMMON,
    "power_nullswap": ["--model", "bert-base-uncased", "--mode", "nullswap", "--n_base", "60000",
                       "--epochs_base", "1", "--n_pass", "6000", "--lr", "3e-5"] + _POWER_COMMON,
    "scale_11m":      ["--model", "google/bert_uncased_L-4_H-256_A-4"] + _SCALE_COMMON,
    "scale_29m":      ["--model", "google/bert_uncased_L-4_H-512_A-8"] + _SCALE_COMMON,
    "scale_41m":      ["--model", "google/bert_uncased_L-8_H-512_A-8"] + _SCALE_COMMON,
    "scale_110m":     ["--model", "bert-base-uncased"] + _SCALE_COMMON,
}

QUICK = {
    "base_strength": ["--model", "bert-base-uncased", "--alphas", "0.25", "1.0", "--seeds", "0", "1", "--n_replicate", "2",
                      "--n_base", "30000", "--epochs_base", "1", "--n_pass", "4000", "--n_eval", "2000", "--lr", "3e-5", "--kl_beta", "0.2"],
    "base_shared":   ["--model", "bert-base-uncased", "--slider", "shared", "--alphas", "0.0", "1.0", "--seeds", "0", "--n_replicate", "2",
                      "--n_base", "30000", "--epochs_base", "1", "--n_pass", "4000", "--n_eval", "2000", "--lr", "3e-5", "--kl_beta", "0.2"],
    "base_weighted": ["--model", "bert-base-uncased", "--mode", "weighted", "--alphas", "1.0", "--seeds", "0", "--n_replicate", "2",
                      "--n_base", "30000", "--epochs_base", "1", "--n_pass", "4000", "--n_eval", "2000", "--lr", "2e-5", "--kl_beta", "2.0"],
    "tiny_strength": ["--alphas", "0.25", "1.0", "--seeds", "0", "1", "--n_replicate", "2", "--n_base", "12000", "--epochs_base", "2",
                      "--n_pass", "1500", "--n_eval", "1000"],
}


def pick_battery(here, label, stages):
    """Resume the newest incomplete exp_<label>_<timestamp> battery, else start a fresh one.
    Only exact timestamped names are resume candidates (archived/pilot folders are left alone)."""
    pat = re.compile(rf"^exp_{label}_\d{{8}}_\d{{6}}$")
    for b in sorted(glob.glob(os.path.join(here, "runs", f"exp_{label}_*")), reverse=True):
        name = os.path.basename(b)
        if pat.match(name) and any(not os.path.exists(os.path.join(b, st, "summary.json")) for st in stages):
            return name, True
    return f"exp_{label}_{time.strftime('%Y%m%d_%H%M%S')}", False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--power", action="store_true",
                    help="v3 measurement battery: m=4 replicates, matched null-swap control, scale curve")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--force", action="store_true", help="start a fresh battery even if an incomplete one exists")
    args = ap.parse_args()
    grid = POWER if args.power else (QUICK if args.quick else STAGES)
    stages = args.only or list(grid)
    here = os.path.dirname(os.path.abspath(__file__)); t0 = time.time()
    label = "power" if args.power else ("quick" if args.quick else "full")
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
        cmd = [sys.executable, os.path.join(here, "sweep.py"), "--name", f"{battery}/{st}", "--exact_name", "--no_zip"] + grid[st]
        r = subprocess.run(cmd, cwd=here)
        if r.returncode != 0:
            print(f"[experiment] stage {st} FAILED (rc={r.returncode}); continuing with the rest", flush=True)
    print(f"[experiment] battery done in {(time.time()-t0)/60:.1f} min; building report", flush=True)
    subprocess.run([sys.executable, os.path.join(here, "report.py"), os.path.join("runs", battery)], cwd=here)
    z = os.path.join(here, f"results_{battery}.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(bdir):
            dirs[:] = [d for d in dirs if d != "ckpt"]  # weights stay local; the zip is the send-back package
            for f in files:
                zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), os.path.join(here, "runs")))
    print(f"[experiment] result package: {z}")


if __name__ == "__main__":
    main()
