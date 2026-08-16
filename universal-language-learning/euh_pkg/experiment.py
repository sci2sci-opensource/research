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
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--force", action="store_true", help="start a fresh battery even if an incomplete one exists")
    args = ap.parse_args()
    grid = QUICK if args.quick else STAGES
    stages = args.only or list(grid)
    here = os.path.dirname(os.path.abspath(__file__)); t0 = time.time()
    label = "quick" if args.quick else "full"
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
