# EUH order-dependence — blinded control-slider PoC

Two revision channels on the NLI verdict simplex Σ = {E, U, H} (entail / neutral / contradict),
applied in both orders, with the composite outcome **predicted and sealed before it is run**.

## Protocol (per control value α, per seed)

1. Train **S** (binary sharpening: class weights emphasise E/H) and **T** (neutral improvement:
   class weights emphasise U, strength α) from the same base, same mixed pool, KL-anchored to the
   previous checkpoint.
2. From base, S, T **only**, fit two channel models and predict S→T and T→S:
   * *ALR-affine* — a linear map on log-ratio coordinates of Δ² (a "tilt" model; composes ≈ commutatively)
   * *Markov* — a row-stochastic 3×3 on verdicts (the lumpable, "benchmark-is-a-sufficient-statistic" model)
   * *item-overlap null* — per-item verdict triple (base,S,T): each pass acts on the verdict the other left; the two
     orders can differ only on the overlap of the two flip sets. Label- and overlap-aware; failure outside the overlap
     = the second pass reacts to what the first did to the *representation*, not to the verdict it left.
     closed-form in the two single passes: Δλ_S Δλ_T (n_S·n_T)(n_S n_Tᵀ − n_T n_Sᵀ)  (PT §6.5)
   Predictions (marginals, Γ, per-item verdicts, disagreement set) are written to `sealed_*.json` with a SHA-256.
3. Train S→T and T→S.
4. Score observed composites against the sealed predictions.

The slider α lets you look for α* where the two marginals coincide while the item-level joint stays off-diagonal
(readouts coincide, revisions differ).

## One command, go for a walk

```
./run.sh experiment          # Linux/WSL/Mac  (RTX 3070: ~1.5–2 h;  ./run.sh experiment quick ≈ 25 min)
run.bat experiment           # Windows
```
Runs four stages — `base_strength` (α = T strength, incl. low α), `base_shared` (α = shared-item fraction),
`base_weighted` (negative control: one operator on a shared pool), `tiny_strength` (scale contrast) — each with
sealed predictions and replicate floors, then builds **`report/report.md` + `report.html`** and packs
**`results_experiment.zip`**. Resumable: finished stages are skipped, so a crash costs nothing. `./run.sh report`
rebuilds the report from whatever ledgers exist.

### The report
* **Hypothesis ledger** — ten pre-registered claims (H1–H10), each with an explicit E/U/H rule, evaluated per dataset.
  U is a definite verdict of non-resolution, not a probability over E/H.
* **Bayesian update over theories of the composite** — last-writer, first-writer, Markov (lumpable), tilt (commuting
  affine), item-overlap, base — each predicting per-item verdicts from base/S/T only, updated on two packets: the
  composite verdicts (tempered) and the order-disagreement indicator (class-balanced). Posterior mass is relative
  to the theories entertained; the winner's actual skill (verdict accuracy, flip-set F1) is printed beside it so a
  merely-least-wrong theory is visible as such.

## Run (single stages)

```
./run.sh smoke        # sanity
./run.sh tiny         # bert-tiny, 3 α × 3 seeds
./run.sh base myrun   # bert-base — CUDA (NVIDIA, fp16 autocast) / MPS (Apple) / CPU picked automatically
./run.sh shared       # α = shared-item fraction between the two passes
```
Windows: `run.bat base myrun` (or use WSL).  `run.sh`/`run.bat` install a CUDA torch wheel (cu124) when
`nvidia-smi` is present and torch can't see the GPU; for another CUDA version see https://pytorch.org/get-started/locally/.
On an RTX 3070 the `base` profile takes roughly 20–30 min.
Output: `runs/<name>_<timestamp>/` (ledger.json with every per-item probability for every checkpoint, sealed
predictions, summary.json, log.txt, figures/) and **`results_<name>_<timestamp>.zip`** — send that back. Run folders
are always timestamped (`--exact_name` for a literal name); battery runs live under `runs/exp_<quick|full>_<timestamp>/`
with the report inside, and an interrupted battery is resumed automatically on relaunch.

Regenerate figures/summary from a ledger: `python viz.py runs/<name>/ledger.json`

Every checkpoint's weights (base, S, T, S→T, T→S, replicates) are saved to `runs/<name>/ckpt/*.pt` (fp16 state dicts,
~220 MB each for bert-base — budget ~5–10 GB for a quick battery, ~40 GB for a full one) so weight-space hypotheses
(task-vector merges, HVP commutators, representation subspaces) can be tested post hoc without retraining:
`euh.model.load_ckpt(path, model_name)`. Disable with `--save_ckpt none`; checkpoints are never zipped.

## Figures
* `01_prediction_vs_empirical` — C(W), Γ, disagreement, prediction error across α; sealed prediction vs observed
* `02_simplex_trajectories` — base → single pass → composite on Δ(Σ), observed vs predicted
* `03_joint_tables` — paired S→T × T→S verdict joint on shared items (what the marginals erase)
* `04_boundary_concentration` — does the order effect live at verdict boundaries? (P(flip) vs base margin, AUC)
* `05_decomposition_commutators` — symmetric interaction vs antisymmetric carryover; ‖[Φ_S,Φ_T]‖ vs ‖[A_S,A_T]‖; join info loss
* `06_item_level_pred_vs_obs` — per-item composed-channel prediction vs observation, flipped items highlighted
* `07_overlap_null` — single-pass flip sets, their overlap vs independence (co-dependence), and whether observed disagreement falls inside or outside the predicted overlap set

## Objects (paper → statistic)
C(W) verdict marginal · paired 3×3 joint · Stuart–Maxwell (readout coincidence) · Bowker / item disagreement
(revision difference) · channels Φ_X and A_X · commutators · sealed composite prediction · non-lumpability χ² ·
Γ / symmetric interaction / antisymmetric carryover · bits destroyed by the contamination-order join.


## Noise floors
`--n_replicate k` reruns each composite pass k−1 extra times from the same S/T checkpoints. The pairwise
verdict disagreement between same-order replicates is the **floor** any order effect must exceed; every
prediction error is plotted against it, and `disagreement_over_floor` in the summary is the ratio.
Per-step loss traces of every pass are stored in the ledger (`traces`) as a covariate; σ_eff (logit jitter
matched to replicate disagreement) is reported so you can test whether loss-noise tracks endpoint wander.

## Modes
* `--mode disjoint` (default): S = binary E-vs-H loss on E/H-labelled items (no gradient about U); T = U-vs-notU loss on its
  own item pool. Item pools are disjoint except `--shared_frac`. Two genuinely different operators.
* `--mode weighted` (legacy): both passes are class-weighted 3-way CE on the *same* pool → mostly one operator; commutes trivially
  on a competent model (kept as a negative control).
* `--slider strength` (default): α = T-pass LR multiplier.  `--slider shared`: α = fraction of T's E/H sub-pool shared
  with S ∈ [0,1] (co-dependence dial). Sharing is **label-matched**: T always keeps its own U items so its label mix —
  and hence the operator itself — is constant across α (the pilot's unmatched version let T degenerate into a pure
  U-suppressor at high α, conflating co-dependence with operator strength).

Recompute from a ledger without retraining: `python rescore.py runs/<name>/ledger.json`
