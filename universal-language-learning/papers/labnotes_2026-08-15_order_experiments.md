# Lab notes — the order-dependence experiments

**Date:** 15 August 2026 · revised 27 August 2026 (re-runs, matched controls, contextual fraction,
and reconciliation audit)
**Companion to:** *On Learning Languages* (OLL) v32, 25 Aug 2026; *Perfect Theory* (PT) v22,
26 Aug 2026; *Universal Language Learning Machine* (ULLM) v7, 27 Aug 2026
**Archived:** Zenodo, *Universal Language Learning series* — DOI [10.5281/zenodo.21971310](https://doi.org/10.5281/zenodo.21971310) (concept, latest version)
**Code:** `euh_pkg/` (experiment 1), `ner_enrich_pkg/` (experiment 2)
**Data artifacts (17 Aug re-runs supersede the 15 Aug batteries):**
`euh_pkg/runs/exp_full_20260817_124411` (sealed H1–H13), `exp_power_20260817_173817` (m=4, null-swap,
scale curve; H14–H16);
`ner_enrich_pkg/runs/exp_full_20260817_143553` (N1–N5 incl. the β=0 ablation),
`exp_control_20260817_202041` (matched null-swap; N6).
Checkpoints on `D:\model_checkpoints\`; the 15 Aug batteries' weights were deleted after the
17 Aug re-runs reproduced their headline numbers (results packages and ledgers retained).

> **A note on this revision.** The 17 August pass added matched controls to both experiments and a
> contextuality test that no earlier battery contained. Several readings in the first draft were
> wrong and are corrected in place rather than quietly dropped — the H11 calibration is degenerate
> by construction (§1.4), the euh order effect is not attributable to the two operators differing
> (§1.5), the enrichment-vs-reweighting gap measures the token population rather than the
> intervention type (§2.3), and the results sort onto PT §6.8's ladder differently than we first
> framed them (§4).

These notes retell the two experiments in plain ML language — what we built, why we built it that
way, what broke, and what came out. The papers state the claims formally; this document is for a
reader who trains models for a living and wants to know what we actually did and what the numbers
mean, without first absorbing the papers' apparatus.

---

## 0. The question, in one paragraph

When you evaluate a model on a benchmark, you get a summary: per-item predictions, accuracies,
maybe a confusion table. Everyone quietly treats that summary as *enough* — if two checkpoints
score the same, they're "the same model" for practical purposes. But training is a process, not a
score, and two checkpoints with identical readouts may have arrived there by different roads. The
question both experiments attack: **is the benchmark readout a sufficient record of what training
did to the model?** Operationally: if I apply two training interventions in both orders (A then B,
vs B then A), can the readouts of the *single* interventions predict what the *composite* will do —
and does order even matter? If order matters in ways the readouts can't predict, then behavioral
snapshots systematically erase decision-relevant information about models. That's a claim with
teeth for anyone doing evals, audits, model merging, or continual learning.

Both experiments follow the same discipline, which is the actual methodological product here:

1. **Train the ingredients** (base model, intervention A alone, intervention B alone).
2. **Predict the composites** (A→B and B→A) from the ingredients only, using several competing
   prediction rules ("nulls"), and **seal the predictions** — write them to disk with a SHA-256
   hash *before* any composite exists. The current pipeline makes seals append-only. One cell in
   the first full battery predates that guard and was resealed during restart; it is disclosed and
   excluded from sealed-prediction claims in §1.4.
3. **Train both composites**, plus *replicates* — extra reruns of each composite from the same
   ingredients with different seeds. The disagreement between same-order replicates is the
   **noise floor**: the amount of disagreement you get from training stochasticity alone. Any
   claimed "order effect" must exceed this floor, or it's noise wearing a costume. In our reading
   of the literature this control is almost always missing.
4. **Score observed vs sealed.** Where the effect lands relative to each null's prediction tells
   you *which picture of training* survives contact with the data.

---

## 1. Experiment 1 — EUH: does the order of two fine-tuning passes matter?

### 1.1 Setup and rationale

**Task:** natural language inference on SNLI. Every item is a premise/hypothesis pair and the model
outputs one of three verdicts: **E** (entailed/witnessed), **U** (undetermined/neutral), **H** —
which in the papers stands for **hallucination**: the claim is refuted by what's in front of you.
SNLI operationalizes H as "contradiction," which is the same verdict wearing a linguist's coat: the
model asserting something the evidence contradicts. We chose a 3-way verdict task deliberately:
three outcomes is the smallest "language" in which the interesting structure (a distinguished middle
"can't-resolve" verdict, an absorbing "refuted" one) exists, and it matches the E/U/H verdict
algebra used throughout the papers.

**Model:** bert-base-uncased with a 3-way head (plus bert-tiny as a scale contrast). Small by 2026
standards, but that's a feature: the whole protocol (39 training cells × up to 8 passes each) has
to fit repeated full runs on one RTX 3070.

**The two interventions.** We wanted two *genuinely different* operations — not one operation in two
costumes — so:

- **S ("sharpening"):** trained only on E- and H-labelled items with a binary E-vs-H loss. It gets
  *no gradient at all about U*. Think: an intervention that makes the model more decisive.
- **T ("neutral improvement"):** trained with a U-vs-not-U loss on its own pool of items. Think:
  an intervention that improves recognition of unresolvable items.

Their training pools are **disjoint** (no shared items), so any interaction between them must go
through the model's internals, not through shared data. Each pass is KL-anchored to the checkpoint
it starts from (a standard "don't wander too far" regularizer), which also mirrors how real-world
sequential fine-tunes are usually leashed.

A **control dial α** scales T's learning rate — from "T is a light touch" (α=0.1) to "T is a
sledgehammer" (α=2.0). A second experiment variant (`base_shared`) instead uses α to control the
*fraction of shared items* between the two pools — a co-dependence dial. And a **negative
control** (`base_weighted`) uses two class-weighted versions of the *same* 3-way loss on the *same*
pool — i.e., deliberately "one operation in two costumes" — where a correctly built instrument must
report *no* order effect.

### 1.2 The sealed prediction rules ("nulls")

Each null is a different theory of *what a fine-tuning pass is*. If a null predicts the composites
well, that theory of training is adequate; where it fails, the failure's location is informative.

- **Markov channel.** Treat a pass as a 3×3 table: "of the items that were E before the pass, what
  fraction ended E/U/H after it," etc. Predict A→B by multiplying the two tables. This is the
  "the benchmark verdict is a sufficient statistic" theory — if it held, you could reason about
  training interventions entirely at the level of confusion tables.
- **ALR-affine.** Same idea but on the continuous probabilities instead of hard verdicts: represent
  each item's probability triple in log-ratio coordinates and fit a linear map per pass. A richer,
  geometry-aware version of the same "training is a map on outputs" theory.
- **Item-overlap.** A per-item bookkeeping rule: each pass "flips" some items (changes their
  verdict); predict the composite by applying the first pass's flips, then the second's. Under
  this rule the two orders can differ **only on items both passes flipped** (the overlap of their
  flip sets). This null is the sharpest instrument in the kit, because it converts "order matters"
  into a *location* claim: disagreement outside the overlap set means the second pass responded to
  something the first pass did to the model's *representation* — something that never showed up in
  any verdict.
- **Contested-susceptibility** (added after the pilot). Not a composite predictor, but a sealed
  *scale estimate*: count items where both passes move the output probabilities further than the
  item's distance to a decision boundary. These are the items *capable* of order sensitivity.

### 1.3 The pilot, and the confound we caught

A quick pilot run produced an exciting headline: at zero pool-sharing, **8.85%** of items got
different verdicts depending on order — ~60× more than the overlap null predicted, with nearly all
of it outside the overlap set. It also produced a seductive trend: sharing items between the pools
seemed to *reduce* the order effect.

That trend was an artifact, and catching it changed the design. In the original shared-pool
construction, cranking the sharing dial silently changed *what T was*: at full sharing T's pool
became all-E/H items, so its U-vs-not-U loss degenerated into "suppress U everywhere" — its
single-pass flip rate exploded from 7% to 32%. We were conflating "more co-dependence" with
"a completely different, much stronger operator." The fix — **label-matched sharing**, where T
always keeps its own U items and only the E/H portion of its pool is shared — holds the operator
fixed while varying co-dependence. This is worth a lab-notes moral: *a slider that changes the
data composition of an operator changes the operator.*

### 1.4 Results (full battery: 5 α values × 3 seeds, 3 replicates; shared variant 4 α × 2 seeds)

| stage | order disagreement | vs noise floor | where it lands |
|---|---|---|---|
| disjoint operators (bert-base) | 5.3% → 9.2% of items (rising with α) | **1.2–1.6× above floor** | **97–98% outside the overlap set** |
| shared-pool dial (label-matched) | 7.1% → 8.4% (rising with sharing) | 1.3–1.5× above | ~98% outside |
| negative control (one operator) | 3.3–3.5% | **0.7× — at/below floor** | — |
| bert-tiny | 3.9–10.2% | 0.7–0.8× — swamped by noise | — |

Reading — and first, what the project's own sealed verdict rules say, because they outrank this
prose. The pre-registered hypothesis ledger (H1: "order disagreement ≥ 2× replicate floor in ≥ ⅔
of cells") returns **U — not resolved — on both bert-base stages** (median 1.4× and 1.3×). The
excess is positive in every cell, but it does not clear the bar the experiment set for itself
before the data arrived, so the item-level *magnitude* claim is officially unresolved: a real
effect smaller than the declared resolution, or noise the floor underestimates — the ledger does
not say, and neither may we.

A further audit finding cuts deeper (all numbers reproducible from the committed ledgers):
**the H3/H4/H6 rules as sealed do not discriminate context-dependence from other causes.** H3's
χ² rejects the Markov composite even when the "observed composite" is replaced by a *same-order
replicate* in 19/19 tested cells; H4's outside-overlap fraction is **identical for observed
disagreement and replicate noise** (0.92 vs 0.92 on base_strength; 0.86 vs 0.86 on the control);
H6's boundary AUC fires on the control too (0.88). The euh claim that survives with a
discriminating rule is **H2 (Γ_U marginal-sign: E on base stages, correctly U on control and
tiny)**.

Two corrections to our own reading of that finding, both from the 2026-08-17 re-analysis
(`analysis/stratified_lumpability.py`), plus a clarification of which question the statistic
answers at all.

*The replicate substitution is not a noise null.* We originally read H3's behaviour as "noise
alone suffices to reject the Markov composite." That is wrong. A same-order replicate is another
run of the *same* composite, so it carries the same systematic non-lumpability as the
observation; the two are exchangeable and the ratio sits at ~1 whether or not the lumpable model
is false. The same flaw makes the calibrated **H11 degenerate**: measured across all four stages
its ratio is 0.95–1.16×, exactly what the construction forces, so its H verdict cannot be read
as "non-lumpability is at noise level." Against a null that *can* fail — a parametric bootstrap
under the lumpable model, resampling items and re-estimating both channels inside the null — the
observed χ² is **15.6–20.7× the null median, p < 0.007 in every cell-order tested**. The verdict
alphabet is genuinely not a closed description, and by a wide margin. (H11's ~1 does carry one
piece of information its rule never intended: the deviation *reproduces across independent runs*,
so it is systematic rather than run noise.)

*It is not item heterogeneity either.* Stratifying by base margin shrinks the excess (5.2× at 4
strata, 2.0× at 16), but stratifying on a *shuffled* covariate of identical granularity shrinks
it just as much (5.3× and 2.1×). The reduction is a mechanical parameter-count effect; margin
explains nothing.

*Which boundary this belongs to.* The Markov composite is the "declared readout is a sufficient
statistic" theory, so its failure is a statement about **comparison adequacy** — whether the
verdict alphabet supplies an operationally adequate common description (PT §6.1–6.2) — and not
about revision order. That is exactly why the single-operator negative control, where H9 confirms
no order effect at all (0.7× floor), shows non-lumpability just as strongly: **20.7× versus
20.0×** in the two-operator stage. PT keeps these apart deliberately: §6.4 notes that the
contextual fraction "says nothing by itself about the order of revision operations," and §6.8
lists an inadequate common comparison, a missing global noncontextual model, and order-dependent
revision as three *different* rungs of one ladder. Our χ² statistic lives on the first rung. It
should not be cited for either of the other two, and the control is what shows why.

Properly noise-calibrated versions of H3/H4 belong in a sealed set (H11–H13 were added for the
2026-08-17 battery); the bootstrap null above is post-hoc and is reported as such, alongside the
sealed H11 verdict as recorded rather than in place of it.

One seal is restart-contaminated: for `base_strength/a0.25_s0` the committed seal was rewritten
on a resume (18:13) after an aborted first attempt had already trained that cell's composites
(sealed 17:21, hash `63250a6b…`, surviving in `log.txt` with near-identical headline statistics).
That cell is excluded from sealed-prediction claims; sweep.py now refuses to overwrite seals
(append-only, cells marked `resealed`).
- **The original negative control stays below the declared 2× magnitude threshold.** One operator
  in two costumes produces 0.7× the replicate floor under H9. The more sensitive pairwise analysis
  in §1.5 later resolves a small systematic component in a matched control, so this result supports
  the threshold-specific H9 verdict rather than an absolute absence of order sensitivity.
- **With the confound removed, sharing data *increases* order sensitivity** — the pilot's opposite
  trend was entirely the operator-degeneration artifact.
- **The effect is a scale phenomenon.** At bert-tiny, replicate noise (7–13% disagreement between
  *identical-order* reruns!) drowns everything. Interesting nuance: tiny's *aggregate* verdict
  distributions still differ by order very significantly — order effects at the readout level and
  at the item level can dissociate.
- The contested-susceptibility count gets the *scale* of the effect roughly right from sealed inputs
  (~10% capable items vs ~7–9% observed) and, after the confound fix, tracks the α-trend too.

### 1.5 The power battery (2026-08-17): can the 2× bar be cleared at all?

The v1 floor rested on a **single replicate pair per cell**, which is why sibling seeds at the same
α reported 1.82× and 1.06×. The `--power` battery attacks the measurement rather than the effect:
m = 4 runs per order (so the ratio rests on 12 within-order and 16 cross-order pairs instead of one
of each), a matched control arm, and a scale curve at fixed settings. The pairwise ratio is
m-independent in expectation, so more replicates sharpen it without inflating it — unlike ensemble
averaging, which would have let us buy the threshold with compute.

Three proposed routes to the bar failed over the tested learning-rate range, model scales, and
estimators:

- **Displacement doesn't work.** Across a 20× range in lr_T (α = 0.1 → 2.0), order disagreement
  grows 1.7× and the floor grows 2.0×, so the ratio *declines* (1.47× → 1.20×, fit −0.065/α).
  Order-sensitivity and seed-sensitivity scale together. We had predicted the opposite — the
  commutator is bilinear in the two step sizes while the noise is first order — and that prediction
  is simply false here.
- **Scale doesn't work.** At fixed settings, 11M → 29M → 41M → 110M gives ratios 1.39×, 1.22×,
  1.23×, 1.26× (Spearman −0.20) while base accuracy climbs 0.748 → 0.849. The apparent v1
  tiny→base gain (0.85 → 1.35) was a config confound: tiny ran at different `n_base`/`epochs`/
  `n_pass` than base.
- **Better estimation doesn't work — it tightens rather than raises.** Same three cells, old
  single-pair statistic: 1.03–1.40. New pairwise statistic: **1.18–1.28**. The 0.37-wide scatter
  was estimator noise.

What the sharper instrument *does* deliver is a definite verdict where the 2× rule returned U.
Sealed **H14** ("a systematic, non-noise order component exists": cross-order minus within-order
pairwise disagreement, bootstrap CI excluding 0, in ≥⅔ of cells) returns **E in 100% of cells in
all six stages**, with 17–28% of cross-order disagreement classified as systematic. The effect is
resolved under the sealed H14 criterion and remains small relative to the 2× magnitude bar.

**The matched control (H15) is the informative negative.** `power_nullswap` replaces the second
operator with a second instance of the first — same objective, different data draw, everything else
identical — and shows *more* effect than the treatment (19% vs 17% systematic). Making the two
operators genuinely different in objective contributes nothing. The direction test agrees once it is
run symmetrically: Γ_U is stably positive in the treatment and scatters in the control, but that is
because both control passes are `binEH` and neither targets U, so the control cannot move that
coordinate by construction. Measured on the axis each arm actually has (NER, §2.3), *both* arms show
the same stable last-writer drift. **H16** (scale trend) returns **H**.

---

## 2. Experiment 2 — NER: does the order of *learning new categories* matter?

### 2.1 Rationale: from changing weights to changing the language

Experiment 1's two operators reweight behavior inside a *fixed* label set. The papers' deeper
subject is agents that change *the language itself* — acquire distinctions they previously couldn't
express. So experiment 2 makes the intervention literally that: **adding a category to the model's
label space.**

**Task:** CoNLL-2003 named-entity recognition, simplified to word-level type tags. The **base
language** knows only {O, PER, LOC} — and here's the crucial trick: it is trained on data where all
ORG and MISC entities are *labelled O*. From the base model's point of view, organizations and
miscellaneous entities are not "hard cases" — they are **inexpressible**; the language has no word
for them. (The papers call this *semantic occlusion*; the ML translation is "labels your ontology
doesn't have yet look like background.")

**The two enrichments:**

- **A** adds **ORG**: widen the classifier head by one freshly initialized row, train on sentences
  containing organizations.
- **B** adds **MISC**: same, for miscellaneous entities.

ORG and MISC were chosen *because they compete* — nationalities, events, product names sit
ambiguously between them — so the two acquisitions genuinely contend for the same tokens.

Two structural pieces the papers dictated, translated to ML:

- **Retraction:** the map "back into the old language" — take an enriched model's output and fold
  any new-category probability into O (since the old language expressed those tokens as O). This
  lets us ask, after any sequence of enrichments: *what does the model now say in the old
  language?*
- **Conservativity anchor:** during each enrichment, a KL penalty ties the *retracted* output
  distribution to the pre-enrichment model. In words: "learn the new category however you like,
  but keep saying the same things in the old language about old things." This is the papers'
  conservative-enrichment condition implemented as a loss term.

The sealed nulls adapt naturally. The star is the **conflict set**: tokens that *both* single
enrichments claim, with different labels (A says ORG, B says MISC). Under label-level bookkeeping,
order can matter *only there* — the second enrichment wins contested tokens. Disagreement outside
the conflict set again means representation-level interaction.

We also measure **improvement under two readouts**: R₀ = error in the old language (retracted
predictions, old gold labels) and R₁ = error in the enriched language (full gold). The papers
(PT, Prop 6.4) predict that adding a distinction can *flip* improvement verdicts — a model can get
better under the new readout while getting worse under the old one. We wanted to see whether that
actually happens in real models.

### 2.2 Results (full battery: 4 α × 3 seeds × 3 replicates, bert-base + bert-tiny)

| readout | bert-base | bert-tiny |
|---|---|---|
| order disagreement (entity-relevant tokens) | 7.2–9.0% | 3.4–19.3% |
| vs noise floor | **1.8–2.2× above** | 1.1–1.8× above |
| disagreement inside vs outside conflict set | **32–35% vs ~1.2%** (~28× enrichment) | 21–67% vs 1–3% |
| old-language agreement between the two orders (after retraction) | **99.7–99.8% — below noise floor** | 99.1–99.5% |
| R₀/R₁ improvement flips | **0** of 72 checks | **38 flips** |

Reading:

- **The entity-matched magnitude is the strongest result in either experiment.** With floor and
  effect measured in the same unit (entity-relevant tokens for both), the order/floor ratio has
  **median 2.02× with 8 of 12 bert-base cells at or above 2×** — this clears the bar the euh
  effect failed. The ledger is now ported: this is the sealed verdict **N1 = E** from the
  2026-08-17 battery, replicating the reported ratio to two decimals. Removing the KL anchor
  raises it further (**2.25×, 10/12 cells**), and bert-tiny stays correctly **U** (1.37×).
- **The conflict set strongly localizes a minority of the effect.** Sealed before any composite
  existed, it captures **17–31% (median 25%) of observed disagreement at ~28× enrichment** — a
  sharp beacon, not an account of the magnitude; most of the disagreement lies outside it.
  Directionally this still inverts experiment 1 (language-level order effects are far more
  label-visible than weighting-level ones), with the same caveat as euh's H4: outside-fraction
  comparisons need replicate-noise calibration before they carry weight.
- **With the KL anchor in place, the old language does not clear the order-effect bar.** Retracted
  to Σ₀ and floored in the matched unit, the two acquisition paths differ at median 1.4× the
  replicate floor with **no cell reaching 2×** — "does not clear the 2× threshold," not "below the
  noise floor." The completed β=0 ablation raises the median retracted ratio only from 1.44× to
  1.59×; sealed N5 remains U, while the conservativity verdict N2 falls from E to U. The ablation
  therefore leaves the anchor's causal effect unresolved. (Implementation note: the penalty is
  KL(retract(current) ‖ reference) — an earlier docstring stated the reverse direction.)
- **The improvement-verdict flip is real, floored, and graded by capacity.** First the floor
  (proposed by V): could replicate jitter manufacture a flip? No — across 192 replicate pairs
  (same intervention, different seed), the flip signature occurs **zero** times. The reason is
  structural: seed jitter moves both readouts *in the same direction* (a noisier run is worse under
  old and new readouts alike), while a genuine flip requires *anti-correlated* movement — exactly
  what a capacity trade-off produces. Against that zero-floor: **38 flips at bert-tiny** (34
  surviving stricter, jitter-calibrated thresholds) — enrichment improves the enriched readout
  while worsening the old one (typically −0.3pp new vs +0.8pp old). And a refinement the floor
  exposed at bert-base: the trade-off doesn't vanish with capacity, it shrinks an order of
  magnitude — 11/72 *small* flips (old-language cost ≲0.1pp) sit above base's much tighter jitter
  scale. These 11 raw sign flips do not satisfy the sealed N4 decision rule, which returns H on
  both base stages and E on tiny. Thus the table's 0/72 counts sealed, threshold-qualified flips,
  while the 11/72 figure records smaller raw reversals resolved by the tighter exploratory jitter
  analysis. Capacity buys down the measured price of a new distinction, and "did this training
  help?" still requires a declared readout. This is the paper's abstract non-monotonicity result
  (Prop 6.4) with an empirical error scale.

### 2.3 The matched control (2026-08-17): does the order effect need the distinctions to differ?

euh's null-swap arm showed its order effect survives replacing the second operator with a second
instance of the first. NER is where the project's positive magnitude result lives, so it needed the
same control. `ctrl_nullswap` has both passes add an arbitrary half of **one** category — ORG#1 and
ORG#2 — against `ctrl_treat`'s ORG and MISC, with `n_pass`, `n_base`, lr, anchor, seeds and
replicates all matched to the recorded `base_strength` at its α=1.0 slice (so the treatment arm
doubles as a replication of that stage; its pool line is identical, 997 cross-category sentences,
36358 eval tokens).

**Design note worth keeping.** The obvious construction — split ORG's *sentences* into two pools —
is not a null control. The same entity would be ORG#1 in one pool and ORG#2 in the other, so the two
enrichments would make contradictory claims about identical tokens: a maximal-conflict condition
that manufactures an order effect by construction. The split is therefore by **entity surface form**
via a deterministic hash, so each form keeps one sub-label everywhere and the two sub-categories are
consistent and mutually exclusive, exactly as ORG and MISC are (verified: 4960 vs 5065 tokens, zero
forms inconsistent between train and validation, conflict set correctly empty in a smoke run).

Sealed **N6** returns **H**: 64% systematic in the control against 49% in the treatment. But the raw
comparison is not like-for-like — the arbitrary split leaves the two halves semantically
indistinguishable, so the model cannot tell which half an unseen entity belongs to and the arms
contest very different amounts (sealed predicted conflict 0.036 vs 0.010, overlap ratios 19 vs 5.8;
pool overlap 2770 vs 997 sentences). Both asymmetries bias toward H.

The arm-normalized statistic compares each arm against **its own** sealed conflict prediction, written before any
composite existed (`analysis/conflict_normalized.py`): treatment **0.61**, control **0.70**, ratio
0.88. Both arms realise about two thirds of the order dependence their own conflict structure
implies, and the treatment shows no detectable excess over the control after this normalization.
Within this matched comparison, the identity of the added distinctions contributes no detected
increment beyond contest volume; the euh control result thereby recurs on another task and
intervention type.

This also dissolves the enrichment-versus-reweighting asymmetry we had briefly treated as the
headline. NER shows ~50% systematic against euh's ~20%, but NER's entity-matched population strips
the ~80% of tokens that are trivially `O`, leaving a contested subpopulation; euh's items have no
comparable dead weight. The gap measures the population, not the intervention type.

**The direction test, run symmetrically.** Per-label marginal drift C(AB) − C(BA), entity-matched:
the treatment moves MISC +0.029 and ORG −0.046; the control moves ORG#2 +0.141 and ORG#1 −0.153.
Both are stable across cells and show the same signature: the category added **last** is
over-represented. The control shows the signature 3–5× more strongly. This last-writer pattern is a
descriptive candidate mechanism for both arms; the present intervention does not isolate it
causally from the associated contest structure.

---

## 3. The quantum-measurement toolbox — what we borrowed, why, and what each instrument said

Some vocabulary first, because "quantum" earns instant suspicion. Nothing here claims models are
quantum systems. The borrowed apparatus is the **operational theory of measurements that disturb
what they measure** — developed for physics and usable as a source of candidate identities for
processes in which extracting or imprinting information changes the system. Sequential fine-tuning
has that intervention/readout structure. Concretely: a
fine-tuning pass both *acts on* the model and *is read out through* benchmarks — the same structure
(instrument + readout) that quantum measurement theory formalizes. The honest reading of that
formalism (which the papers defend) is epistemic: the algebra describes what an observer can
extract and how extraction updates their description — not exotic physics. That makes the tools
legitimately transplantable, and — crucially — makes their *constraints* testable: quantum-shaped
instruments obey identities that generic disturbing processes don't. Each identity is a free
experiment.

**QQ equality (exploratory)** — *what it is:* in survey research, asking two yes/no questions in both orders
changes answer distributions (order effects). The quantum question-order model predicts, with zero
free parameters, that one particular combination — P(yes,yes) + P(no,no), the "agreement rate" —
must be the *same* in both orders. Remarkably, this held across ~70 national surveys. *Our
mapping:* "answering question X" = X's pass leaving its verdict; order S→T gives answer pairs
(v_S, v_ST), order T→S gives (v_TS, v_T). *Why bother:* it's a sharp, parameter-free way to ask
"do these training operators have quantum-instrument structure?" — with either answer being
informative. *Result:* the identity is **violated with structure**: the deviation D drifts
monotonically with operator strength α and **crosses zero** (at α≈0.45 for the E-coarse-graining,
α≈1.06 for H), with a near-satisfying band between. Training operators aren't uniformly
quantum-shaped, but the QQ diagnostic sees an asymmetry structure the raw disagreement rate is
blind to.

**Contextual fraction (Contextuality-by-Default; added before the 17 August rerun, not sealed)** — *what it is:* PT §6.4 defines a graded
quantity. An empirical model is a family of context-wise joint distributions; a **global model** is
one distribution over all outcomes whose marginals reproduce every context. Failure of a global
model is contextuality, and CF = 1 − NCF measures the residual obstruction. Crucially, PT states in
the same paragraph that CF "says nothing by itself about the order of revision operations" — order
dependence and contextuality are different rungs of §6.8's ladder, and none of our sealed
hypotheses tested the second one. *Our test* (`analysis/cbd_contextuality.py`): two contents —
q₁ = "the S pass's verdict," q₂ = "the T pass's verdict" — each measured in two contexts, c₁ = order
S→T and c₂ = order T→S. That is a cyclic system of rank 2, the same structure used on survey
question-order data, and the CbD criterion reduces to

    CNTX = |ΔCorr between the orders| − (|Δ⟨R_S⟩| + |Δ⟨R_T⟩|)

with CNTX > 0 meaning contextual: the two-way correlation moved further than the shift in the
individual marginals can pay for. Verdicts are dichotomised against each label in turn. *Result:*
**CF ≈ 0.** NER: 0/15 tests in each arm. euh: 1/9 in the treatment, 0/9 in the control, and the
single positive (a1.0_s0, target U, +0.026) fails our own replication standard — the same test at
the other two seeds gives +0.004 and −0.103 — and sits within chance for 18 tests at a 95%
interval. The NER numbers show *how* it fails: the largest raw order signal anywhere in the project
(treatment, ORG: |ΔCorr| = 0.478) lands just inside a marginal budget of Δ₀ = 0.485. The order
effects are **direct influences** in the CbD sense — inconsistent connectedness — with essentially
nothing left over. *Caveats:* rank 2 is the weakest scenario available (CHSH-style tests are rank
4), we dichotomised a three-valued verdict, and we treated items as realisations of one system,
which is a modelling choice; a per-item-across-seeds construction asks a different question and the
replicates would support it.

**Instrument context-independence ("deficiency"; exploratory)** — *what it is:* in a proper operator algebra,
"the T operation" is one object regardless of what state it acts on. *Our test:* fit T's verdict
table from base→T, fit it again from S→(S then T), compare, against a bootstrap estimate of pure
fitting noise. *Result:* the two differ by **1.3–4.8× fit noise** across the grid. There is no
single "T operation" at the verdict level — only a family indexed by context. This is the cleanest
quantitative statement that the verdict-level algebra fails to close.

**The commutator (exploratory)** — *what it is:* the textbook non-commutativity measure, ‖Φ_S Φ_T − Φ_T Φ_S‖ for
the fitted verdict tables. *Result:* **pure estimation noise** (z between −0.2 and +0.1 against a
bootstrap null). The most quantum-*looking* statistic carries nothing — because the real
non-commutativity lives below the level the tables are fitted at. We keep this in the record as a
deliberate null: the naive translation of the formalism measures nothing; the refined ones above do.

**The geometry race (amplitudes; exploratory)** — *what it is:* quantum states are amplitudes (square roots of
probabilities); the suspicion was that model-output dynamics might compose more linearly in
amplitude space than in probability or log space. *Our test:* fit each pass as a linear map in
three coordinate systems — raw probabilities, log-ratios, √p — compose both orders, see which
predicts observed composites best. *Result:* **√p wins in 21 of 23 cells** (sign test p ≈ 3×10⁻⁵),
by a small (+0.25pp) but near-unanimous margin. The amplitude embedding is measurably the most
compositional of the three candidates tested. No phases are claimed; the result nominates the
square-root embedding for further comparison against a broader set of geometries.

**The interference grid (exploratory)** — *what it is:* the one place a "superposition" of models is honestly
preparable: θ(a,b) = θ_base + a·τ_S + b·τ_T, where τ = weight-difference ("task vector") of each
single pass. We evaluated a 6×6 grid of such mixtures, then projected the *actual* sequential
composites onto that plane. *A correction with a lesson:* our first pass at this reported that the
second pass contained essentially zero of its own direction — which would have been either profound
or meaningless, since near-zero cosines in 110M dimensions are what random vectors give. The
deciding control (proposed by V) is the **seed-cosine null**: cosine between two independent seeds
of the *same* pass from the *same* checkpoint — our saved replicates provide exactly this. The null
both corrected an unstable least-squares artifact and reframed the result. *Corrected result:* a
pass's direction is only **~25% seed-stable** to begin with (same objective, same start, different
seed: cos ≈ 0.22–0.27); applying it at a *different* starting checkpoint costs almost nothing
beyond that (cos ≈ 0.21–0.23). Each composite keeps ~0.98 of the *first* pass's task vector and
~0.23 — exactly the seed-stable core — of the *second's*. The ~70% off-plane residue is fully
accounted for by second-pass seed noise. So the first-order law of sequential SGD here is
symmetric and simple: **the first mover's direction survives in full; the second mover is
compressed to its stable core; the rest of any single run is seed-specific.** Behaviorally, the
naive merged model still agrees ~94% with either composite — and the residual few percent is the
measured order effect.

**BCH / curvature test (failure pre-registered after the interference analysis)** — *what it is:* a physicist's reflex — if training passes are flows, the
order gap should be predicted to second order by the commutator of the flows, computable via
Hessian-vector products (the Baker–Campbell–Hausdorff correction). Given the interference result
we pre-registered failure. *Result:* **cos(observed gap, BCH prediction) = +0.005.** Not small —
orthogonal, with comparable norms. The observed gap is instead ~40% explained by first-order
"survivor asymmetry" (whose task vector survived being trained over) and ~60% off-plane structure
invisible to this second-order approximation. Under these models, tasks, and training lengths, the
tested task-vector expansion does not describe SGD composition.

**α\*-coincidence (exploratory)** — *the hypothesis:* the QQ zero-crossing and the point where order-asymmetry in
aggregate verdict shares vanishes might be the same "balance point." *Result:* refuted — the
aggregate asymmetry Γ never crosses zero in our range (it tracks persistent last-writer dominance),
while the QQ diagonals cross at readout-dependent points. Order asymmetry is (at least)
two-dimensional, and even "where are the operators balanced?" has no readout-independent answer —
the papers' relativity-to-readout theme reappearing one level up.

---

## 4. What we think this adds up to

The three papers separate several properties that ordinary talk runs together, and the results land
on different ones. PT §6.8 gives the ladder: (1) no operationally adequate common comparison,
(2) locally compatible statistics but no global noncontextual model, (3) representational but not
dynamical commensurability — comparison works, revision is order-dependent, "perfection must be
indexed by the declared update protocol or path," (4) both, so a path-independent claim is well
typed. Sorted onto it:

1. **Rung 1 — the declared readout is not an adequate common description.** The Markov composite
   (verdict-as-sufficient-statistic) fails at **15.6–20.7× a bootstrap null that can fail,
   p < 0.007**, survives the margin-heterogeneity explanation (shuffled-strata placebo), and
   reproduces across independent runs. It appears identically in the single-operator control, which
   is the point: this is a statement about the coarse-graining, not about order. The companion
   result is **H10** — publishing `join(ST,TS)` instead of the tuple destroys 0.22–0.42 bits/item —
   which is OLL §4.4 verbatim: "if only s₁∨⋯∨s_k is published, the identities and disagreements of
   the reporters have been discarded."
2. **Rung 2 — the contextual fraction is ≈ 0.** Measured by CbD on a rank-2 cyclic system: 0/15 in
   both NER arms, 1/9 unreplicated in euh. Every order effect we produced is a **direct influence**
   in the CbD sense; a classical hidden state with order-dependent readouts reproduces the data. In
   the largest case the correlation shift (0.478) is almost exactly paid for by the marginal shift
   (0.485). This is a measurement of a quantity PT §6.4 defines, not a refutation of anything the
   papers assert — and PT is explicit that CF and revision order are separate questions.
3. **Rung 3 — this is where the experiments live.** Revision is order-dependent and the
   commuting-square condition of PT §6.6 fails, while the comparison itself remains available. That
   combination is exactly the **unsharp gap** PT §6.5 constructs: two observables that *are* jointly
   measurable — (√3+1)/2 < 2 — yet whose Lüders channels do not commute, so that "static gluing
   without dynamic gluing" (Prop 6.3) is possible. Our batteries exhibit the same operational
   separation between available static comparison and order-dependent revision. They do not
   establish that the learned operators are jointly measurable observables or Lüders instruments,
   so the unsharp construction is a formal analogue rather than an empirical model fitted here.
   Theorem 6.1 makes commutation, joint measurability and order-independent revision coincide for
   **sharp** observables. These coarse-grained probabilistic verdicts do not supply that sharp
   measurement structure, so order dependence alone licenses no contextuality inference.

Within rung 3, the order effect is **resolved by H14 as small, with no incremental operator-identity
effect detected by the matched controls**: sealed H14 = E in 100% of cells across six stages
(17–28% systematic); the 2× bar
returns U and was not reached by displacement across the tested 20× learning-rate range, by the
tested scale curve (ρ = −0.20 from 11M to 110M), or by better estimation (which tightens
1.03–1.40 to 1.18–1.28). Matched controls on both
tasks — euh's H15 (19% vs 17%) and NER's N6 (0.70 vs 0.61 against each arm's own sealed conflict
prediction) — show no detected increment from swapping *which* operators are used. Every arm has a
**last-writer signature on contested items**, with magnitude tracking contest volume and direction
tracking which pass went last. The strongest magnitude result remains
the **NER entity-matched effect (median 2.02×, 8/12 cells ≥2×, sealed N1 = E; 2.25× and 10/12 with
the anchor removed)**, now with its own ported ledger.

4. **Intervention types differ in *transparency*.** Category acquisition (NER) is mostly label-visible
   and its conflicts are predictable in advance; loss-reweighting (EUH) is representation-opaque.
   The protocol measures where on that spectrum an intervention sits — which is exactly what you'd
   want to know before trusting a behavioral audit of it. What we may *not* infer from the raw gap
   (NER ~50% systematic vs euh ~20%) is that language extension is intrinsically more
   order-sensitive: entity-matching strips the ~80% trivially-`O` tokens, so the gap measures the
   population, not the intervention type.
5. **Conservativity is observed; that the anchor *causes* it is not established.** With the KL
   anchor in place, path-dependence stays confined to newly acquired capabilities — the retracted
   old language sits below the 2× bar in **every cell** (sealed N2 = E, median 1.44×). The
   pre-registered ablation that would license the causal reading did **not** clear its bar: with
   the anchor removed the retracted effect moves only 1.44× → 1.59× (**N5 = U, 1.1×**), while
   conservativity degrades just enough to drop N2 to U. So the recipe is worth trying and the
   correlation is clean, but "the anchor buys conservativity" remains an unresolved causal claim
   on this data, not a demonstrated one.
6. **Improvement is readout-relative under capacity constraints** — 38 measured verdict flips at
   bert-tiny, **0/72 at bert-base in both the anchored and unanchored arms** (sealed N4: E on
   tiny, H on both base stages), against a flip floor of 0 expected. "Did the update help?" needs
   a declared readout to be a question.
7. **The algebra signal is real but lives in refined observables** (QQ drift, context-deficiency,
   amplitude geometry, CF), not in the naive ones (channel commutators, BCH curvature). What the
   borrowed apparatus supplied was a *source of falsifiable identities* — most violated, each
   violation informative, one (amplitude composition) quietly supported, and one (CF) returning a
   clean zero that places the experiments on a specific rung of PT's ladder. Note what the
   batteries do **not** touch: the phase-sensitive sections of OLL §6 and PT §6.7 are conditional
   on reference resources — intertwiners, calibration, cross-sector observables — that we never had
   and that OLL §6.3 says must be charged before they mean anything ("without that resource, adding
   complex amplitudes merely redescribes an empirically classical mixture"). Nothing here bears on
   them either way.

## 5. Infrastructure notes (for whoever reruns this)

- Every run: sealed `sealed_*.json` with SHA-256; full per-item probabilities for every checkpoint
  in `ledger.json`; every checkpoint's weights saved (base fp32, rest fp16) to `D:\model_checkpoints\`
  with junctions from `runs\<name>\ckpt`; cell-level resume (a crash costs one cell); batteries
  auto-resume; results zips exclude weights.
- Windows/8GB-GPU lessons that cost us hours: parked idle models on CPU (WDDM shared-memory
  spillover silently slows training >10×); UTF-8 everywhere (α in a log line killed a run under
  cp1252); pyarrow row-iteration access-violates on this stack — extract dataset columns wholesale.
- Reproduce: `run.bat experiment` in each package (~2.5h euh, ~35min ner on an RTX 3070).
  Rebuild reports from ledgers without retraining: `rescore.py` / `report.py`.

## 6. Postscript (16 Aug; revised 27 Aug): the infrastructure motivated the third paper

The infrastructure built for these experiments motivated several constructions later formalized in
*Universal Language Learning Machine*. The correspondences are architectural rather than claims
that the experimental runner satisfies every hypothesis of the formal machine:

- **Conservatization (ULLM Thm 4.1)** is approximated by the checkpoint, append-only-ledger, and
  deterministic-pool design. Seeds, configurations, and data selections record the declared
  exogenous inputs, while checkpoints preserve completed cell states directly. Exact
  reconstruction by re-simulation additionally depends on the software stack, numerical kernels,
  and hardware determinism; the present archive does not certify those conditions. Cell-level
  resume is therefore an engineering realization of retained-state re-entry, using checkpoints
  together with the ledger rather than reconstructing every state from the ledger alone.
- **The failure that motivates the Forgetting Theorem (ULLM Thm 2.1)** occurred in the first quick
  battery: after termination before resume logic existed, its intermediate states were absent from
  the retained interface and could not be resumed. Retraining might reproduce equivalent states
  under sufficiently controlled conditions, but the run itself supplied no re-entry path. The
  checkpoint-and-ledger design was implemented that afternoon. Cost of the lesson: ~2.5 GPU-hours.
- **Fork** = every replicate (same prefix, fresh reply stream) and the interference grid (continuations
  θ(a,b) attached beneath a replayed node).
- **Itinerary-indexed states (ULLM §8.1)** now have an empirical motivation: ~75% of any single pass's
  weight-direction is reply-stream-specific (the seed-cosine null), and in the NER experiment two
  acquisition paths that *retract to the same old language* remain different enriched states. The
  corresponding formal node is \((P,h,E_h)\). The experiments measure path-associated differences;
  they do not identify a unique decomposition of model state into \(P\), \(h\), and \(E_h\).
