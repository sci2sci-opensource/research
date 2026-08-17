# EUH order-dependence — hypothesis ledger

Verdicts: **E** witnessed under the pre-registered rule · **H** refuted · **U** not resolved by this data (a definite verdict of non-resolution, not a probability over E/H).

## Datasets

| stage | model | mode | slider | cells | base acc | replicates |
|---|---|---|---|---|---|---|
| base_shared | bert-base-uncased | disjoint | shared | 8 | 0.860 | 2 |
| base_strength | bert-base-uncased | disjoint | strength | 15 | 0.860 | 3 |
| base_weighted | bert-base-uncased | weighted | strength | 4 | 0.865 | 2 |
| tiny_strength | google/bert_uncased_L-2_H-128_A-2 | disjoint | strength | 12 | 0.504 | 2 |

## Hypotheses × datasets

| # | hypothesis | rule | base_shared | base_strength | base_weighted | tiny_strength |
|---|---|---|---|---|---|---|
| **H1** | Order effect exceeds the composite's own seed noise | <sub>disagreement(S→T,T→S) ≥ 2× same-order replicate disagreement in ≥2/3 of cells</sub> | ⚪ U<br><sub>mixed: median 1.3× floor</sub> | ⚪ U<br><sub>mixed: median 1.4× floor</sub> | 🔴 H<br><sub>order disagreement ≤1.2× floor in 100% of cells</sub> | 🔴 H<br><sub>order disagreement ≤1.2× floor in 100% of cells</sub> |
| **H2** | Γ_U sign: S→T ends more neutral than T→S, seed-stable | <sub>mean Γ_U > 0, |mean| > 2·SE, positive in ≥80% cells</sub> | 🟢 E<br><sub>Γ_U = +0.050 ± 0.019, positive in 100% of cells</sub> | 🟢 E<br><sub>Γ_U = +0.017 ± 0.017, positive in 100% of cells</sub> | ⚪ U<br><sub>Γ_U = +0.014 ± 0.016, sign not stable</sub> | ⚪ U<br><sub>Γ_U = +0.014 ± 0.036, sign not stable</sub> |
| **H3** | Non-lumpability: verdict marginal is not a sufficient statistic | <sub>Markov composite Φ_S·Φ_T rejected (χ² p<0.01) in ≥2/3 of cells</sub> | 🟢 E<br><sub>Markov composite rejected (p&lt;0.01) in 100% of cells</sub> | 🟢 E<br><sub>Markov composite rejected (p&lt;0.01) in 100% of cells</sub> | 🟢 E<br><sub>Markov composite rejected (p&lt;0.01) in 100% of cells</sub> | 🟢 E<br><sub>Markov composite rejected (p&lt;0.01) in 100% of cells</sub> |
| **H4** | Order effect lives OUTSIDE the overlap of the two flip sets | <sub>≥90% of cross-order disagreement on items neither pass flipped or only one flipped</sub> | 🟢 E<br><sub>98% of order-disagreement lies outside the predicted overlap set</sub> | 🟢 E<br><sub>98% of order-disagreement lies outside the predicted overlap set</sub> | 🟢 E<br><sub>98% of order-disagreement lies outside the predicted overlap set</sub> | 🟢 E<br><sub>100% of order-disagreement lies outside the predicted overlap set</sub> |
| **H5** | Flip-set co-dependence tracks operator identity | <sub>disjoint objectives → overlap ratio ≈1; shared operator → ≫1</sub> | 🔴 H<br><sub>disjoint mode but overlap ratio 6.7× — operators still share a component</sub> | 🔴 H<br><sub>disjoint mode but overlap ratio 6.7× — operators still share a component</sub> | 🟢 E<br><sub>weighted (shared-pool) mode: overlap ratio 8.7× — flip sets co-dependent (one operator)</sub> | 🔴 H<br><sub>disjoint mode but overlap ratio 4.0× — operators still share a component</sub> |
| **H6** | Order effect concentrates at verdict boundaries | <sub>AUC(base top-2 margin → flip) ≥ 0.75</sub> | 🟢 E<br><sub>AUC(base margin → flip) = 0.89: order effect concentrates at verdict boundaries</sub> | 🟢 E<br><sub>AUC(base margin → flip) = 0.89: order effect concentrates at verdict boundaries</sub> | 🟢 E<br><sub>AUC(base margin → flip) = 0.88: order effect concentrates at verdict boundaries</sub> | 🟢 E<br><sub>AUC(base margin → flip) = 0.87: order effect concentrates at verdict boundaries</sub> |
| **H7** | Prop 6.3 specimen: readouts coincide, revisions differ | <sub>some cell with Stuart–Maxwell p>0.05 AND disagreement ≥2× floor</sub> | ⚪ U<br><sub>no cell shows coincident readouts with above-floor revision difference (not refutable by absence)</sub> | ⚪ U<br><sub>no cell shows coincident readouts with above-floor revision difference (not refutable by absence)</sub> | ⚪ U<br><sub>no cell shows coincident readouts with above-floor revision difference (not refutable by absence)</sub> | ⚪ U<br><sub>no cell shows coincident readouts with above-floor revision difference (not refutable by absence)</sub> |
| **H8** | Shared-fraction slider raises co-dependence | <sub>Spearman(α_shared, overlap ratio) ≥ 0.6</sub> | 🔴 H<br><sub>overlap ratio falls with shared fraction (ρ=-0.34)</sub> | ⚪ U<br><sub>needs the shared-fraction slider stage</sub> | ⚪ U<br><sub>needs the shared-fraction slider stage</sub> | ⚪ U<br><sub>needs the shared-fraction slider stage</sub> |
| **H9** | Negative control: one operator ⇒ no order effect | <sub>weighted mode: disagreement ≤ 1.5× floor</sub> | ⚪ U<br><sub>needs the weighted-mode control stage</sub> | ⚪ U<br><sub>needs the weighted-mode control stage</sub> | 🟢 E<br><sub>shared-operator control shows no order effect above floor (0.7×) — design diagnosis confirmed</sub> | ⚪ U<br><sub>needs the weighted-mode control stage</sub> |
| **H10** | The join destroys information | <sub>H(tuple) − H(join) ≥ 0.2 bit/item</sub> | 🟢 E<br><sub>publishing join(ST,TS) instead of the tuple destroys 0.42 bits/item (median)</sub> | 🟢 E<br><sub>publishing join(ST,TS) instead of the tuple destroys 0.34 bits/item (median)</sub> | 🟢 E<br><sub>publishing join(ST,TS) instead of the tuple destroys 0.22 bits/item (median)</sub> | 🟢 E<br><sub>publishing join(ST,TS) instead of the tuple destroys 0.29 bits/item (median)</sub> |
| **H11** | Calibrated non-lumpability: exceeds the replicate-noise statistic | <sub>obs χ² ≥ 2× median replicate-composite χ² in ≥2/3 of cells</sub> | 🔴 H<br><sub>observed non-lumpability ≈ noise level (median 1.1×)</sub> | 🔴 H<br><sub>observed non-lumpability ≈ noise level (median 0.9×)</sub> | 🔴 H<br><sub>observed non-lumpability ≈ noise level (median 1.0×)</sub> | 🔴 H<br><sub>observed non-lumpability ≈ noise level (median 0.7×)</sub> |
| **H12** | Calibrated localization: above-noise excess lies outside the overlap set | <sub>≥90% of excess (obs − replicate-noise rate) outside, ≥3 cells with ≥0.5% excess</sub> | 🔴 H<br><sub>above-noise excess mostly inside the overlap set (18% outside)</sub> | 🔴 H<br><sub>above-noise excess mostly inside the overlap set (18% outside)</sub> | ⚪ U<br><sub>above-noise excess ≥0.5% in only 1 cell(s) — nothing to localize</sub> | ⚪ U<br><sub>above-noise excess ≥0.5% in only 2 cell(s) — nothing to localize</sub> |
| **H13** | Sign consistency: order/floor ratio >1 almost everywhere | <sub>ratio >1× floor in ≥90% of ≥6 cells</sub> | 🟢 E<br><sub>ratio &gt;1× floor in 100% of 8 cells (median 1.3×)</sub> | 🟢 E<br><sub>ratio &gt;1× floor in 100% of 15 cells (median 1.4×)</sub> | ⚪ U<br><sub>fewer than 6 cells with floors</sub> | 🔴 H<br><sub>ratio &gt;1× floor in only 33% of cells</sub> |

## Bayesian update over theories of the composite

Each theory predicts every item's verdict for S→T and T→S from base, S, T only; likelihood uses ε = the cell's measured replicate floor. Uniform prior; posterior after the last cell of each stage.

**(a) composite packet** — per-item verdicts of S→T and T→S (tempered, n_eff=200 per cell)

| stage | last_writer | first_writer | markov | tilt | overlap | base | best | verdict acc of best |
|---|---|---|---|---|---|---|---|---|
| base_shared | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.936 |
| base_strength | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | **first_writer** | 0.942 |
| base_weighted | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.954 |
| tiny_strength | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | **tilt** | 0.947 |

**(b) order packet** — per-item disagreement indicator [v_ST ≠ v_TS], class-balanced log-lik (a theory that predicts no flips pays log ε on every observed flip); this is the statistic the order question is about

| stage | last_writer | first_writer | markov | tilt | overlap | base | best | flip-set F1 of best | observed disagreement |
|---|---|---|---|---|---|---|---|---|---|
| base_shared | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.453 | 0.079 |
| base_strength | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.444 | 0.064 |
| base_weighted | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.317 | 0.034 |
| tiny_strength | 0.500 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | **last_writer** | 0.370 | 0.060 |

<sub>Posterior concentration is relative to the theories entertained; an absent theory cannot acquire mass (§3.5). Per-item accuracy of the best theory is reported so a 'winner' that is merely least-wrong is visible as such.</sub>


### Per-cell verdict accuracy of each theory


**base_shared** — verdict accuracy / flip-set F1 (predicted disagreement rate)

| cell | ε (floor) | obs dis | last_writer | first_writer | markov | tilt | overlap | base |
|---|---|---|---|---|---|---|---|---|
| a0.0_s0 | 0.053 | 0.072 | 0.94 / 0.45 (0.07) | 0.94 / 0.45 (0.07) | 0.93 / 0.00 (0.00) | 0.93 / 0.03 (0.00) | 0.94 / 0.07 (0.00) | 0.93 / 0.00 (0.00) |
| a0.0_s1 | 0.055 | 0.070 | 0.94 / 0.48 (0.07) | 0.94 / 0.48 (0.07) | 0.93 / 0.00 (0.00) | 0.93 / 0.01 (0.00) | 0.94 / 0.02 (0.00) | 0.93 / 0.00 (0.00) |
| a0.25_s0 | 0.053 | 0.092 | 0.94 / 0.51 (0.07) | 0.93 / 0.51 (0.07) | 0.92 / 0.00 (0.00) | 0.92 / 0.03 (0.00) | 0.93 / 0.03 (0.00) | 0.92 / 0.00 (0.00) |
| a0.25_s1 | 0.052 | 0.068 | 0.94 / 0.42 (0.07) | 0.93 / 0.42 (0.07) | 0.92 / 0.00 (0.00) | 0.93 / 0.02 (0.00) | 0.93 / 0.04 (0.00) | 0.92 / 0.00 (0.00) |
| a0.5_s0 | 0.048 | 0.088 | 0.94 / 0.47 (0.07) | 0.93 / 0.47 (0.07) | 0.93 / 0.00 (0.00) | 0.93 / 0.01 (0.00) | 0.93 / 0.04 (0.00) | 0.93 / 0.00 (0.00) |
| a0.5_s1 | 0.059 | 0.074 | 0.93 / 0.45 (0.08) | 0.94 / 0.45 (0.08) | 0.92 / 0.00 (0.00) | 0.92 / 0.03 (0.00) | 0.93 / 0.03 (0.00) | 0.92 / 0.00 (0.00) |
| a1.0_s0 | 0.059 | 0.093 | 0.94 / 0.46 (0.09) | 0.91 / 0.46 (0.09) | 0.92 / 0.00 (0.00) | 0.92 / 0.02 (0.00) | 0.92 / 0.06 (0.01) | 0.92 / 0.00 (0.00) |
| a1.0_s1 | 0.064 | 0.074 | 0.93 / 0.38 (0.08) | 0.93 / 0.38 (0.08) | 0.91 / 0.00 (0.00) | 0.92 / 0.01 (0.00) | 0.93 / 0.03 (0.00) | 0.91 / 0.00 (0.00) |

**base_strength** — verdict accuracy / flip-set F1 (predicted disagreement rate)

| cell | ε (floor) | obs dis | last_writer | first_writer | markov | tilt | overlap | base |
|---|---|---|---|---|---|---|---|---|
| a0.1_s0 | 0.037 | 0.054 | 0.95 / 0.44 (0.06) | 0.96 / 0.44 (0.06) | 0.94 / 0.00 (0.00) | 0.94 / 0.04 (0.00) | 0.96 / 0.01 (0.00) | 0.94 / 0.00 (0.00) |
| a0.1_s1 | 0.036 | 0.053 | 0.95 / 0.43 (0.06) | 0.96 / 0.43 (0.06) | 0.94 / 0.00 (0.00) | 0.94 / 0.02 (0.00) | 0.96 / 0.00 (0.00) | 0.94 / 0.00 (0.00) |
| a0.1_s2 | 0.029 | 0.053 | 0.95 / 0.46 (0.07) | 0.95 / 0.46 (0.07) | 0.94 / 0.00 (0.00) | 0.95 / 0.01 (0.00) | 0.95 / 0.04 (0.00) | 0.94 / 0.00 (0.00) |
| a0.25_s0 | 0.038 | 0.053 | 0.95 / 0.47 (0.06) | 0.96 / 0.47 (0.06) | 0.94 / 0.00 (0.00) | 0.94 / 0.02 (0.00) | 0.95 / 0.05 (0.00) | 0.94 / 0.00 (0.00) |
| a0.25_s1 | 0.039 | 0.050 | 0.95 / 0.40 (0.06) | 0.95 / 0.40 (0.06) | 0.94 / 0.00 (0.00) | 0.94 / 0.01 (0.00) | 0.95 / 0.01 (0.00) | 0.94 / 0.00 (0.00) |
| a0.25_s2 | 0.036 | 0.050 | 0.95 / 0.45 (0.08) | 0.95 / 0.45 (0.08) | 0.94 / 0.00 (0.00) | 0.94 / 0.01 (0.00) | 0.94 / 0.08 (0.00) | 0.94 / 0.00 (0.00) |
| a0.5_s0 | 0.043 | 0.053 | 0.95 / 0.51 (0.07) | 0.95 / 0.51 (0.07) | 0.94 / 0.00 (0.00) | 0.94 / 0.04 (0.00) | 0.95 / 0.08 (0.00) | 0.94 / 0.00 (0.00) |
| a0.5_s1 | 0.045 | 0.048 | 0.95 / 0.45 (0.07) | 0.95 / 0.45 (0.07) | 0.94 / 0.00 (0.00) | 0.94 / 0.02 (0.00) | 0.95 / 0.03 (0.00) | 0.94 / 0.00 (0.00) |
| a0.5_s2 | 0.041 | 0.052 | 0.94 / 0.41 (0.09) | 0.94 / 0.41 (0.09) | 0.94 / 0.00 (0.00) | 0.94 / 0.05 (0.00) | 0.93 / 0.04 (0.00) | 0.94 / 0.00 (0.00) |
| a1.0_s0 | 0.051 | 0.072 | 0.94 / 0.45 (0.07) | 0.94 / 0.45 (0.07) | 0.93 / 0.00 (0.00) | 0.93 / 0.03 (0.00) | 0.94 / 0.07 (0.00) | 0.93 / 0.00 (0.00) |
| a1.0_s1 | 0.052 | 0.070 | 0.94 / 0.48 (0.07) | 0.94 / 0.48 (0.07) | 0.93 / 0.00 (0.00) | 0.93 / 0.01 (0.00) | 0.94 / 0.02 (0.00) | 0.93 / 0.00 (0.00) |
| a1.0_s2 | 0.050 | 0.061 | 0.93 / 0.45 (0.09) | 0.94 / 0.45 (0.09) | 0.93 / 0.00 (0.00) | 0.93 / 0.05 (0.00) | 0.93 / 0.04 (0.00) | 0.93 / 0.00 (0.00) |
| a2.0_s0 | 0.069 | 0.082 | 0.92 / 0.38 (0.09) | 0.92 / 0.38 (0.09) | 0.92 / 0.00 (0.00) | 0.92 / 0.02 (0.00) | 0.91 / 0.02 (0.00) | 0.92 / 0.00 (0.00) |
| a2.0_s1 | 0.072 | 0.114 | 0.90 / 0.47 (0.11) | 0.91 / 0.47 (0.11) | 0.91 / 0.00 (0.00) | 0.89 / 0.06 (0.00) | 0.89 / 0.03 (0.00) | 0.91 / 0.00 (0.00) |
| a2.0_s2 | 0.077 | 0.092 | 0.91 / 0.41 (0.10) | 0.92 / 0.41 (0.10) | 0.91 / 0.00 (0.00) | 0.91 / 0.04 (0.01) | 0.91 / 0.04 (0.00) | 0.91 / 0.00 (0.00) |

**base_weighted** — verdict accuracy / flip-set F1 (predicted disagreement rate)

| cell | ε (floor) | obs dis | last_writer | first_writer | markov | tilt | overlap | base |
|---|---|---|---|---|---|---|---|---|
| a0.5_s0 | 0.044 | 0.037 | 0.96 / 0.35 (0.05) | 0.95 / 0.35 (0.05) | 0.95 / 0.00 (0.00) | 0.94 / 0.02 (0.00) | 0.95 / 0.03 (0.00) | 0.95 / 0.00 (0.00) |
| a0.5_s1 | 0.046 | 0.029 | 0.96 / 0.33 (0.05) | 0.96 / 0.33 (0.05) | 0.95 / 0.00 (0.00) | 0.94 / 0.04 (0.01) | 0.95 / 0.05 (0.00) | 0.95 / 0.00 (0.00) |
| a1.0_s0 | 0.049 | 0.042 | 0.95 / 0.29 (0.06) | 0.94 / 0.29 (0.06) | 0.94 / 0.00 (0.00) | 0.94 / 0.04 (0.00) | 0.94 / 0.02 (0.00) | 0.94 / 0.00 (0.00) |
| a1.0_s1 | 0.047 | 0.029 | 0.95 / 0.30 (0.07) | 0.95 / 0.30 (0.07) | 0.94 / 0.00 (0.00) | 0.94 / 0.09 (0.01) | 0.95 / 0.06 (0.00) | 0.94 / 0.00 (0.00) |

**tiny_strength** — verdict accuracy / flip-set F1 (predicted disagreement rate)

| cell | ε (floor) | obs dis | last_writer | first_writer | markov | tilt | overlap | base |
|---|---|---|---|---|---|---|---|---|
| a0.1_s0 | 0.110 | 0.036 | 0.89 / 0.22 (0.20) | 0.89 / 0.22 (0.20) | 0.82 / 0.00 (0.00) | 0.96 / 0.00 (0.00) | 0.97 / 0.00 (0.00) | 0.82 / 0.00 (0.00) |
| a0.1_s1 | 0.061 | 0.049 | 0.95 / 0.47 (0.06) | 0.96 / 0.47 (0.06) | 0.95 / 0.00 (0.00) | 0.96 / 0.00 (0.00) | 0.96 / 0.00 (0.00) | 0.95 / 0.00 (0.00) |
| a0.1_s2 | 0.038 | 0.032 | 0.96 / 0.29 (0.06) | 0.96 / 0.29 (0.06) | 0.94 / 0.00 (0.00) | 0.95 / 0.00 (0.00) | 0.98 / 0.00 (0.00) | 0.94 / 0.00 (0.00) |
| a0.25_s0 | 0.113 | 0.044 | 0.89 / 0.26 (0.22) | 0.87 / 0.26 (0.22) | 0.83 / 0.00 (0.00) | 0.96 / 0.04 (0.00) | 0.94 / 0.00 (0.00) | 0.83 / 0.00 (0.00) |
| a0.25_s1 | 0.059 | 0.055 | 0.95 / 0.43 (0.05) | 0.96 / 0.43 (0.05) | 0.94 / 0.00 (0.00) | 0.96 / 0.00 (0.00) | 0.96 / 0.00 (0.00) | 0.94 / 0.00 (0.00) |
| a0.25_s2 | 0.035 | 0.035 | 0.96 / 0.35 (0.07) | 0.95 / 0.35 (0.07) | 0.94 / 0.00 (0.00) | 0.95 / 0.00 (0.00) | 0.96 / 0.00 (0.00) | 0.94 / 0.00 (0.00) |
| a0.5_s0 | 0.118 | 0.058 | 0.89 / 0.34 (0.24) | 0.86 / 0.34 (0.24) | 0.84 / 0.00 (0.00) | 0.95 / 0.03 (0.00) | 0.90 / 0.00 (0.00) | 0.84 / 0.00 (0.00) |
| a0.5_s1 | 0.059 | 0.061 | 0.95 / 0.47 (0.05) | 0.96 / 0.47 (0.05) | 0.94 / 0.00 (0.00) | 0.95 / 0.00 (0.00) | 0.95 / 0.00 (0.00) | 0.94 / 0.00 (0.00) |
| a0.5_s2 | 0.047 | 0.048 | 0.94 / 0.42 (0.10) | 0.94 / 0.42 (0.10) | 0.95 / 0.00 (0.00) | 0.95 / 0.00 (0.00) | 0.93 / 0.00 (0.00) | 0.95 / 0.00 (0.00) |
| a1.0_s0 | 0.150 | 0.081 | 0.89 / 0.42 (0.25) | 0.83 / 0.42 (0.25) | 0.86 / 0.00 (0.00) | 0.94 / 0.09 (0.01) | 0.85 / 0.07 (0.01) | 0.86 / 0.00 (0.00) |
| a1.0_s1 | 0.143 | 0.148 | 0.91 / 0.30 (0.07) | 0.90 / 0.30 (0.07) | 0.90 / 0.00 (0.00) | 0.90 / 0.03 (0.00) | 0.90 / 0.00 (0.00) | 0.90 / 0.00 (0.00) |
| a1.0_s2 | 0.092 | 0.078 | 0.93 / 0.46 (0.14) | 0.90 / 0.46 (0.14) | 0.90 / 0.00 (0.00) | 0.94 / 0.03 (0.00) | 0.91 / 0.05 (0.01) | 0.90 / 0.00 (0.00) |

## Figures


### base_shared

![01_prediction_vs_empirical.png](../base_shared/figures/01_prediction_vs_empirical.png)
![02_simplex_trajectories.png](../base_shared/figures/02_simplex_trajectories.png)
![03_joint_tables.png](../base_shared/figures/03_joint_tables.png)
![04_boundary_concentration.png](../base_shared/figures/04_boundary_concentration.png)
![05_decomposition_commutators.png](../base_shared/figures/05_decomposition_commutators.png)
![06_item_level_pred_vs_obs.png](../base_shared/figures/06_item_level_pred_vs_obs.png)
![07_overlap_null.png](../base_shared/figures/07_overlap_null.png)

### base_strength

![01_prediction_vs_empirical.png](../base_strength/figures/01_prediction_vs_empirical.png)
![02_simplex_trajectories.png](../base_strength/figures/02_simplex_trajectories.png)
![03_joint_tables.png](../base_strength/figures/03_joint_tables.png)
![04_boundary_concentration.png](../base_strength/figures/04_boundary_concentration.png)
![05_decomposition_commutators.png](../base_strength/figures/05_decomposition_commutators.png)
![06_item_level_pred_vs_obs.png](../base_strength/figures/06_item_level_pred_vs_obs.png)
![07_overlap_null.png](../base_strength/figures/07_overlap_null.png)

### base_weighted

![01_prediction_vs_empirical.png](../base_weighted/figures/01_prediction_vs_empirical.png)
![02_simplex_trajectories.png](../base_weighted/figures/02_simplex_trajectories.png)
![03_joint_tables.png](../base_weighted/figures/03_joint_tables.png)
![04_boundary_concentration.png](../base_weighted/figures/04_boundary_concentration.png)
![05_decomposition_commutators.png](../base_weighted/figures/05_decomposition_commutators.png)
![06_item_level_pred_vs_obs.png](../base_weighted/figures/06_item_level_pred_vs_obs.png)
![07_overlap_null.png](../base_weighted/figures/07_overlap_null.png)

### tiny_strength

![01_prediction_vs_empirical.png](../tiny_strength/figures/01_prediction_vs_empirical.png)
![02_simplex_trajectories.png](../tiny_strength/figures/02_simplex_trajectories.png)
![03_joint_tables.png](../tiny_strength/figures/03_joint_tables.png)
![04_boundary_concentration.png](../tiny_strength/figures/04_boundary_concentration.png)
![05_decomposition_commutators.png](../tiny_strength/figures/05_decomposition_commutators.png)
![06_item_level_pred_vs_obs.png](../tiny_strength/figures/06_item_level_pred_vs_obs.png)
![07_overlap_null.png](../tiny_strength/figures/07_overlap_null.png)