# Language-enrichment order dependence — NER category addition (blinded, sealed)

Companion experiment to `euh_pkg`. There, two *weighting* operators acted on a fixed verdict simplex.
Here the operators **change the language itself**: each enrichment pass adds a category to a token
classifier's label space (head widening + training on newly labelled data). We apply two enrichments
in both orders, with the composite outcome **predicted and sealed before it is run**, and score what
survives: does the order of *language acquisition* change what the final language says — and does it
change what remains of the old language?

Formal home: *Perfect Theory* §6.7 (Prop 6.4 — distinction-adding enrichment is verdict-non-monotone)
and *On Learning Languages* §3.4 (conservative enrichment: ι embedding, r retraction) & §5.4
(path dependence of representational learning). The euh_pkg experiment instantiates dynamical
incommensurability on a fixed language; this one instantiates non-commutativity of **enrichment**.

## Construction

Dataset: CoNLL-2003 (HF `eriktks/conll2003`), IO tagging (type only, no B-/I-).

* **Base language** Σ₀ = {O, PER, LOC}: base model trained with ORG and MISC tokens labelled O —
  those categories are *semantically occluded* (expressible only as silence/O).
* **Enrichment A** adds ORG: widen head by one fresh row (ι: old rows copied verbatim), train on
  sentences containing ORG entities (labels projected to Σ₀∪{ORG}).
* **Enrichment B** adds MISC likewise. ORG/MISC are deliberately confusable (nationalities,
  events, named products vs organisations), so the two enrichments *compete for tokens*.
* **Retraction** r: fold new-category probability mass into O and drop the row — the map back into
  the old language. KL-anchor during enrichment is applied to the **retracted** distribution
  (conservativity pressure: the enriched model should keep speaking the old language about old things).
* **Composites**: (base+A)+B and (base+B)+A. Both end at the same label *set*
  {O, PER, LOC, ORG, MISC} with different row orders; all comparisons are name-aligned.

## Protocol (per α, per seed) — sealed as in euh_pkg

1. Train base on Σ₀ (ORG/MISC → O in its data).
2. Train A and B from base (single enrichments). α scales B's learning rate (strength slider).
3. **SEAL** (SHA-256, before any composite exists) predictions of both composites from base/A/B only:
   * **claims null** — token t is *claimed* by X when v_X(t) ≠ v_base(t). Composite = base verdicts
     overwritten by first pass's claims, then second pass's claims (second wins conflicts).
     The two orders can differ **only** on the conflict set claims_A ∩ claims_B with different labels.
     Disagreement outside the conflict set = the second enrichment reacts to what the first did to the
     *representation*, not to the labels it left. Direct analog of euh_pkg's item-overlap null.
   * **Markov channel null** — 5×5 name-aligned verdict channels base→A, base→B, composed both orders.
   * last-writer / first-writer / base as degenerate baselines.
   Also sealed: predicted disagreement set, predicted retraction behaviour, claim rates, conflict rate.
4. Train both composites (+ replicates from the same A/B checkpoints → noise floor).
5. Score against sealed predictions:
   * order disagreement per token in the final language, vs the replicate floor and a
     **sentence-level** bootstrap floor (tokens within an entity are correlated);
   * conflict-set localisation: observed disagreement inside vs outside the sealed conflict set;
   * **retraction error**: retract both composites to Σ₀ — do the two orders leave the *same old
     language* behind? (Empirical (3.26): failure = enrichment is nonconservative and path-dependent
     at the language level, not merely the weight level.)
   * **improvement-verdict table** (Prop 6.4): for each checkpoint pair, is it an improvement under
     the old readout R₀ (retracted predictions, old gold) and under the enriched readout R₁ (full
     gold)? Non-monotone flips across the two readouts are the paper's predicted phenomenon.
   * Stuart–Maxwell / Bowker on the 5×5 order joint; entity-token-restricted variants of everything
     (most tokens are O; unrestricted rates understate the effect).

Every checkpoint (base fp32; A, B, composites, replicates fp16) is saved under `runs/<name>/ckpt/`
for post-hoc weight-space work (task vectors, HVP commutators, new-row subspace geometry).
Resumable at cell level (crash costs the in-flight cell only); idle models parked on CPU;
run folders timestamped; results zip excludes checkpoints.

## Run

```
run.bat experiment            # full battery (bert-base; a few hours on an 8 GB GPU)
run.bat experiment quick      # reduced grid
run.bat smoke                 # bert-tiny sanity, minutes
run.bat tiny                  # bert-tiny grid
run.bat base myrun            # single full-size stage
```

Output: `runs/<name>_<timestamp>/` with `ledger.json` (every per-token probability for every
checkpoint), `sealed_*.json`, `summary.json`, `figures/`, `log.txt`; batteries under
`runs/exp_<label>_<timestamp>/` and a `results_*.zip` (checkpoints excluded).

## Readouts (paper object → statistic)

| object | statistic |
|---|---|
| enrichment ι / retraction r | head widening; new-mass→O fold |
| conservativity (3.26) | retracted-KL anchor; retraction agreement with base |
| dynamical incommensurability | order disagreement above floors |
| claims/conflict null | disagreement in/out of sealed conflict set |
| Prop 6.4 non-monotonicity | improvement flips between R₀ and R₁ readouts |
| path dependence of language | retracted-composite divergence between orders |

## v1 simplifications (documented, revisit later)

* IO tagging, token-level F1 (span-level F1 is a TODO; token-level is the honest unit for the
  verdict algebra).
* Enrichment pools drawn independently; sentences containing both ORG and MISC may appear in both
  pools (they are exactly the conflict carriers). A shared-fraction slider like euh_pkg's is a
  natural follow-up, label-matched from day one.
* Contested-susceptibility null (logit geometry) not yet ported to the k-simplex.
* Dataset abstraction is minimal; Few-NERD (8 coarse types → richer enrichment menus) is the
  intended scale-up once the parquet availability is confirmed.
