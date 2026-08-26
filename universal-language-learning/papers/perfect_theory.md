---
title: "Perfect Theory"
date: "14 August 2026 — Revised Draft 21"
lang: en
---

# Abstract

Learning theory usually asks how an agent selects the best hypothesis from a fixed class. *On Learning Languages* [1] extends that problem to agents that can revise the language in which hypotheses are formed. This paper asks when such an agent may stop searching and call a theory done.

We would call a theory **Perfect** when no admissible alternative is better at any target. Making that judgment requires closed candidate and target domains and an operationally adequate comparison among the alternatives. I show that the simplicity of an improvement gives no computable bound on when even an exhaustive proposer will find it. Deciding that the declared search can never produce a certified improvement, and deciding Perfection over an unbounded effective domain, are $\Pi^0_1$-complete; deciding that no successor improves the current theory uniformly over that domain is $\Pi^0_2$-complete. Existence adds a further quantifier: deciding whether an effective comparison contract contains any Perfect presentation is $\Sigma^0_2$-complete, and unlike fixed-candidate Perfection this availability question is not computably identifiable in the limit. The co-enumerable completion claims still support an exact one-retraction procedure: treat the theory as complete unless a finite counterexample appears, but do not treat its continued survival as a certificate of completion. Computability is not the only obstacle. Completion also requires an adequate comparison structure. A shared statistical description may exist even when revisions remain order-dependent, and locally compatible comparisons may fail to combine into a neutral global language.

Finally, the **Omnipotence Theorem** considers an agent granted an arbitrarily strong computational oracle together with the full measurement interface permitted by its declared physical model. Such resources may close the earlier problems for which they were introduced. Once the grant becomes available for constructing new presentations and completion problems, however, the same hierarchy reappears relative to the enriched resource base. Even "magical" resources therefore yield only relative completion: they solve the old game while making a stronger game expressible. Where certification remains unavailable, the appropriate responses are bounded stopping, continued exploration for theories and comparison resources, and refutation.

\tableofcontents

# 1. When is a theory done?

Perfection is an ordinary word before it is a mathematical one. We call a construction perfect when no relevant alteration would improve it, and we call the work done when we are entitled to stop looking. Both expressions conceal quantifiers. Nothing is perfect without a domain of use, a class of alternatives, and a standard of comparison; nothing is known to be done without some reason for believing that those quantifiers have been discharged.

Most learning theories avoid this problem by fixing a hypothesis language. The learner compares represented hypotheses, updates their probabilities, and perhaps converges on one of them. A learner capable of changing its language faces a different problem. It may add a primitive, revise an ontology, replace an interpreter, strengthen a verifier, or alter the procedure by which successor theories are proposed. The present theory therefore determines not only what the agent believes, but also which improvements it can formulate, locate, compare, and certify.

The companion paper *On Learning Languages* [1] models this operation as updating over language presentations and the bounded procedures that search and verify within them. It proves a sharp instance--schema boundary: two supplied presentations can be compared on any fixed finite serialization in the declared $\mathrm{KT}$ class, while deciding whether one charged presentation dominates another on every finite serialization is $\Pi^0_1$-complete. The present paper asks what follows from that boundary. When does a language merely survive the search performed so far? When does it have no improving successor? When is it at least as good as every admissible alternative at every relevant target? And under what conditions may the agent certify any of these claims?

These questions must be separated because failure to find an improvement has several possible sources. No improvement may exist. An improvement may exist but be unreachable by the proposal procedure. It may be proposed but remain outside the available comparison structure. It may be comparable pointwise while the universal claim required for finality remains undecidable. Or it may be true and formally expressible but unprovable in the verifier currently available to the agent.

I use **Good**, **Final**, and **Perfect** for three increasingly strong properties. Good is operational: no reachable certificate presently defeats the theory. Final is extensional relative to an admissible successor class: no improving successor exists. Perfect adds a comparison-completeness condition and a pointwise one: every admissible alternative can be compared with the current theory, and none is locally better anywhere on the declared target domain. The word **Done** is reserved for the licensed announcement that the required perfection claim has been certified.

The resulting theory of perfection has two independent boundaries. The first is computational: even when every individual comparison is effective, the universal claim may not be. The second is representational: the alternatives may fail to admit a neutral comparison structure in the first place. The first boundary leads to the halting problem, limit identification, exploration, and refutation. The second leads to reference resources, joint measurability, contextuality, and order effects in revision. A complete account of when a theory is done requires both.

# 2. Finality contracts

## 2.1 Presentations, targets, and comparisons

Let $\mathcal Q$ be a declared class of candidate presentations, and let $P\in\mathcal Q$ denote the current presentation under evaluation. I use the presentation model introduced in *On Learning Languages* [1]:

$$
P_e=(\mathcal L_e,D_e,U_e),
\tag{2.1}
$$

where $\mathcal L_e$ is a language, $D_e$ is a partial linguistic decoder, and $U_e$ is an interpreter that runs expressions to produce further expressions. As in [1], proposal and verification procedures belong to a bounded realization of the presentation rather than to the presentation itself.

Let $\mathcal X$ be the declared target domain. Its elements may be finite serializations, contexts, prediction tasks, proof obligations, or other public comparison objects. A reference structure $\mathcal R$ supplies the readouts, translations, calibrations, and admissible operations by which the behaviour of two presentations is placed in a common comparison space. I write

$$
\operatorname{Cmp}_{\mathcal R}(P,Q;x)
\tag{2.2}
$$

when the comparison of $P$ and $Q$ at $x$ is operationally defined and adequate for the distinctions declared by the task. Adequacy is stronger than the existence of a byte encoding. A comparison must preserve the outputs, probabilities, costs, and interventions on which the declared objective depends.

When (2.2) holds, let $L_P^{\mathcal R}(x)$ be the charged loss of $P$ at $x$. It may include predictive loss, description cost, proposal cost, verification cost, presentation charge, or a declared vector of such quantities. For a scalar loss, define the task-relative pointwise dominance relation

$$
P\preceq_{\mathcal R,\mathcal X}Q
\iff
\forall x\in\mathcal X\;
\left[
\operatorname{Cmp}_{\mathcal R}(P,Q;x)
\ \wedge\ 
L_P^{\mathcal R}(x)\leq L_Q^{\mathcal R}(x)
\right].
\tag{2.3}
$$

Write $P\prec_{\mathcal R,\mathcal X}Q$ when $P\preceq_{\mathcal R,\mathcal X}Q$ and the inequality is strict for at least one target. On any subfamily for which comparison is reflexive and compositionally closed---that is, for all presentations $P,Q,R$ in the subfamily and every $x\in\mathcal X$,

$$
\operatorname{Cmp}_{\mathcal R}(P,P;x)
$$

and

$$
\operatorname{Cmp}_{\mathcal R}(P,Q;x)
\wedge
\operatorname{Cmp}_{\mathcal R}(Q,R;x)
\Longrightarrow
\operatorname{Cmp}_{\mathcal R}(P,R;x),
$$

the relation $\preceq_{\mathcal R,\mathcal X}$ is a preorder. These closure properties are imposed only where stated; elsewhere, $\preceq_{\mathcal R,\mathcal X}$ remains a typed dominance relation. For vector-valued objectives, the scalar inequality in (2.3) is replaced by the declared product or Pareto order. Nothing below requires a universal utility function, but every perfection claim requires an explicit order.

## 2.2 The finality contract

A **finality contract** is the data

$$
\mathfrak F
=
(\mathcal X,\mathcal Q,\leadsto,\mathcal R,\preceq,g,V,B).
\tag{2.4}
$$

Here $\mathcal X$ is the target domain, $\mathcal Q$ the admissible candidate class, $\leadsto$ the successor relation, $\mathcal R$ the comparison structure, and $\preceq$ the declared dominance relation. The effective proposer $g$ emits candidate moves and finite proof objects, $V$ checks those objects, and $B$ records the construction, comparison, and verification budgets when the claim is bounded. Components that are fixed by context may be suppressed, but not silently changed.

A finite object $\pi$ is an **improvement certificate** when

$$
V(P,Q,\pi)=1
\quad\Longrightarrow\quad
P\leadsto Q
\ \wedge\ 
Q\prec_{\mathcal R,\mathcal X}P.
\tag{2.5}
$$

The implication is the soundness requirement. Completeness is separate: a strict improvement may exist even when the verifier accepts no proof of it. Certificates may establish a symbolic theorem covering an unbounded domain; they need not consist of an exhaustive table of targets.

The contract is **comparison-complete for $P$** when

$$
\operatorname{Adeq}_{\mathfrak F}(P)
\iff
\forall Q\in\mathcal Q\;\forall x\in\mathcal X,
\operatorname{Cmp}_{\mathcal R}(P,Q;x).
\tag{2.6}
$$

Thus $\operatorname{Adeq}_{\mathfrak F}(P)$ requires every admissible $Q$ to be adequately comparable with $P$ at every target. Comparisons among alternatives $Q,Q'$ remain unspecified; they are required only by procedures that rank the candidate class as a whole.

## 2.3 Good, Final, and Perfect

The weakest status is operational survival.

**Definition 2.1 (Good).** A presentation $P$ is Good for the realized contract $\mathfrak F$ when the proposal process produces no accepted certificate of a strict improvement:

$$
\operatorname{Good}_{\mathfrak F}(P)
\iff
\nexists t,Q,\pi\;
[g(P,t)=(Q,\pi)\wedge V(P,Q,\pi)=1].
\tag{2.7}
$$

Good is indexed by an agent's effective reach. An inaccessible improvement does not prevent the status, even if it prevents any stronger claim.

When $B$ is a fixed finite budget and the bounded run is effectively exhaustible, bounded Good is decidable. Definition 2.1 allows an unbounded effective proposal horizon; the distinction is stated whenever it matters below.

**Definition 2.2 (Final).** A presentation $P$ is Final for $\mathfrak F$ when it has no admissible improving successor:

$$
\operatorname{Final}_{\mathfrak F}(P)
\iff
\nexists Q\in\mathcal Q\;
[P\leadsto Q\wedge Q\prec_{\mathcal R,\mathcal X}P].
\tag{2.8}
$$

Finality is independent of whether the realized proposer reaches the successor. It remains weaker than perfection. A Final theory may coexist with incomparable alternatives, or with alternatives that trade gains on one target for losses on another. Finality therefore excludes improving successors only within the domain of the declared comparison. An otherwise admissible successor outside that domain does not count against it. Section 6.1 treats this possible vacuity explicitly; it is precisely why Perfection also requires comparison completeness.

**Definition 2.3 (Perfect).** A presentation $P$ is Perfect for $\mathfrak F$ when the comparison is adequate and $P$ is nowhere locally worse than any admissible alternative:

$$
\operatorname{Perfect}_{\mathfrak F}(P)
\iff
\operatorname{Adeq}_{\mathfrak F}(P)
\ \wedge\ 
\forall Q\in\mathcal Q\;\forall x\in\mathcal X,
L_P^{\mathcal R}(x)\leq L_Q^{\mathcal R}(x).
\tag{2.9}
$$

Equivalently, $P\preceq_{\mathcal R,\mathcal X}Q$ for every $Q\in\mathcal Q$. Finality says that $P$ is undominated among its successors. Perfection says that $P$ is a least element of the declared comparison problem. It rules out not only a uniformly dominating successor but any local target on which an admissible alternative performs better.

**Proposition 2.4 (hierarchy).** Suppose the verifier is sound and the proposer emits only admissible successors. Then

$$
\operatorname{Perfect}_{\mathfrak F}(P)
\Longrightarrow
\operatorname{Final}_{\mathfrak F}(P)
\Longrightarrow
\operatorname{Good}_{\mathfrak F}(P).
\tag{2.10}
$$

**Proof.** If $P$ is Perfect, then $L_P(x)\leq L_Q(x)$ for every admissible $Q$ and every $x$, so no $Q$ can be a strict pointwise improvement over $P$; hence $P$ is Final. If $P$ is Final, soundness prevents the proposer and verifier from producing an accepted certificate for an improving successor that does not exist; hence $P$ is Good. $\square$

Neither converse holds. A proposer may never emit an available improvement, making $P$ Good but not Final. Two presentations with loss vectors $(0,1)$ and $(1,0)$ may both be Final under pointwise dominance, while neither is Perfect. Finally, a presentation may satisfy (2.9) while no effective procedure can certify the universal quantifiers involved.

## 2.4 When the agent may say Done

The status **Done as Perfect** records a certified Perfection claim. Let $V^\star$ be a declared meta-verifier for finality contracts. The agent may assign this status to $P$ when it possesses a finite certificate $\Pi$ such that

$$
V^\star(\mathfrak F,P,\Pi)=1
\quad\Longrightarrow\quad
\operatorname{Perfect}_{\mathfrak F}(P).
\tag{2.11}
$$

Within a budget $B$, the certificate must also be constructible and checkable within $B$. A certificate of Good or Final licenses only the corresponding weaker announcement. The phrase "this theory is done" is therefore incomplete unless the finality contract and the certified grade are recoverable from context.

The distinction between truth and licensed announcement is load-bearing. A theory may be Perfect but not effectively callable Done. Conversely, an agent may stop rationally under a cost or risk criterion without claiming any form of logical completion. Stopping is an action; Done is a certified statement about why stopping is warranted.

# 3. Discovering improvements

The hierarchy of §2 states what must be true and what must be certified, but it does not explain how an improving presentation enters the agent's reach. Existence, discovery, and recognition are different problems: an improvement may be finitely describable and immediately verifiable once supplied, yet remain absent from every completed stage of search. I therefore begin by asking whether the simplicity of an improvement places any effective bound on when an exhaustive proposer must discover it.

## 3.1 Targets, descriptions, and proposal time

Let $\mathcal Z$ be an infinite effectively enumerated domain of finite targets. Fix a universal prefix machine $M_{\mathrm{univ}}$ and write

$$
K_{\mathrm{univ}}(z)=\min\{|p|:M_{\mathrm{univ}}(p)=z\}.
\tag{3.1}
$$

An effective proposer $A$ emits a finite set of targets at each stage. It is **exhaustive** when every target is eventually emitted, and $\tau_A(z)$ denotes the first stage at which $z$ appears. Exhaustiveness is deliberately generous. The proposer is granted eventual success; the question is whether the simplicity of the target supplies a computable deadline for that success.

## 3.2 The Simplicity Fallacy

**Theorem 3.1 (Simplicity Fallacy).** For every exhaustive effective proposer $A$ over an infinite effective domain, there is no total computable $b$ satisfying

$$
\tau_A(z)\leq b(K_{\mathrm{univ}}(z))
\qquad\text{for every }z.
\tag{3.2}
$$

More strongly, for every computable $b$ there are targets $z_m$ with $K_{\mathrm{univ}}(z_m)\leq K_{\mathrm{univ}}(m)+O(1)$ whose first proposal occurs after stage $b(m)$.

**Proof.** Replace $b$ by its computable monotone envelope $\bar b$. For each $m$, simulate $A$ for $\bar b(m)$ stages. Only finitely many targets have appeared, so let $z_m$ be the least target not yet emitted. A fixed program computes $z_m$ from a self-delimiting description of $m$, giving

$$
K_{\mathrm{univ}}(z_m)\leq K_{\mathrm{univ}}(m)+c\leq m
$$

for all sufficiently large $m$. But $\tau_A(z_m)>\bar b(m)\geq \bar b(K_{\mathrm{univ}}(z_m))$. $\square$

The bound is uniform over arbitrary exhaustive effective proposers. Particular schedules may still relate description length to runtime: Levin search does so under a specified universal schedule, and distributions favouring short descriptions may remain useful [8]. The theorem rules out a computable discovery deadline determined solely by shortest description.

In the language of the hierarchy, simplicity cannot promote Good to Final. Before the relevant proposal arrives, the current theory may remain undefeated under every performed search even though a short improving successor exists. The difficulty lies in constructing the proposal, not in evaluating it once it arrives. Simply put, it can be very complex to construct a simple thing.

## 3.3 Certificates do not close their own search space

An arrived improvement certificate may be completely decisive about the move it certifies. Failure to receive one does not certify finality; it contributes only through the likelihood assigned to that search failure under the declared proposal model and budget. Let

$$
\operatorname{Defeat}(P,g,t)
\iff
\exists Q,\pi\;
[g(P,t)=(Q,\pi)\wedge V(P,Q,\pi)=1].
\tag{3.3}
$$

Each finite stage is decidable when $g$ and $V$ are effective. The universal claim

$$
\forall t\;\neg\operatorname{Defeat}(P,g,t)
\tag{3.4}
$$

is different. More search can provide a counterexample to (3.4); no finite improvement-free prefix exhausts its quantifier. This elementary change of quantifier produces the first imperfection result.

# 4. The computability boundary of completion

With the search process explicit, the completion grades become decision problems. Their complexity is governed by the domain that must be exhausted: proposal stages, admissible successors, or target points. This section locates those boundaries and shows that even a candidate class containing only two presentations can yield an undecidable completion claim when its target domain is unbounded.

## 4.1 Operational goodness

The complement of unbounded Good is computably enumerable: simulate the proposer and halt when the verifier accepts a strict-improvement certificate. Good is therefore co-c.e. A fixed finite-budget version is decidable by exhausting its bounded run; the theorem concerns reachability over an unbounded effective proposal horizon.

**Theorem 4.1 (Operational Imperfection).** Suppose there exist finitely described presentations $P_0,P_1$ and a finite certificate $\pi_1$ such that

$$
V(P_0,P_1,\pi_1)=1.
$$

Then

$$
\mathsf{GOOD}
=
\{\langle\mathfrak F,P\rangle:
\operatorname{Good}_{\mathfrak F}(P)\}
\tag{4.1}
$$

is $\Pi^0_1$-complete.

**Proof.** Membership follows from (3.4). For hardness, use the witnesses $P_0,P_1,\pi_1$ from the hypothesis. From a machine--input pair $(M,w)$, construct a proposer $g_{M,w}$ that simulates $M(w)$ and emits $(P_1,\pi_1)$ exactly when the simulation halts. Then

$$
\operatorname{Good}(P_0,g_{M,w})
\iff
M(w)\uparrow.
\tag{4.2}
$$

The construction is effective. $\square$

Every universal proposal system that executes arbitrary programs contains delayed branches of this form.

**Corollary 4.2 (no complete Good certificate).** No effective verifier is both sound for Good and complete on all Good instances. Such a verifier would computably enumerate a $\Pi^0_1$-complete set whose complement is already computably enumerable, and would therefore decide it. $\square$

## 4.2 Extensional finality

Operational goodness depends on the realized proposer. Finality quantifies over the declared successor class itself. If admissible successor encodings are effectively enumerable and the certificate system is complete for strict improvement,

$$
P\leadsto Q\ \wedge\ Q\prec_{\mathcal R,\mathcal X}P
\iff
\exists\pi\;V(P,Q,\pi)=1,
$$

then

$$
\operatorname{NonFinal}_{\mathfrak F}(P)
\iff
\exists Q,\pi\;
[P\leadsto Q\wedge V(P,Q,\pi)=1]
\tag{4.3}
$$

is c.e., and Final is co-c.e. If the enumeration contains the reduction used in Theorem 4.1, this certificate-complete Final problem is $\Pi^0_1$-complete. An exhaustive proposer collapses the difference between Good and certificate-complete Final in the limit, but not at any known finite time: the agent still cannot know when exhaustiveness has delivered its last relevant move.

The certificate-completeness assumption is substantive. Under the pointwise order (2.3), establishing that one successor dominates another already contains a universal quantifier. Extensional Finality then rises one level.

**Theorem 4.3 (Extensional Finality).** Over comparison-complete effective contracts with an effectively enumerable successor class and total computable pointwise losses, deciding Finality under strict pointwise dominance is $\Pi^0_2$-complete.

**Proof.** Nonfinality has the form

$$
\exists Q\;\exists y\;\forall x\;
\left[
L_Q(x)\leq L_P(x)
\ \wedge\ 
L_Q(y)<L_P(y)
\right],
\tag{4.4}
$$

with a decidable matrix, so Finality is in $\Pi^0_2$.

For hardness, reduce the totality problem $\mathsf{TOT}$. Given a machine $M_e$, let $P_e$ have constant loss $L_{P_e}(s)=1$. For every input $n$, include an admissible successor $Q_{e,n}$ with

$$
L_{Q_{e,n}}(s)
=
\begin{cases}
0,&M_e(n)\text{ has not halted within }s\text{ steps},\\
2,&M_e(n)\text{ has halted within }s\text{ steps}.
\end{cases}
\tag{4.5}
$$

Each loss is total and computable. The successor $Q_{e,n}$ strictly dominates $P_e$ exactly when $M_e(n)$ never halts. Hence

$$
\operatorname{Final}(P_e)
\iff
\forall n\;M_e(n)\downarrow,
\tag{4.6}
$$

which is the $\Pi^0_2$-complete totality problem. $\square$

The stronger grade can therefore have the simpler refutation structure. Finality permits trade-offs and asks whether some entire successor loss vector lies below the current one. Perfection is refuted by one local coordinate at which an alternative is better.

## 4.3 Finite-Schema Imperfection

Open-ended proposal is not required. Undecidability can enter through the target horizon even when the entire candidate menu is present from the beginning.

**Theorem 4.4 (Finite-Schema Imperfection).** There is a uniformly computable family $(\mathfrak F_{M,w})$ of finitely described finality contracts, each containing exactly two presentations with total, uniformly computable pointwise losses over an infinite effective target domain, such that

$$
\left\{
\langle M,w\rangle:
\operatorname{Perfect}_{\mathfrak F_{M,w}}(A)
\right\}
$$

is $\Pi^0_1$-complete.

**Proof.** Given a machine--input pair $(M,w)$, let $\mathfrak F_{M,w}$ have target domain $\mathbb N$ and candidate class $\{A,B_{M,w}\}$. Define their losses by

$$
L_A(n)=1,
\qquad
L_{B_{M,w}}(n)=
\begin{cases}
2,&M(w)\text{ has not halted within }n\text{ steps},\\
0,&M(w)\text{ has halted within }n\text{ steps}.
\end{cases}
\tag{4.7}
$$

Every pointwise evaluation is total: it simulates $M(w)$ for exactly $n$ steps. The comparison is operationally complete. Moreover,

$$
\operatorname{Perfect}_{\mathfrak F_{M,w}}(A)
\iff
\forall n\;L_A(n)\leq L_{B_{M,w}}(n)
\iff
M(w)\uparrow.
\tag{4.8}
$$

Thus the displayed family problem is $\Pi^0_1$-hard. Membership follows because failure of perfection is witnessed by a finite pair $(Q,n)$ with $L_Q(n)<L_A(n)$. $\square$

The reduction uses only two candidates, and every comparison at a fixed target is decidable. The $\Pi^0_1$ complexity arises from universal quantification over the unbounded target domain $\mathcal X$: non-perfection has a finite witness, whereas perfection requires the pointwise order to hold at every target.

## 4.4 The finite boundary

Finite, fully enumerated contracts admit exhaustive decision.

**Proposition 4.5 (finite perfection).** If $\mathcal Q$ and $\mathcal X$ are finite and completely enumerated, $\operatorname{Cmp}_{\mathcal R}$ is decidable and total on $\{P\}\times\mathcal Q\times\mathcal X$, and every pointwise loss comparison is decidable, then $\operatorname{Perfect}_{\mathfrak F}(P)$ is decidable by exhaustion. $\square$

Finiteness must occur in the right places:

| Candidate class | Target domain | Comparison | Perfection |
|---|---|---|---|
| finite | finite and fully enumerated | total decidable | decidable |
| finite | finite but partially observed | pointwise decidable | empirical best decidable; true best unidentified |
| finite, even two | infinite effective | total decidable pointwise | $\Pi^0_1$-complete |
| effectively bounded | finite | total decidable | decidable by bounded exhaustion |
| effectively enumerable, unbounded | finite | total decidable | generally co-c.e.; the candidate quantifier remains |
| effective | infinite effective | total decidable pointwise | generally $\Pi^0_1$-complete |
| any | any | operationally incomplete | only comparison-relative claims are licensed |

The last row represents operational incompleteness. Decidability of the universal order can be considered only after the relevant order has been operationally defined.

## 4.5 The $\mathrm{KT}$ realization

The resource-bounded specialization in [1] supplies a concrete instance of this boundary. For a presentation $e$ and finite serialization $x$, presentation-relative $\mathrm{KT}_e(x)$ has a computable literal ceiling. Threshold comparison can therefore be decided by finite bounded exhaustion. Yet the charged dominance claim

$$
\forall x\in\{0,1\}^*,
\qquad
L_{e_0}(x)\leq L_{e_1}(x)
\tag{4.9}
$$

is $\Pi^0_1$-complete over the declared effective presentation class [1, Thm. 8.2]. Equation (4.9) is precisely the two-presentation fragment of perfection. The literal branch makes every local comparison terminate, while uniform dominance over the infinite target domain remains $\Pi^0_1$-complete.

## 4.6 Indexed completion claims

A system may prove that its theory is Perfect within a finite declared class, that it reaches a computable lower bound, or that no successor with proof length at most $L$ improves the declared objective. It may stop because the expected value of further search lies below its cost. Each result licenses completion only within its declared candidate class, target domain, resource bound, or stopping rule. The unrestricted claim that no effective future enlargement can improve the theory remains stronger.

Completion is therefore indexed. Theorems 4.1--4.4 show that moving from a finite contract to an unbounded effective one changes the logical type of the claim.

# 5. Limit completion and its boundary

The boundary results determine which strategies remain available to the agent. I now turn from classifying completion claims to acting when those claims cannot be decided or certified: convergence to a defeasible verdict, acquisition of stronger computational or reference resources, bounded stopping, continued exploration, and refutation. I begin with the co-enumerable cases, where failure has a finite witness even though truth cannot be uniformly certified.

## 5.1 A one-retraction approximation

The co-enumerable completion claims admit a one-retraction approximation. For Good, define

$$
\gamma(P,g,t)=
\begin{cases}
1,&\text{no accepted improvement certificate appears by stage }t,\\
0,&\text{otherwise.}
\end{cases}
\tag{5.1}
$$

For comparison-complete contracts with total decidable pointwise loss, define the analogous approximation to Perfect by returning $1$ until a finite witness $(Q,x)$ with $L_Q(x)<L_P(x)$ is found, and $0$ thereafter.

**Theorem 5.1 (limit completion).** For the Perfect clause, assume that the candidate class $\mathcal Q$ is effectively enumerable. Then the characteristic functions of Good, Perfect, and certificate-complete Final admit computable approximations that begin at $1$, converge on every instance, and change at most once, from $1$ to $0$. These $\Pi^0_1$ completion sets are co-c.e., equivalently co-1-c.e. in the Ershov hierarchy [22,23].

**Proof.** A false universal completion claim has a finite counterexample. Effective dovetailing eventually finds it, after which the approximation remains $0$. A true claim has no counterexample, so the approximation remains $1$. $\square$

**Lemma 5.2 (optimality of one retraction).** No total computable zero-mind-change approximation decides any $\Pi^0_1$-complete completion set. Such an approximation would be a decider. Hence one retraction is sufficient and zero is not sufficient uniformly. $\square$

The policy *presume completion until refuted* minimizes mind changes for these contracts. While the approximation remains at $1$, its value is a defeasible working stance rather than a certificate.

## 5.2 The announcement asymmetry

On a negative instance, the arrival of a counterexample certifies both noncompletion and convergence of the approximation: the value can never return to $1$. On a true completion instance, no sound and complete effective procedure can announce convergence. Such an announcement would certify the corresponding $\Pi^0_1$ property and contradict Theorem 4.1 or 4.4.

This yields a strict separation:

1. the internal working guess may be “the claimed completion condition holds”;
2. its epistemic status may remain unresolved under the current theory, proof system, and computational horizon;
3. an accepted counterexample refutes the completion claim and closes that particular inquiry.

The unresolved status records the inability of the declared carrier and verifier to determine the universal claim. Stronger proof systems may certify particular true instances, but no fixed sound effective verifier certifies all of them.

## 5.3 Extensional Finality is not limit-computable

The one-retraction result does not apply to generic extensional Finality under pointwise dominance. By Theorem 4.3 that problem is $\Pi^0_2$-complete. A set admitting an ordinary convergent computable approximation lies in $\Delta^0_2$ by the limit lemma, whereas a $\Pi^0_2$-complete set does not. Thus generic Finality has no uniformly convergent computable approximation at the base level, let alone a one-retraction approximation.

Relative to $0'$, the problem becomes co-c.e. and again admits a one-retraction approximation. The hierarchy of grades and the hierarchy of epistemic resources therefore cross: Perfect is a stronger property than Final, but its failure is locally witnessed and its decision problem lies one jump lower in the present pointwise model.

## 5.4 The finite-witness requirement

The one-retraction result requires effective finite witnesses of failure. A missing comparison apparatus instead requires the construction of a common operational frame. If $P$ and $Q$ cannot be placed in such a frame, waiting longer need not produce either a comparison or a counterexample. In that case the agent must search not only for an improving presentation but also for the reference resources that make the comparison meaningful. This is the second boundary of perfection.

# 6. Commensurability and the right to compare

The limit strategies of §5 presuppose that candidate presentations can be compared. Comparability requires more than a shared byte encoding: it requires a neutral operational structure in which an improvement relation is defined. I therefore turn to commensurability at three levels: whether presentations admit an operationally adequate joint readout, whether their local statistics glue into a global description, and whether revision through the resulting structure is independent of order. The first is required for a presentation to be Perfect; the latter two determine how far the comparison can be treated as neutral.

## 6.1 Finality without comparison is vacuous

An order can compare only the objects on which it is defined. If the current reference structure cannot place $P$ and $Q$ in a common operational experiment, the failure of $Q\prec P$ does not favour $P$. It records an undefined comparison.

Let

$$
\operatorname{Dom}(\mathcal R)
\subseteq
\mathcal Q\times\mathcal Q\times\mathcal X
\tag{6.1}
$$

be the domain on which the declared comparison is operationally adequate. The comparison-completeness condition (2.6) requires

$$
\{P\}\times\mathcal Q\times\mathcal X
\subseteq
\operatorname{Dom}(\mathcal R).
\tag{6.2}
$$

Without (6.2), $P$ may still be Good or Final relative to the comparisons already available, but it is not Perfect under Definition 2.3.

Commensurability is the availability of enough shared operational structure to evaluate the distinctions declared by the finality contract. It may hold without word-for-word translation between the languages. Two presentations may remain linguistically incommensurable while their predictions are commensurable through a public packet space. Conversely, two theories may exchange bytes while lacking any adequate operation that preserves the distinctions on which their relative quality depends.

## 6.2 Representational commensurability

Presentations $P$ and $Q$ are **representationally commensurable for a task** when there is a common reference system in which their relevant outputs, probabilities, and comparison operations have operationally faithful images. In the classical case this may be a common measurable space with calibrated readouts. In a phase-sensitive model it may require a common Hilbert space or linking algebra together with admissible cross-sector observables.

Let $\mathcal A_P$ and $\mathcal A_Q$ be the accessible observable algebras of two presentation sectors. Reference maps

$$
J_P:\mathcal H_P\longrightarrow\mathcal H_R,
\qquad
J_Q:\mathcal H_Q\longrightarrow\mathcal H_R
\tag{6.3}
$$

allow an observable $X$ on $\mathcal H_R$ to induce the cross-sector component

$$
X_{PQ}=J_P^*XJ_Q.
\tag{6.4}
$$

The maps alone do not establish commensurability. The preparation, calibration, admissible transformation, measurement, and readout procedures must make the relevant $X_{PQ}$ operationally available. A merely formal embedding is not enough.

Representational commensurability is indexed by the task. A reference structure may preserve predictive probabilities while erasing verification cost, or preserve terminal outputs while failing to preserve the interventions used during revision. Such a structure supports only the claims whose required operations it preserves.

## 6.3 The sharp coincidence

The strongest equivalence appears for sharp observables.

**Theorem 6.1 (sharp commensurability).** Let $E^{(1)},\ldots,E^{(k)}$ be finite-outcome projection-valued measures on a Hilbert space. The following are equivalent:

1. the family admits a joint projection-valued measure whose marginals are the $E^{(i)}$;
2. every projection in every $E^{(i)}$ commutes with every projection in every $E^{(j)}$;
3. the von Neumann algebra generated by the projections is abelian;
4. the represented event algebras of the measurements are contained in the projection lattice of a common abelian von Neumann algebra on the given Hilbert space.

Condition 4 concerns the given represented projections. An abstract Boolean coproduct is not sufficient, since it need not preserve their operator relations or the comparison operations declared by the task.

**Proof.** A joint projection-valued measure has mutually commuting range projections, and its marginals therefore commute. Conversely, products of a finite commuting family of marginal projections define the atoms of a joint projection-valued measure. Pairwise commutation is equivalent to abelianness of the generated von Neumann algebra, whose projection lattice supplies the common Boolean event algebra. $\square$

For every state $\rho$, the joint measurement in Theorem 6.1 defines a global probability distribution over joint outcomes whose marginals recover all declared sharp contexts. The converse must be stated with care: the existence of a global distribution for one empirical state does not by itself imply operator commutation. The equivalence is structural because the parent sharp measurement is required.

Let the canonical nonselective Lüders revision associated with $E^{(i)}$ be

$$
\mathcal I_i(\rho)
=
\sum_a E^{(i)}_a\rho E^{(i)}_a.
\tag{6.5}
$$

**Corollary 6.2 (sharp dynamical commensurability).** Under the hypotheses of Theorem 6.1, the canonical Lüders revisions commute:

$$
\mathcal I_i\mathcal I_j
=
\mathcal I_j\mathcal I_i.
\tag{6.6}
$$

The same holds outcome by outcome for the corresponding selective operations. In the sharp canonical regime, joint representation supports commuting revision. Generalized measurements separate these properties.

## 6.4 Local descriptions and global models

Suppose a comparison experiment has a finite set $\mathsf{Obs}$ of measurement labels, a family of jointly available contexts $\mathcal C\subseteq 2^{\mathsf{Obs}}$, and a finite outcome set $O_m$ for each $m\in\mathsf{Obs}$. An empirical model is a compatible family

$$
p=
\left\{
p_C\in\Delta\left(\prod_{m\in C}O_m\right):
C\in\mathcal C
\right\}
\tag{6.7}
$$

whose marginals agree on overlapping contexts. A **global model** is a probability distribution on $\prod_{m\in\mathsf{Obs}}O_m$ whose marginal on every $C\in\mathcal C$ equals $p_C$. In the sheaf-theoretic language, it is a global section of the probabilistic model [24]. Its existence gives a neutral classical account of all declared local comparison statistics.

Failure of a global model is contextuality. The local descriptions may be individually coherent and mutually compatible on every shared boundary while still resisting a single global distribution. In the vocabulary of this paper, every declared local comparison may be meaningful even though no neutral classical presentation glues all of them together.

The obstruction can be graded. Let $\mathrm{NCF}(p)$ be the greatest $\lambda\in[0,1]$ for which

$$
p
=
\lambda p^{\mathrm{nc}}
+
(1-\lambda)p',
\tag{6.8}
$$

where $p^{\mathrm{nc}}$ is noncontextual and $p'$ is another empirical model. The **contextual fraction** is

$$
\mathrm{CF}(p)=1-\mathrm{NCF}(p).
\tag{6.9}
$$

The noncontextual fraction is the largest part of the observed comparison behaviour that admits a neutral classical explanation; the contextual fraction measures the residual obstruction [25,31,32]. It is a property of the empirical comparison model, not a replacement for the structural adequacy condition (6.2), and it says nothing by itself about the order of revision operations.

## 6.5 The unsharp gap

Generalized measurements separate representational from dynamical commensurability. The separation can be seen already for two binary qubit measurements.

Let $\mathbf n$ and $\mathbf m$ be unit Bloch vectors meeting at an angle of $60^\circ$, take $\eta=1/2$, and define

$$
E^{\mathbf n}_{\pm}
=
\frac12(I\pm\eta\,\mathbf n\cdot\boldsymbol\sigma),
\qquad
E^{\mathbf m}_{\pm}
=
\frac12(I\pm\eta\,\mathbf m\cdot\boldsymbol\sigma).
\tag{6.10}
$$

For two unbiased binary qubit observables, joint measurability is equivalent to the following inequality [26]:

$$
\eta\|\mathbf n+\mathbf m\|
+
\eta\|\mathbf n-\mathbf m\|
\leq 2.
\tag{6.11}
$$

Here the left-hand side is $(\sqrt3+1)/2<2$, so the pair admits a parent observable. The two effects do not commute because $\mathbf n\times\mathbf m\neq0$.

Consider their nonselective Lüders channels. On Bloch vectors, the channel associated with direction $\mathbf n$ acts as

$$
T_{\mathbf n}
=
aI+(1-a)\mathbf n\mathbf n^{\mathsf T},
\qquad
a=\sqrt{1-\eta^2},
\tag{6.12}
$$

and similarly for $\mathbf m$. Their commutator is

$$
[T_{\mathbf n},T_{\mathbf m}]
=
(1-a)^2(\mathbf n\cdot\mathbf m)
(\mathbf n\mathbf m^{\mathsf T}-\mathbf m\mathbf n^{\mathsf T}),
\tag{6.13}
$$

which is nonzero because $\mathbf n\cdot\mathbf m=1/2$ and the vectors are not parallel.

**Proposition 6.3 (static gluing without dynamic gluing).** The measurements in (6.10) are jointly measurable, but their canonical Lüders revision channels are order-dependent.

The pair is therefore representationally commensurable: a parent observable supplies a common statistical language. It is dynamically incommensurable: revision through one context and then the other need not agree with the reverse order. The example establishes a second boundary: representational commensurability may hold while dynamical commensurability fails [27].

## 6.6 Commuting-square dynamics

The operator-algebraic formulation extends beyond Lüders instruments. Let $\mathcal N_1,\mathcal N_2\subseteq\mathcal M$ be accessible subalgebras and let

$$
E_i:\mathcal M\longrightarrow\mathcal N_i
\tag{6.14}
$$

be state-preserving conditional expectations. A sufficient composability condition is the commuting square

$$
E_1E_2
=
E_2E_1
=
E_{\mathcal N_1\cap\mathcal N_2}.
\tag{6.15}
$$

Under (6.15), revision through the two declared subtheories is independent of order at the common retained level. Without it, a common ambient algebra may exist while the two retractions implement different learning paths. Commuting squares therefore test a stronger property than joint representability [28--30].

This distinction refines conservativity. An old theory may be recoverable from a richer one through a state-preserving conditional expectation, yet two such recoveries may fail to compose neutrally. To call perfection path-independent, the finality contract must declare and verify the required dynamical compatibility. Otherwise perfection is indexed by the revision protocol.

## 6.7 Reference enrichment and phase-sensitive comparison

For this subsection, take each charged loss to be a finite vector ordered componentwise. Write $\mathcal R\sqsubseteq\mathcal R'$ when $\mathcal R'$ is a distinction-adding enrichment of $\mathcal R$ on fixed candidate, target, and comparison domains: there is a coordinate projection $\pi$ such that

$$
\pi\!\left(L_Q^{\mathcal R'}(x)\right)
=
L_Q^{\mathcal R}(x)
$$

for every $Q\in\mathcal Q$ and $x\in\mathcal X$. Thus every old loss component remains available with its old value, while new components may be added. The dominance verdict is nevertheless recomputed from the complete enriched vector.

**Proposition 6.4 (reference non-monotonicity).** Under distinction-adding enrichment, NonFinality is non-monotone in both directions:

$$
\operatorname{NonFinal}_{\mathcal R}(P)
\not\Longrightarrow
\operatorname{NonFinal}_{\mathcal R'}(P),
\qquad
\operatorname{NonFinal}_{\mathcal R'}(P)
\not\Longrightarrow
\operatorname{NonFinal}_{\mathcal R}(P).
\tag{6.16}
$$

If both reference structures are comparison-complete for the same candidate and target classes, then

$$
\operatorname{Perfect}_{\mathcal R'}(P)
\Longrightarrow
\operatorname{Perfect}_{\mathcal R}(P),
\tag{6.17}
$$

while the converse may fail.

**Proof.** Take one target and one admissible successor $P\leadsto Q$. For the first failure, let the coarse losses be

$$
L_P^{\mathcal R}=1,
\qquad
L_Q^{\mathcal R}=0.
$$

Then $Q$ strictly improves $P$. Under the enriched losses

$$
L_P^{\mathcal R'}=(1,0),
\qquad
L_Q^{\mathcal R'}=(0,5),
$$

the two presentations are Pareto-incomparable, so the old improvement witness disappears.

For the reverse failure, let the coarse losses tie:

$$
L_P^{\mathcal R}
=
L_Q^{\mathcal R}
=
1.
$$

Under the enrichment

$$
L_P^{\mathcal R'}=(1,1),
\qquad
L_Q^{\mathcal R'}=(1,0),
$$

$Q$ becomes a strict improvement. Thus either verdict may change under enrichment.

For (6.17), perfection under $\mathcal R'$ gives the componentwise inequality $L_P^{\mathcal R'}(x)\leq L_Q^{\mathcal R'}(x)$ for every $Q$ and $x$. Projecting onto the retained coordinates gives $L_P^{\mathcal R}(x)\leq L_Q^{\mathcal R}(x)$. The second counterexample also shows that the converse can fail. $\square$

Reference enrichment is a verdict-changing epistemic event: it preserves the old data while changing which combinations of distinctions count as an improvement.

Phase-sensitive operations are one source of such enrichment. Block-diagonal comparisons identify states that differ only in cross-sector terms. An admitted reference observable with a nonzero off-diagonal component may separate them [1, §6]. A presentation that appears Perfect under every classical packet statistic may cease to be Perfect once the required phase reference, calibration, and cross-sector measurement become available.

Phase-sensitive comparison requires specified and charged reference maps, intertwiners, state preparation, calibration, and verification procedures. The richer contract is a different contract.

## 6.8 Consequences for perfection

Commensurability determines which completion claims are even available:

1. **No operationally adequate common comparison.** Only sector-relative or context-relative Good and Final claims can be made. Global perfection is not established.
2. **Locally compatible comparison statistics but no global noncontextual model.** Local comparisons exist, but no neutral classical account glues all contexts. Any global claim must retain the contextual reference structure.
3. **Representational but not dynamical commensurability.** Alternatives can be compared, but the result of revision may depend on order. Perfection must be indexed by the declared update protocol or path.
4. **Representational and dynamical commensurability.** A path-independent perfection claim is well typed. Its certification may nevertheless remain computationally impossible.

The last qualification is essential. Commensurability buys the right to formulate a global comparison; it does not discharge the comparison's universal quantifiers.

# 7. Perfect resources

Sections 4--6 identify two independent obstructions to calling a theory Done: the required universal claim may exceed the agent's computational power, and the comparisons over which it quantifies may lack an adequate reference structure. I now ask what resources can remove each obstruction. The two obstructions require distinct resources. Computational resources decide claims within an effective comparison domain; reference resources create or refine the comparisons on which those claims depend. They may be combined, but neither can substitute for the other.

## 7.1 Turing jumps as completion resources

The preceding completion problems share an exact computational resource.

**Theorem 7.1 (Perfect Resource).** For the effective contract classes used in Section 4,

$$
\mathsf{GOOD}\equiv_T0'.
\tag{7.1}
$$

When admissible improving successors are effectively enumerable with complete finite decidable witnesses,

$$
\mathsf{FINAL}\equiv_T0'.
\tag{7.2}
$$

When the contract is comparison-complete, the candidate and target classes are effectively enumerable, pointwise losses are total computable, and the class contains the construction of Theorem 4.4,

$$
\mathsf{PERFECT}\equiv_T0'.
\tag{7.3}
$$

For unrestricted extensional Finality under total computable pointwise loss,

$$
\mathsf{FINAL}_{\mathrm{pt}}\equiv_T0''.
\tag{7.4}
$$

**Proof.** The reductions in Theorems 4.1 and 4.4 give $0'$-hardness for Good and Perfect; the same delayed-witness construction gives it for certificate-complete Final. Conversely, construct a program that searches respectively for an accepted reachable improvement, a certified admissible improving successor, or a finite pair $(Q,x)$ witnessing $L_Q(x)<L_P(x)$. In each case the search program halts exactly on the complement of the completion claim. A halting oracle decides whether it halts. Equation (7.4) follows from the $\Pi^0_2$ upper bound and $\mathsf{TOT}$ reduction in Theorem 4.3. $\square$

The theorem identifies the resource required to decide whether a theory satisfies the declared condition. Each stated jump is sufficient and, up to Turing degree, necessary. Extensional Finality requires the second jump because it quantifies over the absence of uniformly dominating successor vectors; Perfection has finite local counterexamples despite being the stronger property.

**Corollary 7.2 (perfection jump).** For any oracle $R$, if proposals, certificates, comparisons, and losses are $R$-computable, Good, Perfect, and certificate-complete Final have degree $R'$ whenever the relativized contract class contains the reductions above. Extensional pointwise Finality has degree $R''$.

Every oracle can close a weaker effective horizon while opening new completion problems above it. No resource decides every perfection and finality problem generated by the comparison and proposal processes computable from that same resource.

## 7.2 Computational and reference resources

Theorem 7.1 presupposes that the comparison problem has already been typed. A halting oracle decides the absence of counterexamples in an effective comparison domain; it does not supply missing reference maps, calibrations, or joint observables. Conversely, a reference apparatus may make every pair operationally comparable while leaving the unbounded perfection claim $\Pi^0_1$-complete.

The two axes give four regimes:

| Comparison structure | Completion claim | Strongest warranted status |
|---|---|---|
| operationally complete | decidable or finitely certified | Done as Perfect |
| operationally complete | not effectively decidable | completion may be true; limit methods where available, exploration, and refutation remain |
| operationally incomplete | locally decidable where defined | context- or sector-relative Good and Final |
| operationally incomplete | unbounded and undecidable | simultaneous search for theories, counterexamples, and reference resources |

The computational and reference axes are independent, so completion requires both sufficient decision power and an adequate comparison structure.

## 7.3 Quantum decision access and imperfection

Call a quantum decision procedure operationally effective when every input determines, in computable time, a finite experiment with uniformly computable matrix entries, a computable termination bound, and a fixed decision gap. Standard finite-gate quantum algorithms satisfy these conditions [9].

**Corollary 7.3.** No operationally effective uniform quantum procedure decides any of the undecidable completion problems in Theorem 7.1 with bounded error.

**Proof.** With computable entries and a fixed decision gap, the acceptance probability of each finite experiment can be approximated classically far enough to determine on which side of the gap it lies. Efficiency is irrelevant; exponential simulation suffices. The resulting classical decider would contradict Theorem 7.1. $\square$

Quantum or phase-sensitive resources may change accessibility. They may alter proposal probabilities, interfere construction paths, or supply comparisons unavailable to a block-diagonal classical apparatus. Under effective operational assumptions they do not decide the halting problem.

Infinite-dimensional and operator-algebraic models require an effective presentation and a uniform approximation modulus before the same conclusion can be drawn. Without them, an exact real parameter or limiting operation may import an oracle through the model's specification [10,11,13]. Encoding an undecidable answer into a physical family and operationally extracting it remain different achievements.

## 7.4 Continuum parameters as computational carriers

Continuum parameters can carry computational degree without providing an interface to it. Let $h_n$ be the halting bit of the $n$th machine on blank input and set

$$
\alpha_H
=
\sum_{n\geq0}h_n4^{-(n+1)}.
\tag{7.5}
$$

The separated base-$4$ digits give

$$
\alpha_H\equiv_T0'
\tag{7.6}
$$

under an addressable Cauchy-name interface that returns certified approximations at requested precision. A quantum phase may carry the parameter in

$$
|\psi_H\rangle
=
\frac{|0\rangle+e^{2\pi i\alpha_H}|1\rangle}{\sqrt2},
\tag{7.7}
$$

and a classical coin may carry the same degree in its bias. Neither mathematical embedding provides the interface assumed in (7.6).

One specimen does not expose arbitrarily many digits [12]. Repeatable exact preparation and ordinary sampling can recover any fixed separated digit with arbitrarily high confidence at rapidly growing cost, but never with zero-error certainty from a finite sample. A genuine oracle contract requires the noncomputable preparation, the addressable operations, and the certified-precision readout together. The extra computability belongs to that apparatus, not to superposition or continuity.

This observation links the two resource axes without conflating them. Phase-sensitive reference structure may provide a representational location for distinctions absent from a classical mixture. If a noncomputable parameter is installed there with an exact readout contract, the apparatus also supplies computational power. The phase degree of freedom alone supplies neither.

## 7.5 Omnipotence and resource self-escalation

The strongest case admitted by the framework grants both resource axes at once. Let $R$ be an installed oracle, possibly of super-Turing degree, and let $\mu_{\mathrm{full}}$ code the certified input-output interface for every preparation, measurement, calibration, and readout operation admitted by the declared physical model and reference structure. Put

$$
S
=
R\oplus\mu_{\mathrm{full}}.
\tag{7.8}
$$

This limiting contract represents the strongest apparatus admitted by the framework, independently of its physical realizability. An $S$-effective contract is a finality contract whose proposal, verification, comparison, and loss procedures may query $S$. The underlying state space may be continuous, provided every operation available to the agent is finitely addressable.

**Theorem 7.4 (Omnipotence Theorem).** Suppose $\mathcal R^{\mathrm{full}}$ is comparison-complete for the declared candidate and target classes, and suppose the relevant $S$-effective contract classes satisfy the hypotheses of Theorem 7.1 and contain the $S$-relativized constructions used in Theorems 4.1, 4.3, and 4.4. Then

$$
\begin{aligned}
\mathsf{GOOD}^{S}
&\equiv_T
\mathsf{FINAL}_{\mathrm{cert}}^{S}
\equiv_T
\mathsf{PERFECT}^{S}
\equiv_T
S',\\
\mathsf{FINAL}_{\mathrm{pt}}^{S}
&\equiv_T
S''.
\end{aligned}
\tag{7.9}
$$

Here $\mathsf{FINAL}_{\mathrm{cert}}^{S}$ denotes the certificate-complete Final problem of §4.2. Consequently, no $S$-effective procedure decides every completion problem that an $S$-enabled agent can construct.

**Proof.** For Good, given an $S$-oracle program $\Phi_e^S(w)$, construct a proposer that emits a fixed accepted improvement certificate exactly when $\Phi_e^S(w)$ halts. The current presentation is Good exactly when the computation diverges. This gives $S'$-hardness.

For Perfect, use the two-presentation construction on target domain $\mathbb N$:

$$
L_A(n)=1,
\qquad
L_{B_{e,w}^S}(n)
=
\begin{cases}
2,&\Phi_e^S(w)\text{ has not halted within }n\text{ steps},\\
0,&\Phi_e^S(w)\text{ has halted within }n\text{ steps}.
\end{cases}
$$

Each pointwise loss is total and $S$-computable, and comparison completeness supplies every required local comparison. Hence

$$
\operatorname{Perfect}(A)
\iff
\Phi_e^S(w)\uparrow.
$$

The upper bounds follow by searching with oracle $S$ for finite counterexamples. Certificate-complete Finality uses the same finite-witness argument. Relativizing the totality construction of Theorem 4.3 gives $S''$-completeness for extensional pointwise Finality. Finally, the relativized jump theorem gives $S<_T S'<_T S''$. $\square$

The theorem is uniform in the granted resource. An oracle strong enough to decide the old completion problem becomes part of the effective base from which new presentations and searches can be constructed. The resulting completion problem therefore lies one jump above the grant.

$$
\boxed{
\begin{gathered}
\text{Granting }S\text{ closes an old horizon}\\
\text{by making }S'\text{ the next completion boundary.}
\end{gathered}}
\tag{7.10}
$$

> // **Author's comment.** This is the paper's version of *Omnipotence*: granting god mode solves the old game, but the grant itself becomes part of the agent's constructive language. It enlarges what the agent can propose, compare, and ask to certify, and thereby creates the next completion problem. In learning, god mode is therefore omnipotence only relative to the position from which it was granted, not relative to the position the grant creates.

Full measurement access is likewise full only relative to the declared physical model and comparison task. Enlarging the admissible operations, targets, or presentations produces a new contract. Thus even the strongest combined resource not excluded by the framework may license Done for a fixed theory and domain, but it cannot license an unindexed claim that no computational or representational improvement remains.

## 7.6 The availability of Perfection

The Omnipotence Theorem shows that no fixed resource base closes every completion problem constructible from that base. A separate question arises even when the resource base and contract schema remain fixed: does the candidate class contain any Perfect presentation at all? Testing a supplied candidate is co-c.e. under the hypotheses of Theorem 4.4. Quantifying over the candidates adds another alternation.

**Theorem 7.5 (existence of Perfection).** Over uniformly effectively presented, comparison-complete contracts with candidate class $\mathcal Q=\{P_n:n\in\mathbb N\}$, target domain $\mathcal X=\mathbb N$, and total uniformly computable scalar losses, the problem

$$
\mathsf{HASPERFECT}
=
\left\{
\langle\mathfrak F\rangle:
\exists n\;\operatorname{Perfect}_{\mathfrak F}(P_n)
\right\}
\tag{7.11}
$$

is $\Sigma^0_2$-complete.

**Proof.** Comparison completeness makes adequacy automatic. Membership follows from

$$
\exists n\;\forall m,x\;
L_{P_n}^{\mathcal R}(x)
\leq
L_{P_m}^{\mathcal R}(x),
\tag{7.12}
$$

whose matrix is decidable.

For hardness, reduce the $\Sigma^0_2$-complete set

$$
\mathsf{FIN}
=
\{e:W_e\text{ is finite}\}.
$$

Given $e$, construct a contract $\mathfrak F_e$ with the candidate and target classes above. Let $W_{e,s}$ be the finite approximation to $W_e$ after stage $s$, and define

$$
L_{P_n}^{(e)}(x)
=
\begin{cases}
1,
&\exists s\;[n<s\leq x\ \wedge\ W_{e,s}\neq W_{e,s-1}],\\
0,&\text{otherwise.}
\end{cases}
\tag{7.13}
$$

Every pointwise loss is total and uniformly computable by simulating the enumeration through stage $x$.

If $W_e$ is finite, choose $N$ at or after its final enumeration stage. Then $L_{P_N}^{(e)}(x)=0$ for every $x$, so $P_N$ is Perfect. If $W_e$ is infinite, fix any $n$ and choose a later stage $s>n$ at which the enumeration changes. At target $x=s$,

$$
L_{P_n}^{(e)}(s)=1,
\qquad
L_{P_s}^{(e)}(s)=0,
$$

so $P_n$ is not Perfect. Hence

$$
\exists P\in\mathcal Q\;
\operatorname{Perfect}_{\mathfrak F_e}(P)
\iff
W_e\text{ is finite}.
\tag{7.14}
$$

The map $e\mapsto\mathfrak F_e$ is computable. $\square$

**Corollary 7.6 (no uniform limit diagnosis).** No computable binary approximation converges on every effective contract to the correct answer about whether that contract contains a Perfect presentation.

**Proof.** Any predicate admitting such an approximation is $\Delta^0_2$, while $\mathsf{HASPERFECT}$ is $\Sigma^0_2$-complete. $\square$

The corollary marks the limit of the one-retraction discipline. For a supplied presentation, Perfection is co-c.e. and may be presumed until a finite counterexample appears. For the existential question, an agent may successively find and lose plausible candidates without converging to whether the class contains a Perfect member.

**Remark 7.7 (natural nonexistence through speedup).** The reduction above is exact but deliberately constructed. Blum speedup supplies natural fixed-contract instances with no Perfect element [6]. For a suitable Blum complexity measure $\Phi$, there are total computable functions $f$ such that every program $i$ computing $f$ has another program $j$ computing $f$ with a prescribed computable speedup on almost all inputs. If the candidates are programs computing $f$, targets are inputs, and $L_{P_i}(x)=\Phi_i(x)$, then no $P_i$ is Perfect: some $P_j$ is locally better at a target. This conclusion concerns Perfection. Almost-everywhere speedup need not give pointwise dominance on the finitely many exceptional inputs, so it does not by itself show that $P_i$ is non-Final under (2.8). If the contract charges additional components such as description length, the verdict must be recomputed under its declared order.

# 8. Acting without certified completion

The preceding sections characterize the conditions required for completion and the resource-relative boundaries of its certification. The practical question is how an agent should act when the claim is undecidable, the comparison is not yet well typed, revision is path-dependent, or further search is too costly. Each obstruction requires a different response.

## 8.1 Diagnose the missing warrant

The hierarchy orders completion claims:

$$
\mathrm{Perfect}
\Longrightarrow
\mathrm{Final}
\Longrightarrow
\mathrm{Good}.
\tag{8.1}
$$

These implications remain valid under the stated contract. What varies is the warrant available for asserting each grade.

| Claim sought | What must be established |
|---|---|
| **Good** | that no accepted improvement is reachable through the declared proposal and verification process |
| **Final** | that no admissible successor is a strict improvement |
| **Perfect** | that the comparison is complete and the current presentation is nowhere locally worse over the entire target domain |
| **Done** | that the appropriate meta-verifier accepts a sound completion certificate |

The missing warrant may lie in the performed proposal and verification process, the quantified class of admissible successors, the coverage of the comparison structure, the existence of a least element, the target horizon, or the availability of a completion certificate. The first task is to identify which of these prevents the desired grade from being asserted.

## 8.2 Exploration under computational imperfection

When the comparison structure is adequate but the universal claim is not decidable, the principal action is counterexample search. The agent may allocate resources among:

- proposing new presentations;
- expanding the target sequence on which pointwise losses are tested;
- searching for short improvement witnesses;
- strengthening the proof system or verification budget;
- testing candidate lower bounds that could yield a positive perfection certificate.

For Good, Perfect, and certificate-complete Final, the co-c.e. structure privileges refutation. A finite witness establishes failure under the declared contract; elapsed search time supplies no completion certificate. Generic extensional Finality is different: refuting it requires establishing that an entire successor loss vector dominates the current one, which may itself require a universal certificate.

For the co-c.e. grades, the one-retraction approximation of Section 5 supplies a disciplined default: act provisionally as if the present theory satisfied the grade and retract on an accepted counterexample. The unretracted state remains a working presumption. This policy minimizes uniform mind changes for the logical objective considered here, while other economic objectives may favour different policies.

Strengthening the computational resource base is another possible response. A stronger resource may decide completion claims formulated under the previous contract. Once that resource becomes available to proposal, verification, and construction, the resulting claims are indexed by the enriched base, and the next completion problem moves to the corresponding higher degree. Resource acquisition may therefore close a declared inquiry while generating a stronger completion problem.

## 8.3 Search for comparison resources

When comparison is incomplete, the agent must search for the resources that make comparison possible. It may seek:

- a shared readout or calibration;
- a translation preserving the declared task distinctions;
- a parent observable or common refinement;
- an intertwiner or phase reference exposing cross-sector structure;
- an intervention that tests whether local descriptions can be glued;
- a restricted common subdomain on which a weaker finality claim is well typed.

This is representational exploration: the agent seeks an apparatus through which the relative quality of theories becomes addressable. Its construction and verification costs belong in the finality contract.

Acquiring such an apparatus changes the comparison contract and may change its verdicts. Under distinction-adding enrichment, a former improvement may become incomparable, while a former tie may become a strict improvement. Finality and Perfection must therefore be recomputed under the enriched comparison contract; neither verdict transfers automatically from the coarser presentation.

If no neutral global structure exists, the agent should retain the local contexts rather than force them into an artificial total order. A contextual model can support coherent local decisions without licensing a context-free declaration of perfection.

## 8.4 Revision under dynamical incommensurability

If alternatives admit a common statistical description but their revision operations do not commute, the agent must record the learning path. The relevant state is the pair $(P,h)$, where $h$ contains the ordered interventions and commitments that produced the current presentation.

Accordingly, $h$ belongs to the candidate state and to the comparison contract. Suppressing it changes the object whose Finality or Perfection is being evaluated.

Three responses are then available:

1. declare a revision protocol and evaluate perfection relative to it;
2. retain several path-indexed successor states rather than collapsing them into one posterior;
3. acquire a stronger dynamical reference structure, such as a verified commuting square, if the task requires order independence.

Calling a theory Perfect without stating the path in a dynamically incommensurable regime discards information on which later comparisons may depend.

## 8.5 Rational stopping under a declared model

A bounded agent may rationally stop a logically open search. Given a proposal law, a posterior over improvement sizes and discovery times, and the cost of another search allocation, it may stop when the expected value of continued exploration falls below its cost.

Such a rule certifies that continued search is not worthwhile under the current distribution and budget. Finality and Perfection remain separate claims. New evidence, a new proposal law, or a new reference resource may rationally restart the search without contradicting the earlier decision.

The strongest useful reports are consequently typed:

| Report | What it licenses |
|---|---|
| **Good under $(g,V,B)$** | no accepted improvement is reachable through the declared realization |
| **Final in $(\mathcal Q,\leadsto,\mathcal X,\mathcal R,\preceq)$** | no admissible successor is a strict improvement under the declared comparison contract |
| **Perfect on $(\mathcal Q,\mathcal X,\mathcal R,\preceq)$** | all relevant comparisons are adequate and $P$ is nowhere locally worse |
| **Done as Perfect under $S$, certificate $\Pi$** | the $S$-enabled meta-verifier accepts a sound perfection certificate |
| **Resource base extended to $S$** | earlier questions may become decidable, but completion claims must be re-indexed by $S$ |
| **Reference structure enriched to $\mathcal R'$** | comparisons have changed and the earlier Final or Perfect verdict must be recomputed |
| **Search paused under policy $\delta$** | further search has insufficient expected value under the declared decision model |

## 8.6 Reflective learning systems

For a reflective learning system, every installed resource becomes part of the next constructive language. Source-code access and universal search enlarge the proposal horizon; proof assistants enlarge the set of checkable certificates; standard effective quantum computation may alter accessibility and reference structure without deciding an undecidable completion problem. Even hypothetical oracle and full-measurement access closes only a contract formulated below the granted resource: once that access can be used in construction, completion relativizes to the enriched base.

A well-designed system should expose the contract behind its claims. It may report that no better candidate exists in an enumerated class, that no proof below a declared length defeats the current theory, that the current presentation attains a certified lower bound, or that search has been paused by an expected-value rule. Each report should retain the candidate class, target domain, resource base, and stopping rule under which it was obtained.

A controlled ascent architecture uses proof-carrying local improvements, explicit comparison resources, typed stopping claims, and separate strategies for computational, representational, and dynamical obstruction. Every resource grant re-indexes the completion problem, and every distinction-adding enrichment requires its verdicts to be recomputed. Exploration searches for new candidates and comparison apparatus; refutation removes false completion claims; certification identifies the contracts under which search may close.

# 9. Relations and scope

The results intersect computability theory, learning in the limit, operational theories of measurement, and philosophical accounts of commensurability. This section states those relations and marks the boundary between the formal claims proved here and their broader interpretations.

## 9.1 Computability and learning in the limit

Turing supplies the base obstruction and the oracle hierarchy [2,3]; Post organizes the degrees [14]. The Simplicity Fallacy sits beside Busy Beaver [4] and Blum speedup [6], but concerns first discovery under an arbitrary exhaustive proposer. Algorithmic information theory gives machine-relative description and invariance [7], while Levin couples length and runtime under a universal schedule [8]. Theorem 3.1 adds that shortest description alone supplies no computable discovery deadline for an arbitrary exhaustive proposer.

Putnam's trial-and-error predicates, the limit lemma, and the Ershov hierarchy locate Theorem 5.1 [15,16,22,23]. Gold studies identification in the limit [5], and Kelly develops the corresponding logic of reliable inquiry [17]. Good, Perfect, and certificate-complete Final are co-c.e., so one retraction suffices and zero does not suffice uniformly. Generic extensional Finality occupies the next arithmetical level.

The finite-schema theorem is adjacent to meta-complexity. MCSP and MKtP ask whether a supplied finite object has a short bounded description [18--21]. The $\mathrm{KT}$ presentation-dominance result of [1] moves one quantifier upward: every supplied target remains decidable, while uniform pointwise dominance throughout the unbounded serialization domain is not.

## 9.2 Commensurability

Kuhn made incommensurability central to the study of scientific change [33]. The present framework treats translatability and isolation as endpoints rather than an exhaustive choice. It asks which operational comparisons are preserved, through which reference resources, and at what cost. Packet-level evidential commensurability may coexist with linguistic incommensurability; local operational comparisons may coexist with the absence of a neutral global language.

The sharp boundary draws on the standard equivalence between joint sharp measurement and commutation [27]. The unsharp gap belongs to the theory of jointly measurable generalized observables and nondisturbing measurements [26,27]. The global/local distinction uses the sheaf-theoretic account of contextuality [24], and the contextual fraction supplies its empirical grading [25]. Commuting squares of conditional expectations provide the stronger dynamical composability condition [28--30]. These tools describe operational comparison structures independently of whether their physical implementation is quantum.

## 9.3 Resource-relative omnipotence

Theorem 7.4 also isolates the formal structure behind familiar paradoxes of omnipotence. Let $S$ denote the resources installed in an agent's constructive and decision procedures. An appropriately strong $S$ may decide every completion problem in a previously fixed contract class. Once $S$ is admitted to proposal, verification, comparison, and construction, however, the agent can formulate $S$-effective completion problems whose uniform decision problem has degree $S'$. Since

$$
S <_T S',
\tag{9.1}
$$

the same fixed resource cannot decide every completion problem generated from the language that the grant itself creates.

This gives two consistent readings of omnipotence. If the admissible task domain is fixed, a resource may be complete relative to that domain; demanding that it solve a newly admitted task changes the contract. If the task domain must remain closed under every construction enabled by the resource, no fixed effective resource is complete for the resulting hierarchy. The familiar paradox arises by holding the attribution of power fixed while allowing the quantified class of challenges to expand.

The theorem applies to finitely addressable agents, operationally specified powers, and task classes that may expand through the exercise of those powers. It separates completeness relative to a fixed domain from closure under self-generated challenges.

## 9.4 Scope conditions

The results depend on declared contracts. In particular:

1. Good is relative to a proposer, verifier, and budget.
2. Final is relative to an admissible successor class and improvement relation.
3. Perfect is relative to a candidate class, target domain, reference structure, and pointwise objective.
4. A least element need not exist. Several Final theories may exist even when no theory is Perfect.
5. The $\Pi^0_1$ classifications require effective enumeration and finite recognizable counterexamples. Generic extensional Finality under pointwise dominance is $\Pi^0_2$-complete; other comparison predicates may have still greater logical complexity.
6. The one-retraction policy applies to those co-c.e. contracts; it does not manufacture missing commensurability.
7. A global distribution for one empirical state does not imply structural commutation of the underlying observables.
8. Joint measurability of unsharp observables does not imply commuting or order-independent instruments.
9. Contextual fraction grades an empirical obstruction; it is not by itself a cost of constructing the reference apparatus.
10. A noncomputable parameter is an installed computational resource only when the preparation and readout contract makes its information operationally available.
11. Full measurement access is full only relative to the declared physical model, operational interface, and target class.
12. A resource that decides an earlier completion problem need not decide the completion problems constructible from that resource; those claims must be relativized to the enriched base.
13. Resource-relative incompleteness does not establish any claim about metaphysically unrestricted agency.
14. Expected-value stopping is a rational action under a model, not a certificate of perfection.

# 10. Conclusion

Stopping inquiry and certifying **Done** are distinct. A theory may be **Good** because no accepted improvement is reachable through the declared realization, **Final** because no admissible improving successor exists, or **Perfect** because every admissible alternative is comparable and none is locally better anywhere on the declared target domain. Under sound procedures,

$$
\mathrm{Perfect}
\Longrightarrow
\mathrm{Final}
\Longrightarrow
\mathrm{Good},
\tag{10.1}
$$

and neither converse holds. A **Done** announcement records that the required grade has been certified.

Good, certificate-complete Finality, and pointwise Perfection are $\Pi^0_1$-complete and require the first Turing jump. Generic extensional Finality is $\Pi^0_2$-complete and requires the second. Quantifying over candidates raises a different question: whether the contract contains any Perfect presentation is $\Sigma^0_2$-complete and is not computably identifiable in the limit. Thus the one-retraction policy for a supplied candidate does not decide whether Perfection is available somewhere in the class. In the co-enumerable cases, an effective learner can achieve the optimal limit behaviour: presume completion, retract once when a finite counterexample arrives, and never announce convergence without a certificate.

Before any such universal claim can be evaluated, however, the alternatives must be comparable. In the sharp canonical regime, joint measurability, commuting projections, a common Boolean refinement, and order-independent revision align. Outside that regime they separate. A neutral statistical language may exist while revision remains path-dependent; locally compatible comparisons may have no global noncontextual description; and a new reference resource may change, rather than merely reveal, the existing Final or Perfect verdict. Perfection is therefore conditional on the right to compare as well as the power to decide.

The **Omnipotence Theorem** combines both forms of power. Let $S$ contain an arbitrarily strong computational oracle and the certified full-measurement interface admitted by the declared model. For the relativized contract classes,

$$
\mathsf{GOOD}^{S}
\equiv_T
\mathsf{FINAL}_{\mathrm{cert}}^{S}
\equiv_T
\mathsf{PERFECT}^{S}
\equiv_T
S',
\qquad
\mathsf{FINAL}_{\mathrm{pt}}^{S}
\equiv_T
S''.
\tag{10.2}
$$

The grant may solve every completion problem in the earlier contract. Once a reflective agent can use it in proposal, comparison, and construction, the resulting completion problems are computed relative to $S$ and lie at $S'$ or $S''$. God mode is therefore omnipotent relative to the position from which it was granted, while the grant creates a stronger position.

The remaining strategies are typed. Computational obstruction calls for counterexample search, limit-correct presumption, stronger proof resources, or rationally bounded stopping. Missing commensurability calls for new readouts, calibrations, reference structures, or restricted comparison domains. Dynamical incommensurability calls for path-indexed states or an explicitly declared revision protocol. Reports of these actions should retain the contract and warrant under which they were taken.

$$
\boxed{
\begin{gathered}
\text{A theory is Perfect only under a complete comparison contract;}\\
\text{it is Done only under an accepted certificate;}\\
\text{and no fixed usable resource closes every completion problem it enables.}
\end{gathered}}
\tag{10.3}
$$

*Perfect Theory* identifies the conditions under which a particular inquiry may close, the resources required to close it, and the new boundary created when those resources become part of what the agent can express and construct.

# References

1. *On Learning Languages: Bayesian Updating of Epistemic Theories and the Meta-Complexity of Representational Choice*, companion manuscript, revised draft, 14 August 2026.
2. A. M. Turing, “On Computable Numbers, with an Application to the Entscheidungsproblem,” *Proceedings of the London Mathematical Society* s2-42(1), 1936--37, 230--265.
3. A. M. Turing, “Systems of Logic Based on Ordinals,” *Proceedings of the London Mathematical Society* s2-45(1), 1939, 161--228.
4. T. Radó, “On Non-Computable Functions,” *Bell System Technical Journal* 41(3), 1962, 877--884.
5. E. M. Gold, “Language Identification in the Limit,” *Information and Control* 10(5), 1967, 447--474.
6. M. Blum, “A Machine-Independent Theory of the Complexity of Recursive Functions,” *Journal of the ACM* 14(2), 1967, 322--336.
7. P. D. Grünwald, P. M. B. Vitányi, “Algorithmic Information Theory,” 2008. arXiv:0809.2754.
8. L. A. Levin, “Universal Sequential Search Problems,” *Problems of Information Transmission* 9(3), 1973, 265--266.
9. E. Bernstein, U. Vazirani, “Quantum Complexity Theory,” *SIAM Journal on Computing* 26(5), 1997, 1411--1473.
10. M. B. Pour-El, J. I. Richards, “The Wave Equation with Computable Initial Data such that Its Unique Solution Is Not Computable,” *Advances in Mathematics* 39(3), 1981, 215--239.
11. T. S. Cubitt, D. Pérez-García, M. M. Wolf, “Undecidability of the Spectral Gap,” *Nature* 528, 2015, 207--211.
12. A. S. Holevo, “Bounds for the Quantity of Information Transmitted by a Quantum Communication Channel,” *Problems of Information Transmission* 9(3), 1973, 177--183.
13. K. Weihrauch, *Computable Analysis*, Springer, 2000.
14. E. L. Post, “Recursively Enumerable Sets of Positive Integers and Their Decision Problems,” *Bulletin of the American Mathematical Society* 50, 1944, 284--316.
15. H. Putnam, “Trial and Error Predicates and the Solution to a Problem of Mostowski,” *Journal of Symbolic Logic* 30(1), 1965, 49--57.
16. J. R. Shoenfield, “On Degrees of Unsolvability,” *Annals of Mathematics* 69(3), 1959, 644--653.
17. K. T. Kelly, *The Logic of Reliable Inquiry*, Oxford University Press, 1996.
18. E. Allender, H. Buhrman, M. Koucký, D. van Melkebeek, D. Ronneburger, “Power from Random Strings,” *SIAM Journal on Computing* 35(6), 2006, 1467--1493.
19. M. Carmosino, R. Impagliazzo, V. Kabanets, A. Kolokolova, “Learning Algorithms from Natural Proofs,” *Computational Complexity Conference*, 2016.
20. Y. Liu, R. Pass, “On One-Way Functions and Kolmogorov Complexity,” *FOCS*, 2020.
21. S. Hirahara, “Non-Black-Box Worst-Case to Average-Case Reductions within NP,” *FOCS*, 2018.
22. Y. L. Ershov, “A Hierarchy of Sets, I,” *Algebra and Logic* 7(1), 1968, 25--43.
23. R. G. Downey, C. G. Jockusch, T. H. McNicholl, P. E. Schupp, “Asymptotic Density and the Ershov Hierarchy,” 2016. arXiv:1610.06504.
24. S. Abramsky, A. Brandenburger, “The Sheaf-Theoretic Structure of Non-Locality and Contextuality,” *New Journal of Physics* 13, 2011, 113036.
25. S. Abramsky, R. S. Barbosa, S. Mansfield, “The Contextual Fraction as a Measure of Contextuality,” *Physical Review Letters* 119, 2017, 050504.
26. S. Yu, N.-L. Liu, L. Li, C. H. Oh, “Joint Measurement of Two Unsharp Observables of a Qubit,” 2008. arXiv:0805.1538.
27. T. Heinosaari, M. M. Wolf, “Non-Disturbing Quantum Measurements,” *Journal of Mathematical Physics* 51, 2010, 092201.
28. S. Popa, “Relative Dimension, Towers of Projections and Commuting Squares of Subfactors,” *Pacific Journal of Mathematics* 137(1), 1989, 181--207.
29. J. Tomiyama, “On the Projection of Norm One in $W^*$-Algebras,” *Proceedings of the Japan Academy* 33, 1957, 608--612.
30. M. Takesaki, “Conditional Expectations in von Neumann Algebras,” *Journal of Functional Analysis* 9(3), 1972, 306--321.
31. D. Schmid, J. H. Selby, M. F. Pusey, R. W. Spekkens, “A Structure Theorem for Generalized-Noncontextual Ontological Models,” 2020. arXiv:2005.07161.
32. L. Catani et al., “Resource-Theoretic Hierarchy of Contextuality for General Probabilistic Theories,” 2024. arXiv:2406.00717.
33. T. S. Kuhn, *The Structure of Scientific Revolutions*, University of Chicago Press, 1962.
