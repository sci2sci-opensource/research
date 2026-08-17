# EUH order-dependence — hypothesis ledger

Verdicts: **E** witnessed under the pre-registered rule · **H** refuted · **U** not resolved by this data (a definite verdict of non-resolution, not a probability over E/H).

## Datasets

| stage | model | mode | slider | cells | base acc | replicates |
|---|---|---|---|---|---|---|
| power_nullswap | bert-base-uncased | nullswap | strength | 3 | 0.860 | 4 |
| power_treat | bert-base-uncased | disjoint | strength | 3 | 0.860 | 4 |
| scale_110m | bert-base-uncased | disjoint | strength | 3 | 0.849 | 4 |
| scale_11m | google/bert_uncased_L-4_H-256_A-4 | disjoint | strength | 3 | 0.748 | 4 |
| scale_29m | google/bert_uncased_L-4_H-512_A-8 | disjoint | strength | 3 | 0.781 | 4 |
| scale_41m | google/bert_uncased_L-8_H-512_A-8 | disjoint | strength | 3 | 0.800 | 4 |

## Hypotheses × datasets

| # | hypothesis | rule | power_nullswap | power_treat | scale_110m | scale_11m | scale_29m | scale_41m |
|---|---|---|---|---|---|---|---|---|
| **H1** | Order effect exceeds the composite's own seed noise | <sub>disagreement(S→T,T→S) ≥ 2× same-order replicate disagreement in ≥2/3 of cells</sub> | 🔴 H<br><sub>order disagreement ≤1.2× floor in 67% of cells</sub> | ⚪ U<br><sub>mixed: median 1.4× floor</sub> | 🔴 H<br><sub>order disagreement ≤1.2× floor in 67% of cells</sub> | ⚪ U<br><sub>mixed: median 1.6× floor</sub> | 🔴 H<br><sub>order disagreement ≤1.2× floor in 67% of cells</sub> | 🔴 H<br><sub>order disagreement ≤1.2× floor in 67% of cells</sub> |
| **H2** | Γ_U sign: S→T ends more neutral than T→S, seed-stable | <sub>mean Γ_U > 0, |mean| > 2·SE, positive in ≥80% cells</sub> | ⚪ U<br><sub>Γ_U = -0.002 ± 0.025, sign not stable</sub> | 🟢 E<br><sub>Γ_U = +0.026 ± 0.017, positive in 100% of cells</sub> | ⚪ U<br><sub>Γ_U = +0.026 ± 0.037, sign not stable</sub> | ⚪ U<br><sub>Γ_U = +0.035 ± 0.054, sign not stable</sub> | ⚪ U<br><sub>Γ_U = +0.029 ± 0.030, sign not stable</sub> | ⚪ U<br><sub>Γ_U = +0.016 ± 0.039, sign not stable</sub> |
| **H3** | Non-lumpability: verdict marginal is not a sufficient statistic | <sub>Markov composite Φ_S·Φ_T rejected (χ² p<0.01) in ≥2/3 of cells</sub> | 🟢 E<br><sub>Markov composite rejected (p&lt;0.01) in 100% of cells</sub> | 🟢 E<br><sub>Markov composite rejected (p&lt;0.01) in 100% of cells</sub> | 🟢 E<br><sub>Markov composite rejected (p&lt;0.01) in 100% of cells</sub> | 🟢 E<br><sub>Markov composite rejected (p&lt;0.01) in 100% of cells</sub> | 🟢 E<br><sub>Markov composite rejected (p&lt;0.01) in 100% of cells</sub> | 🟢 E<br><sub>Markov composite rejected (p&lt;0.01) in 100% of cells</sub> |
| **H4** | Order effect lives OUTSIDE the overlap of the two flip sets | <sub>≥90% of cross-order disagreement on items neither pass flipped or only one flipped</sub> | 🟢 E<br><sub>98% of order-disagreement lies outside the predicted overlap set</sub> | 🟢 E<br><sub>98% of order-disagreement lies outside the predicted overlap set</sub> | 🟢 E<br><sub>98% of order-disagreement lies outside the predicted overlap set</sub> | 🟢 E<br><sub>97% of order-disagreement lies outside the predicted overlap set</sub> | 🟢 E<br><sub>98% of order-disagreement lies outside the predicted overlap set</sub> | 🟢 E<br><sub>98% of order-disagreement lies outside the predicted overlap set</sub> |
| **H5** | Flip-set co-dependence tracks operator identity | <sub>disjoint objectives → overlap ratio ≈1; shared operator → ≫1</sub> | 🔴 H<br><sub>disjoint mode but overlap ratio 7.7× — operators still share a component</sub> | 🔴 H<br><sub>disjoint mode but overlap ratio 6.1× — operators still share a component</sub> | 🔴 H<br><sub>disjoint mode but overlap ratio 4.9× — operators still share a component</sub> | 🔴 H<br><sub>disjoint mode but overlap ratio 3.3× — operators still share a component</sub> | 🔴 H<br><sub>disjoint mode but overlap ratio 5.2× — operators still share a component</sub> | 🔴 H<br><sub>disjoint mode but overlap ratio 4.3× — operators still share a component</sub> |
| **H6** | Order effect concentrates at verdict boundaries | <sub>AUC(base top-2 margin → flip) ≥ 0.75</sub> | 🟢 E<br><sub>AUC(base margin → flip) = 0.87: order effect concentrates at verdict boundaries</sub> | 🟢 E<br><sub>AUC(base margin → flip) = 0.89: order effect concentrates at verdict boundaries</sub> | 🟢 E<br><sub>AUC(base margin → flip) = 0.86: order effect concentrates at verdict boundaries</sub> | 🟢 E<br><sub>AUC(base margin → flip) = 0.85: order effect concentrates at verdict boundaries</sub> | 🟢 E<br><sub>AUC(base margin → flip) = 0.81: order effect concentrates at verdict boundaries</sub> | 🟢 E<br><sub>AUC(base margin → flip) = 0.83: order effect concentrates at verdict boundaries</sub> |
| **H7** | Prop 6.3 specimen: readouts coincide, revisions differ | <sub>some cell with Stuart–Maxwell p>0.05 AND disagreement ≥2× floor</sub> | ⚪ U<br><sub>no cell shows coincident readouts with above-floor revision difference (not refutable by absence)</sub> | ⚪ U<br><sub>no cell shows coincident readouts with above-floor revision difference (not refutable by absence)</sub> | ⚪ U<br><sub>no cell shows coincident readouts with above-floor revision difference (not refutable by absence)</sub> | ⚪ U<br><sub>no cell shows coincident readouts with above-floor revision difference (not refutable by absence)</sub> | ⚪ U<br><sub>no cell shows coincident readouts with above-floor revision difference (not refutable by absence)</sub> | ⚪ U<br><sub>no cell shows coincident readouts with above-floor revision difference (not refutable by absence)</sub> |
| **H8** | Shared-fraction slider raises co-dependence | <sub>Spearman(α_shared, overlap ratio) ≥ 0.6</sub> | ⚪ U<br><sub>needs the shared-fraction slider stage</sub> | ⚪ U<br><sub>needs the shared-fraction slider stage</sub> | ⚪ U<br><sub>needs the shared-fraction slider stage</sub> | ⚪ U<br><sub>needs the shared-fraction slider stage</sub> | ⚪ U<br><sub>needs the shared-fraction slider stage</sub> | ⚪ U<br><sub>needs the shared-fraction slider stage</sub> |
| **H9** | Negative control: one operator ⇒ no order effect | <sub>weighted mode: disagreement ≤ 1.5× floor</sub> | ⚪ U<br><sub>needs the weighted-mode control stage</sub> | ⚪ U<br><sub>needs the weighted-mode control stage</sub> | ⚪ U<br><sub>needs the weighted-mode control stage</sub> | ⚪ U<br><sub>needs the weighted-mode control stage</sub> | ⚪ U<br><sub>needs the weighted-mode control stage</sub> | ⚪ U<br><sub>needs the weighted-mode control stage</sub> |
| **H10** | The join destroys information | <sub>H(tuple) − H(join) ≥ 0.2 bit/item</sub> | 🟢 E<br><sub>publishing join(ST,TS) instead of the tuple destroys 0.40 bits/item (median)</sub> | 🟢 E<br><sub>publishing join(ST,TS) instead of the tuple destroys 0.40 bits/item (median)</sub> | 🟢 E<br><sub>publishing join(ST,TS) instead of the tuple destroys 0.42 bits/item (median)</sub> | 🟢 E<br><sub>publishing join(ST,TS) instead of the tuple destroys 0.50 bits/item (median)</sub> | 🟢 E<br><sub>publishing join(ST,TS) instead of the tuple destroys 0.46 bits/item (median)</sub> | 🟢 E<br><sub>publishing join(ST,TS) instead of the tuple destroys 0.46 bits/item (median)</sub> |
| **H11** | Calibrated non-lumpability: exceeds the replicate-noise statistic | <sub>obs χ² ≥ 2× median replicate-composite χ² in ≥2/3 of cells</sub> | 🔴 H<br><sub>observed non-lumpability ≈ noise level (median 1.1×)</sub> | 🔴 H<br><sub>observed non-lumpability ≈ noise level (median 0.9×)</sub> | 🔴 H<br><sub>observed non-lumpability ≈ noise level (median 0.9×)</sub> | 🔴 H<br><sub>observed non-lumpability ≈ noise level (median 0.9×)</sub> | ⚪ U<br><sub>median 1.3× the noise statistic</sub> | 🔴 H<br><sub>observed non-lumpability ≈ noise level (median 0.9×)</sub> |
| **H12** | Calibrated localization: above-noise excess lies outside the overlap set | <sub>≥90% of excess (obs − replicate-noise rate) outside, ≥3 cells with ≥0.5% excess</sub> | 🔴 H<br><sub>above-noise excess mostly inside the overlap set (26% outside)</sub> | 🔴 H<br><sub>above-noise excess mostly inside the overlap set (12% outside)</sub> | ⚪ U<br><sub>above-noise excess ≥0.5% in only 2 cell(s) — nothing to localize</sub> | 🔴 H<br><sub>above-noise excess mostly inside the overlap set (46% outside)</sub> | ⚪ U<br><sub>above-noise excess ≥0.5% in only 2 cell(s) — nothing to localize</sub> | 🔴 H<br><sub>above-noise excess mostly inside the overlap set (29% outside)</sub> |
| **H13** | Sign consistency: order/floor ratio >1 almost everywhere | <sub>ratio >1× floor in ≥90% of ≥6 cells</sub> | ⚪ U<br><sub>fewer than 6 cells with floors</sub> | ⚪ U<br><sub>fewer than 6 cells with floors</sub> | ⚪ U<br><sub>fewer than 6 cells with floors</sub> | ⚪ U<br><sub>fewer than 6 cells with floors</sub> | ⚪ U<br><sub>fewer than 6 cells with floors</sub> | ⚪ U<br><sub>fewer than 6 cells with floors</sub> |
| **H14** | A systematic (non-noise) order component exists | <sub>cross-order minus within-order pairwise disagreement >0, bootstrap CI excluding 0, in ≥2/3 of cells</sub> | 🟢 E<br><sub>systematic component &gt;0 (bootstrap CI excludes 0) in 100% of cells; 19% of cross-order disagreement is systematic (median ratio 1.23×)</sub> | 🟢 E<br><sub>systematic component &gt;0 (bootstrap CI excludes 0) in 100% of cells; 17% of cross-order disagreement is systematic (median ratio 1.20×)</sub> | 🟢 E<br><sub>systematic component &gt;0 (bootstrap CI excludes 0) in 100% of cells; 21% of cross-order disagreement is systematic (median ratio 1.26×)</sub> | 🟢 E<br><sub>systematic component &gt;0 (bootstrap CI excludes 0) in 100% of cells; 28% of cross-order disagreement is systematic (median ratio 1.39×)</sub> | 🟢 E<br><sub>systematic component &gt;0 (bootstrap CI excludes 0) in 100% of cells; 18% of cross-order disagreement is systematic (median ratio 1.22×)</sub> | 🟢 E<br><sub>systematic component &gt;0 (bootstrap CI excludes 0) in 100% of cells; 19% of cross-order disagreement is systematic (median ratio 1.23×)</sub> |

## Battery-level hypotheses

These compare stages against each other rather than scoring one stage, so they carry a single verdict per battery.

| # | hypothesis | rule | verdict |
|---|---|---|---|
| **H15** | Operator identity drives the order difference (matched null-swap control) | <sub>median systematic fraction in power_treat ≥ 2× power_nullswap, with CI>0 in ≥2/3 of treat cells</sub> | 🔴 H<br><sub>null swap shows as much order effect as the two-operator arm (19% vs 17%)</sub> |
| **H16** | Order/noise ratio rises with model scale | <sub>Spearman(log params, pairwise ratio) ≥ 0.6 over ≥4 scale stages</sub> | 🔴 H<br><sub>ratio does not rise with scale (ρ=-0.20)</sub> |

## Bayesian update over theories of the composite

Each theory predicts every item's verdict for S→T and T→S from base, S, T only; likelihood uses ε = the cell's measured replicate floor. Uniform prior; posterior after the last cell of each stage.

**(a) composite packet** — per-item verdicts of S→T and T→S (tempered, n_eff=200 per cell)

| stage | last_writer | first_writer | markov | tilt | overlap | base | best | verdict acc of best |
|---|---|---|---|---|---|---|---|---|
| power_nullswap | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | **first_writer** | 0.943 |
| power_treat | 0.062 | 0.937 | 0.000 | 0.000 | 0.000 | 0.000 | **first_writer** | 0.939 |
| scale_110m | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | **first_writer** | 0.924 |
| scale_11m | 0.000 | 0.001 | 0.000 | 0.999 | 0.000 | 0.000 | **tilt** | 0.906 |
| scale_29m | 0.750 | 0.102 | 0.000 | 0.000 | 0.148 | 0.000 | **last_writer** | 0.908 |
| scale_41m | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | **first_writer** | 0.918 |

**(b) order packet** — per-item disagreement indicator [v_ST ≠ v_TS], class-balanced log-lik (a theory that predicts no flips pays log ε on every observed flip); this is the statistic the order question is about

| stage | last_writer | first_writer | markov | tilt | overlap | base | best | flip-set F1 of best | observed disagreement |
|---|---|---|---|---|---|---|---|---|---|
| power_nullswap | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.428 | 0.066 |
| power_treat | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.459 | 0.068 |
| scale_110m | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.399 | 0.079 |
| scale_11m | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.433 | 0.103 |
| scale_29m | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.354 | 0.084 |
| scale_41m | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.424 | 0.091 |

<sub>Posterior concentration is relative to the theories entertained; an absent theory cannot acquire mass (§3.5). Per-item accuracy of the best theory is reported so a 'winner' that is merely least-wrong is visible as such.</sub>


### Per-cell verdict accuracy of each theory


**power_nullswap** — verdict accuracy / flip-set F1 (predicted disagreement rate)

| cell | ε (floor) | obs dis | last_writer | first_writer | markov | tilt | overlap | base |
|---|---|---|---|---|---|---|---|---|
| a1.0_s0 | 0.056 | 0.067 | 0.93 / 0.45 (0.07) | 0.95 / 0.45 (0.07) | 0.92 / 0.00 (0.00) | 0.93 / 0.03 (0.00) | 0.94 / 0.04 (0.00) | 0.92 / 0.00 (0.00) |
| a1.0_s1 | 0.053 | 0.061 | 0.93 / 0.39 (0.07) | 0.94 / 0.39 (0.07) | 0.91 / 0.00 (0.00) | 0.92 / 0.04 (0.00) | 0.93 / 0.05 (0.00) | 0.91 / 0.00 (0.00) |
| a1.0_s2 | 0.055 | 0.070 | 0.94 / 0.45 (0.06) | 0.95 / 0.45 (0.06) | 0.92 / 0.00 (0.00) | 0.92 / 0.01 (0.00) | 0.94 / 0.03 (0.00) | 0.92 / 0.00 (0.00) |

**power_treat** — verdict accuracy / flip-set F1 (predicted disagreement rate)

| cell | ε (floor) | obs dis | last_writer | first_writer | markov | tilt | overlap | base |
|---|---|---|---|---|---|---|---|---|
| a1.0_s0 | 0.052 | 0.072 | 0.94 / 0.45 (0.07) | 0.94 / 0.45 (0.07) | 0.93 / 0.00 (0.00) | 0.93 / 0.03 (0.00) | 0.94 / 0.07 (0.00) | 0.93 / 0.00 (0.00) |
| a1.0_s1 | 0.051 | 0.070 | 0.94 / 0.48 (0.07) | 0.94 / 0.48 (0.07) | 0.93 / 0.00 (0.00) | 0.93 / 0.01 (0.00) | 0.94 / 0.02 (0.00) | 0.93 / 0.00 (0.00) |
| a1.0_s2 | 0.059 | 0.061 | 0.93 / 0.45 (0.09) | 0.94 / 0.45 (0.09) | 0.93 / 0.00 (0.00) | 0.93 / 0.05 (0.00) | 0.93 / 0.04 (0.00) | 0.93 / 0.00 (0.00) |

**scale_110m** — verdict accuracy / flip-set F1 (predicted disagreement rate)

| cell | ε (floor) | obs dis | last_writer | first_writer | markov | tilt | overlap | base |
|---|---|---|---|---|---|---|---|---|
| a1.0_s0 | 0.071 | 0.071 | 0.91 / 0.36 (0.10) | 0.92 / 0.36 (0.10) | 0.90 / 0.00 (0.00) | 0.92 / 0.07 (0.01) | 0.92 / 0.05 (0.01) | 0.90 / 0.00 (0.00) |
| a1.0_s1 | 0.062 | 0.093 | 0.91 / 0.39 (0.10) | 0.92 / 0.39 (0.10) | 0.91 / 0.00 (0.00) | 0.91 / 0.04 (0.01) | 0.90 / 0.03 (0.00) | 0.91 / 0.00 (0.00) |
| a1.0_s2 | 0.060 | 0.072 | 0.92 / 0.45 (0.10) | 0.93 / 0.45 (0.10) | 0.93 / 0.00 (0.00) | 0.92 / 0.03 (0.00) | 0.92 / 0.05 (0.00) | 0.93 / 0.00 (0.00) |

**scale_11m** — verdict accuracy / flip-set F1 (predicted disagreement rate)

| cell | ε (floor) | obs dis | last_writer | first_writer | markov | tilt | overlap | base |
|---|---|---|---|---|---|---|---|---|
| a1.0_s0 | 0.065 | 0.073 | 0.90 / 0.40 (0.16) | 0.90 / 0.40 (0.16) | 0.86 / 0.00 (0.00) | 0.92 / 0.08 (0.01) | 0.90 / 0.06 (0.01) | 0.86 / 0.00 (0.00) |
| a1.0_s1 | 0.079 | 0.125 | 0.87 / 0.53 (0.15) | 0.91 / 0.53 (0.15) | 0.89 / 0.00 (0.00) | 0.91 / 0.00 (0.00) | 0.88 / 0.05 (0.01) | 0.89 / 0.00 (0.00) |
| a1.0_s2 | 0.062 | 0.110 | 0.91 / 0.37 (0.09) | 0.90 / 0.37 (0.09) | 0.88 / 0.00 (0.00) | 0.89 / 0.02 (0.00) | 0.91 / 0.01 (0.00) | 0.88 / 0.00 (0.00) |

**scale_29m** — verdict accuracy / flip-set F1 (predicted disagreement rate)

| cell | ε (floor) | obs dis | last_writer | first_writer | markov | tilt | overlap | base |
|---|---|---|---|---|---|---|---|---|
| a1.0_s0 | 0.076 | 0.078 | 0.89 / 0.30 (0.13) | 0.89 / 0.30 (0.13) | 0.86 / 0.00 (0.00) | 0.89 / 0.07 (0.01) | 0.89 / 0.06 (0.01) | 0.86 / 0.00 (0.00) |
| a1.0_s1 | 0.074 | 0.101 | 0.91 / 0.34 (0.10) | 0.90 / 0.34 (0.10) | 0.88 / 0.00 (0.00) | 0.89 / 0.00 (0.00) | 0.90 / 0.03 (0.00) | 0.88 / 0.00 (0.00) |
| a1.0_s2 | 0.063 | 0.074 | 0.93 / 0.42 (0.10) | 0.92 / 0.42 (0.10) | 0.90 / 0.00 (0.00) | 0.91 / 0.04 (0.00) | 0.92 / 0.04 (0.00) | 0.90 / 0.00 (0.00) |

**scale_41m** — verdict accuracy / flip-set F1 (predicted disagreement rate)

| cell | ε (floor) | obs dis | last_writer | first_writer | markov | tilt | overlap | base |
|---|---|---|---|---|---|---|---|---|
| a1.0_s0 | 0.075 | 0.080 | 0.89 / 0.40 (0.14) | 0.91 / 0.40 (0.14) | 0.87 / 0.00 (0.00) | 0.91 / 0.16 (0.02) | 0.91 / 0.08 (0.01) | 0.87 / 0.00 (0.00) |
| a1.0_s1 | 0.080 | 0.119 | 0.89 / 0.52 (0.11) | 0.93 / 0.52 (0.11) | 0.89 / 0.00 (0.00) | 0.90 / 0.10 (0.01) | 0.91 / 0.03 (0.00) | 0.89 / 0.00 (0.00) |
| a1.0_s2 | 0.067 | 0.075 | 0.91 / 0.35 (0.09) | 0.92 / 0.35 (0.09) | 0.89 / 0.00 (0.00) | 0.91 / 0.08 (0.01) | 0.92 / 0.04 (0.00) | 0.89 / 0.00 (0.00) |

## Figures


### power_nullswap

![01_prediction_vs_empirical.png](../power_nullswap/figures/01_prediction_vs_empirical.png)
![02_simplex_trajectories.png](../power_nullswap/figures/02_simplex_trajectories.png)
![03_joint_tables.png](../power_nullswap/figures/03_joint_tables.png)
![04_boundary_concentration.png](../power_nullswap/figures/04_boundary_concentration.png)
![05_decomposition_commutators.png](../power_nullswap/figures/05_decomposition_commutators.png)
![06_item_level_pred_vs_obs.png](../power_nullswap/figures/06_item_level_pred_vs_obs.png)
![07_overlap_null.png](../power_nullswap/figures/07_overlap_null.png)

### power_treat

![01_prediction_vs_empirical.png](../power_treat/figures/01_prediction_vs_empirical.png)
![02_simplex_trajectories.png](../power_treat/figures/02_simplex_trajectories.png)
![03_joint_tables.png](../power_treat/figures/03_joint_tables.png)
![04_boundary_concentration.png](../power_treat/figures/04_boundary_concentration.png)
![05_decomposition_commutators.png](../power_treat/figures/05_decomposition_commutators.png)
![06_item_level_pred_vs_obs.png](../power_treat/figures/06_item_level_pred_vs_obs.png)
![07_overlap_null.png](../power_treat/figures/07_overlap_null.png)

### scale_110m

![01_prediction_vs_empirical.png](../scale_110m/figures/01_prediction_vs_empirical.png)
![02_simplex_trajectories.png](../scale_110m/figures/02_simplex_trajectories.png)
![03_joint_tables.png](../scale_110m/figures/03_joint_tables.png)
![04_boundary_concentration.png](../scale_110m/figures/04_boundary_concentration.png)
![05_decomposition_commutators.png](../scale_110m/figures/05_decomposition_commutators.png)
![06_item_level_pred_vs_obs.png](../scale_110m/figures/06_item_level_pred_vs_obs.png)
![07_overlap_null.png](../scale_110m/figures/07_overlap_null.png)

### scale_11m

![01_prediction_vs_empirical.png](../scale_11m/figures/01_prediction_vs_empirical.png)
![02_simplex_trajectories.png](../scale_11m/figures/02_simplex_trajectories.png)
![03_joint_tables.png](../scale_11m/figures/03_joint_tables.png)
![04_boundary_concentration.png](../scale_11m/figures/04_boundary_concentration.png)
![05_decomposition_commutators.png](../scale_11m/figures/05_decomposition_commutators.png)
![06_item_level_pred_vs_obs.png](../scale_11m/figures/06_item_level_pred_vs_obs.png)
![07_overlap_null.png](../scale_11m/figures/07_overlap_null.png)

### scale_29m

![01_prediction_vs_empirical.png](../scale_29m/figures/01_prediction_vs_empirical.png)
![02_simplex_trajectories.png](../scale_29m/figures/02_simplex_trajectories.png)
![03_joint_tables.png](../scale_29m/figures/03_joint_tables.png)
![04_boundary_concentration.png](../scale_29m/figures/04_boundary_concentration.png)
![05_decomposition_commutators.png](../scale_29m/figures/05_decomposition_commutators.png)
![06_item_level_pred_vs_obs.png](../scale_29m/figures/06_item_level_pred_vs_obs.png)
![07_overlap_null.png](../scale_29m/figures/07_overlap_null.png)

### scale_41m

![01_prediction_vs_empirical.png](../scale_41m/figures/01_prediction_vs_empirical.png)
![02_simplex_trajectories.png](../scale_41m/figures/02_simplex_trajectories.png)
![03_joint_tables.png](../scale_41m/figures/03_joint_tables.png)
![04_boundary_concentration.png](../scale_41m/figures/04_boundary_concentration.png)
![05_decomposition_commutators.png](../scale_41m/figures/05_decomposition_commutators.png)
![06_item_level_pred_vs_obs.png](../scale_41m/figures/06_item_level_pred_vs_obs.png)
![07_overlap_null.png](../scale_41m/figures/07_overlap_null.png)