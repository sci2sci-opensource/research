# Lab notes — the order-dependence experiments

**Date:** 15 August 2026
**Companion to:** *On Learning Languages* (OLL) and *Perfect Theory* (PT), drafts of 14 Aug 2026
**Code:** `euh_pkg/` (experiment 1), `ner_enrich_pkg/` (experiment 2)
**Data artifacts:** `runs/exp_full_20260815_151503` (euh), `runs/exp_full_20260815_213139` (ner), checkpoints on `D:\model_checkpoints\`

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
   hash *before* any composite exists. This is pre-registration enforced by code: we cannot
   retroactively adjust what we "expected."
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

Reading:

- **Order matters, above noise, and in the wrong place for the sufficiency story.** The verdict-level
  nulls don't just underpredict the effect; they predict it in the wrong location. Nearly all
  disagreement occurs on items where at most one pass had visibly moved the verdict — the second
  pass was reacting to invisible representation changes. This is the experiment's core exhibit:
  what benchmarks record is not what training acts on.
- **The negative control reads zero.** One operator in two costumes produces order differences fully
  explained by training noise. The instrument doesn't invent effects.
- **With the confound removed, sharing data *increases* order sensitivity** — the pilot's opposite
  trend was entirely the operator-degeneration artifact.
- **The effect is a scale phenomenon.** At bert-tiny, replicate noise (7–13% disagreement between
  *identical-order* reruns!) drowns everything. Interesting nuance: tiny's *aggregate* verdict
  distributions still differ by order very significantly — order effects at the readout level and
  at the item level can dissociate.
- The contested-susceptibility count gets the *scale* of the effect roughly right from sealed inputs
  (~10% capable items vs ~7–9% observed) and, after the confound fix, tracks the α-trend too.

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

- **Order matters here too, above floor — but now the sealed bookkeeping largely *works*.** The
  conflict set, sealed before any composite existed, localizes the effect at ~28× enrichment and
  accounts for most of its magnitude. Inversion of experiment 1: weighting-type interventions
  interact through hidden representation; **category acquisition interacts mostly out in the open**,
  through visible label competition. Same protocol, two regimes — and the difference between the
  two experiments is itself a measurement of *how opaque* an intervention type is.
- **The old language survives both acquisition paths identically** — to within noise. Whatever order
  you learn ORG and MISC in, what the model says in {O, PER, LOC} terms is the same. The
  conservativity anchor genuinely confines path-dependence to the acquired categories. As
  engineering advice this stands alone: *KL-anchor on the retracted distribution if you want
  order-robust continual learning of new classes.*
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
  scale. So the honest law is not "capacity buys monotonicity" but **"capacity buys down the price
  of a new distinction"** — and "did this training help?" still has no readout-independent answer;
  the readouts just disagree by less when the model is big enough. This is the paper's abstract
  non-monotonicity result (Prop 6.4) wearing overalls, with an error bar.

---

## 3. The quantum-measurement toolbox — what we borrowed, why, and what each instrument said

Some vocabulary first, because "quantum" earns instant suspicion. Nothing here claims models are
quantum systems. The borrowed apparatus is the **operational theory of measurements that disturb
what they measure** — developed for physics, applicable to *any* process where extracting/imprinting
information changes the system, which sequential fine-tuning obviously is. Concretely: a
fine-tuning pass both *acts on* the model and *is read out through* benchmarks — the same structure
(instrument + readout) that quantum measurement theory formalizes. The honest reading of that
formalism (which the papers defend) is epistemic: the algebra describes what an observer can
extract and how extraction updates their description — not exotic physics. That makes the tools
legitimately transplantable, and — crucially — makes their *constraints* testable: quantum-shaped
instruments obey identities that generic disturbing processes don't. Each identity is a free
experiment.

**QQ equality** — *what it is:* in survey research, asking two yes/no questions in both orders
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

**Instrument context-independence ("deficiency")** — *what it is:* in a proper operator algebra,
"the T operation" is one object regardless of what state it acts on. *Our test:* fit T's verdict
table from base→T, fit it again from S→(S then T), compare, against a bootstrap estimate of pure
fitting noise. *Result:* the two differ by **1.3–4.8× fit noise** across the grid. There is no
single "T operation" at the verdict level — only a family indexed by context. This is the cleanest
quantitative statement that the verdict-level algebra fails to close.

**The commutator** — *what it is:* the textbook non-commutativity measure, ‖Φ_S Φ_T − Φ_T Φ_S‖ for
the fitted verdict tables. *Result:* **pure estimation noise** (z between −0.2 and +0.1 against a
bootstrap null). The most quantum-*looking* statistic carries nothing — because the real
non-commutativity lives below the level the tables are fitted at. We keep this in the record as a
deliberate null: the naive translation of the formalism measures nothing; the refined ones above do.

**The geometry race (amplitudes)** — *what it is:* quantum states are amplitudes (square roots of
probabilities); the suspicion was that model-output dynamics might compose more linearly in
amplitude space than in probability or log space. *Our test:* fit each pass as a linear map in
three coordinate systems — raw probabilities, log-ratios, √p — compose both orders, see which
predicts observed composites best. *Result:* **√p wins in 21 of 23 cells** (sign test p ≈ 3×10⁻⁵),
by a small (+0.25pp) but near-unanimous margin. The amplitude embedding is measurably the most
compositional of the three. No phases claimed — but "which geometry does training compose in?" now
has an empirical answer, and it's the quantum-flavored one.

**The interference grid** — *what it is:* the one place a "superposition" of models is honestly
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

**BCH / curvature test** — *what it is:* a physicist's reflex — if training passes are flows, the
order gap should be predicted to second order by the commutator of the flows, computable via
Hessian-vector products (the Baker–Campbell–Hausdorff correction). Given the interference result
we pre-registered failure. *Result:* **cos(observed gap, BCH prediction) = +0.005.** Not small —
orthogonal, with comparable norms. The observed gap is instead ~40% explained by first-order
"survivor asymmetry" (whose task vector survived being trained over) and ~60% off-plane structure
invisible to any low-order expansion. **SGD composition is non-perturbative in task vectors** at
these training lengths.

**α\*-coincidence** — *the hypothesis:* the QQ zero-crossing and the point where order-asymmetry in
aggregate verdict shares vanishes might be the same "balance point." *Result:* refuted — the
aggregate asymmetry Γ never crosses zero in our range (it tracks persistent last-writer dominance),
while the QQ diagonals cross at readout-dependent points. Order asymmetry is (at least)
two-dimensional, and even "where are the operators balanced?" has no readout-independent answer —
the papers' relativity-to-readout theme reappearing one level up.

---

## 4. What we think this adds up to

1. **Benchmark readouts are not sufficient records of training interventions** — demonstrated with
   sealed predictions, above noise floors, with a clean negative control. For the evals/audit
   world: two checkpoints with matching scores are *not* interchangeable objects; they can respond
   differently to identical further training, and ~98% of that divergence (for weighting-type
   interventions) is invisible to any verdict-level account.
2. **Intervention types differ in *transparency*.** Category acquisition (NER) is mostly label-visible
   and its conflicts are predictable in advance; loss-reweighting (EUH) is representation-opaque.
   The protocol measures where on that spectrum an intervention sits — which is exactly what you'd
   want to know before trusting a behavioral audit of it.
3. **Conservativity is purchasable.** A KL anchor on the retracted distribution empirically confines
   path-dependence to newly acquired capabilities (old-language divergence below noise). Cheap,
   actionable continual-learning recipe.
4. **Improvement is readout-relative under capacity constraints** — 38 measured verdict flips at
   bert-tiny, zero at bert-base. "Did the update help?" needs a declared readout to be a question.
5. **The algebra signal is real but lives in refined observables** (QQ drift, context-deficiency,
   amplitude geometry), not in the naive ones (channel commutators, BCH curvature). The
   quantum-measurement toolbox earned its keep as a *source of falsifiable identities* — most were
   violated, each violation informative, one (amplitude composition) quietly supported.

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

## 6. Postscript (16 Aug): the infrastructure turned out to be the third paper

The *Universal Language Learning Machine* draft formalizes, almost clause for clause, the
infrastructure these experiments forced us to build — before the draft existed:

- **Conservatization (ULLM Thm 5.1)** is what the checkpoint + append-only-ledger + deterministic-pool
  design implements: every exogenous input to a training cell (seeds, configs, data selection) is
  logged, so any cell state is reconstructible by re-simulation. The cell-level *resume* is
  literally the Replay map — the dry-run that resumed a live battery's ledger and skipped three
  finished cells without training a step was `Replay(c₀, E_t, k)` executing on real hardware.
- **The Forgetting Theorem (ULLM Thm 4.1) was lived before it was read**: the first quick battery,
  killed before resume logic existed, left four hours of states that no amount of further
  computation could re-enter — the ledger retained too little. The same afternoon we implemented
  the conservatization that makes the theorem's converse available. Cost of the lesson: ~2.5 GPU-hours.
- **Fork** = every replicate (same prefix, fresh reply stream) and the interference grid (continuations
  θ(a,b) attached beneath a replayed node).
- **"Itineraries, not endpoints" (ULLM §9.1)** now has numbers: ~75% of any single pass's
  weight-direction is reply-stream-specific (the seed-cosine null), and in the NER experiment two
  acquisition paths that *retract to the same old language* remain different enriched states. The
  node must be (P, h, E); the experiments measure how much of the state is h.

*Results dashboard (private): claude.ai artifact "Order-Dependence Ledger."*
