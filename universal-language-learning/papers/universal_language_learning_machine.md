---
title: "Universal Language Learning Machine"
date: "16 August 2026 — Draft 2"
lang: en
---

# Abstract

A learner that changes its language can lose more than a hypothesis: it can lose the path by which an earlier representation was reached. This creates a problem for universality. A learner whose transition rules irreversibly discard an earlier state may enter an enrichment dead end from which otherwise effective continuations are no longer reachable. Universality therefore cannot be realized by a single forward trajectory: it requires a machine that preserves earlier states and can branch from them into incompatible continuations. The machine retains an append-only record of every finite input on which its learning-relevant state depends, reconstructs any earlier internal configuration from a finite prefix, and can fork a new learning itinerary from that configuration. I prove that forgetting a distinction between two behaviorally different configurations is irreversible learning erasure: no amount of further computation can recover both from the same retained state. Erasure also acts forward: identifying two configurations that some admissible boundary still separates makes at least one previously reachable behaviour permanently unreachable — a dead end — and a single such commit can destroy the reachable availability of a Perfect presentation. Deciding whether a state is such a dead end is \(\Pi^0_1\)-complete: escape certifies itself, entrapment is never certifiable — the halting problem of language learning. Conversely, every effective learner has a behaviorally equivalent replay-conservative realization when its packets, oracle replies, and realized random choices are logged. I then construct a Universal Language Learning Machine that dovetails all effectively described learners and embeds each of them as a branch rather than forcing their incompatible outputs into one sequence. The scheduling price of a branch is its surprisal under the machine's proposal law. The construction relativizes to arbitrary oracle resources, but no oracle-relative universal learner is universal for the learners available at its own Turing jump. Universality therefore supplies a canonical method of continued exploration, not an unrestricted certificate that learning is complete.

# 1. The third problem

Learning theory usually fixes a hypothesis language. *On Learning Languages* [1] instead treats the presentation itself---its expressions, decoder, interpreter, proposal law, and verifier---as revisable. *Perfect Theory* [2] asks when such a process may stop and proves that completion is relative both to the available comparison structure and to the resources with which universal claims are decided.

Those papers leave a third problem. If language learning remains open, what should carry it? A universal machine for ordinary computation executes any effectively described program. A universal machine for language learning must do more. Its simulated programs may change the language in which later programs, evidence, and comparisons are expressed. Their commits may not commute. An earlier presentation may be recoverable only from the evidential route by which it was reached. A universal learner must therefore preserve itineraries, not merely terminal outputs. Section 4 makes the danger exact: without preservation, a learning trajectory can enter dead ends that no input the boundary will supply can reopen — and the learner can never prove, from inside, that this has happened.

The construction developed here has three operations:

1. **Replay:** reconstruct the learning-relevant state at any retained finite stage.
2. **Fork:** install that state as the root of a new effective continuation.
3. **Embed:** represent every effective learner as a branch of one universal search tree.

Replay is not physical time reversal. Elapsed work is not refunded, and an external world is not restored. The theorem concerns internal reachability on a universal Turing machine with unbounded tape and time. Every finite replay has finite cost and therefore remains possible. If an agent has acted irreversibly on its environment, replay reconstructs the agent at the earlier boundary and can continue it in simulation or in a new interaction; it does not undo the old interaction.

This distinction makes forgetting exact. Computational difficulty concerns how long a retained distinction takes to use. Forgetting concerns whether the distinction remains present at all. Infinite time may overcome the first. It cannot invert a many-to-one erasure without information from outside the erased state.

The central results are consequently paired. The Replay--Fork Theorem shows that a retained finite learning history remains constructively re-enterable. The Forgetting Theorem shows that identifying two learning-distinguishable histories destroys at least one such re-entry. The Dead-End Theorems extend erasure forward: a collapsed distinction that the boundary still separates removes previously reachable continuations permanently, and recognizing this condition is \(\Pi^0_1\)-complete — escape is the halting problem of the learning itinerary, entrapment its divergence. The Conservatization Theorem shows that every effective learner can avoid this destruction by logging enough. The Universality Theorem then constructs a single replay-conservative machine whose branch tree contains every effective learner up to public behaviour.

# 2. Learners, ledgers, and behavioural state

## 2.1 Presentations and public packets

Let \(\mathcal Y\) be a countable effectively encoded packet space. Its elements are the public observations available at the boundary of the learning process. As in [1], a detected silence may be represented by a distinguished packet, while an undetected silence supplies no packet and prompts no step. Nothing below requires candidates to assign the same internal meaning to a packet.

A presentation has the form

$$
P=(\mathcal L,D,U),
\tag{2.1}
$$

where \(\mathcal L\) is a language, \(D\) a partial map from opaque carriers to expressions, and \(U\) an interpreter that runs expressions to produce further expressions. A learner may replace any component of its current presentation. Such a replacement is a **commit**.

Fix an effective coding of finite strings, presentations, configurations, and finite sequences. A deterministic learner with index \(e\) has an initial configuration \(c_{e,0}\) and a partial computable transition

$$
T_e(c_t,y_{t+1},r_{t+1})
=
(c_{t+1},o_{t+1}).
\tag{2.2}
$$

Here \(y_{t+1}\in\mathcal Y\) is the next public packet, \(r_{t+1}\) contains every finite exogenous reply used at that step, and \(o_{t+1}\) is the public output. The reply field includes realized random bits, answers to permitted oracle queries, and any other finite input not computable from the previous configuration and public packet. A randomized learner is therefore treated as a deterministic learner conditional on its realized reply stream.

The configuration \(c_t\) contains the current presentation \(P_t\), finite side state \(m_t\), and the commit itinerary \(h_t\). I assume that every transition on a valid completed trajectory halts. A partial branch is allowed to diverge; the universal construction will dovetail it without blocking the others.

## 2.2 Ledgers

At step \(t\), the learner retains a self-delimiting record \(a_t\). Its ledger is

$$
E_t
=
a_1a_2\cdots a_t.
\tag{2.3}
$$

The records are append-only. Each record carries enough boundary information to recover its endpoint, so every prefix

$$
E_k=a_1\cdots a_k,
\qquad
k\leq t,
\tag{2.4}
$$

is computable from \((E_t,k)\). The ledger may be lossy: a learner need not retain the raw packet, oracle reply, or realized coin. The consequences of that choice are the subject of Sections 4 and 5.

The evidential and semantic ledgers of [1] remain distinct. The evidential ledger records what entered the learning process and what was publicly produced. The semantic ledger records the executable meanings and commitments currently in force. Replay is grounded in retained evidence; it reconstructs a semantic state rather than allowing that state to rewrite its own evidential history.

## 2.3 Learning-relevant state

Exact machine configurations can differ in irrelevant cache contents. Replay should preserve learning, not the address of each unused tape cell. I therefore quotient configurations by future public behaviour.

For configurations \(c,c'\) of the same learner, write

$$
c\simeq_e c'
\tag{2.5}
$$

when every finite continuation of packets and exogenous replies produces the same public outputs and the same commit itinerary from both configurations, including the same pattern of divergence. The configurations are **learning-distinguishable** when \(c\not\simeq_e c'\). Equivalently, some finite continuation exposes a difference relevant to what the learner can say, commit to, or subsequently generate.

The relation (2.5) is semantic and need not be decidable. It prevents irrelevant hidden state from being mistaken for retained knowledge.

## 2.4 Replay-conservativity

The word *conservative* is overloaded in learning theory and in the theory of language extension. I use **replay-conservative** only for the following ledger property.

**Definition 2.1 (replay-conservative learner).** A learner \(L_e\) is replay-conservative when there is a partial computable map \(R_e\), defined on every valid finite ledger of \(L_e\), such that

$$
R_e(c_{e,0},E_t)
\simeq_e
c_{e,t}.
\tag{2.6}
$$

Thus the retained ledger determines the complete learning-relevant state. The definition permits caches and incremental execution. It requires only that their relevant contribution be reconstructible.

A learner is **replay-nonconservative** when no such map exists. Concretely, this occurs when two valid histories induce the same retained ledger but lead to learning-distinguishable configurations.

# 3. Replay and constructive re-entry

## 3.1 Prefix replay

**Lemma 3.1 (prefix recovery).** Given a valid self-delimiting ledger \(E_t\) and \(k\leq t\), the prefix \(E_k\) is computable.

**Proof.** Decode records from the beginning of \(E_t\) until the \(k\)th record boundary. Append-only writing ensures that the resulting string is exactly the ledger that existed at stage \(k\). \(\square\)

**Theorem 3.2 (Replay).** Let \(L_e\) be replay-conservative. There is a partial computable operation

$$
\operatorname{Replay}_e(c_{e,0},E_t,k)
\simeq_e
c_{e,k}
\qquad(k\leq t)
\tag{3.1}
$$

defined on every valid finite ledger.

**Proof.** Recover \(E_k\) by Lemma 3.1 and return \(R_e(c_{e,0},E_k)\). Equation (2.6) gives behavioural equivalence with the configuration originally reached at stage \(k\). \(\square\)

Replay is already stronger than a semantic snapshot. A snapshot preserves one configuration in the representation used when it was taken. The ledger records a derivation of that configuration from the declared boundary. If the replay procedure itself is later reimplemented, the derivation remains the public object against which the new implementation can be checked.

## 3.2 Fork

Let \(\eta\) be an effective continuation procedure. It may emit a simulated continuation of packets and replies, connect the reconstructed agent to a new live interaction, or implement a counterfactual intervention. Define

$$
\operatorname{Fork}_e(c_{e,0},E_t,k,\eta)

$$

to allocate a new branch, install

$$
\widehat c_k
=
\operatorname{Replay}_e(c_{e,0},E_t,k),
\tag{3.2}
$$

and continue \(L_e\) from \(\widehat c_k\) under \(\eta\).

**Theorem 3.3 (Replay--Fork).** Every finite itinerary position of a replay-conservative learner is constructively re-enterable. More precisely, for every valid \(E_t\), every \(k\leq t\), and every effective finite continuation \(\eta\), the forked branch reproduces the public behaviour that \(L_e\) would produce by receiving \(\eta\) from its original stage-\(k\) configuration.

**Proof.** Theorem 3.2 returns a configuration behaviourally equivalent to \(c_{e,k}\). Behavioural equivalence is defined by agreement on every finite continuation, so running \(\eta\) produces the same public outputs and commits. Each replay and each finite continuation consists of finitely many terminating computations, hence completes in finite time. \(\square\)

The theorem creates a reverse edge in the internal reachability graph: from a later universal-machine state one may allocate a branch rooted at an earlier learning state. It does not reduce the accumulated work counter. Under a finite budget, replay may be unaffordable and its cost must be charged. Under the unbounded machine used for the existence theorem, finite cost affects delay but not reachability.

For interactive systems, the re-entry is equally exact but differently interpreted. The learner's earlier internal state is recovered. The external world is not. A fork that requires the earlier world must use a recorded simulator, a restorable environment, or a new experiment. The absence of such an apparatus is a reference-resource limitation, not a failure of internal replay.

# 4. Forgetting

## 4.1 Erasure as a quotient

Let \(\mathcal C_e\) be the valid learning configurations of \(L_e\). A **forgetting operation** is a computable map

$$
q:\mathcal C_e\longrightarrow\overline{\mathcal C}_e
\tag{4.1}
$$

for which there are learning-distinguishable configurations \(c_0,c_1\) satisfying

$$
c_0\not\simeq_e c_1,
\qquad
q(c_0)=q(c_1).
\tag{4.2}
$$

The definition excludes harmless compression. If two configurations have identical future learning behaviour, identifying them removes no learning-relevant distinction. Forgetting begins when a behaviourally exposed distinction is collapsed.

**Theorem 4.1 (Forgetting).** A forgetting operation is irreversible from the retained state. There is no computable map \(s\) satisfying

$$
s(q(c))\simeq_e c
\tag{4.3}
$$

for every configuration in any set containing both \(c_0\) and \(c_1\) from (4.2). Consequently, after forgetting, at least one of their continuation trees is absent from internal replay.

**Proof.** Suppose such an \(s\) existed. Since \(q(c_0)=q(c_1)\), the value of \(s\) on both erased configurations would be the same. Equation (4.3) would then make that value behaviourally equivalent to both \(c_0\) and \(c_1\), contradicting \(c_0\not\simeq_e c_1\). \(\square\)

The obstruction is not undecidability. Both configurations may be finite and individually easy to compute. The obstruction is non-injectivity: after (4.2), the retained state contains no fact that selects which preimage was present.

> // **Author's comment.** Infinite time can search forever for a bit that is no longer present. It will not find it.

## 4.2 Implementations of the universal learner

Let \(U\) be a replay-fork machine and \(M\) a host learner. A faithful implementation of a family \(C\) of \(U\)-configurations consists of computable maps

$$
\iota:C\longrightarrow\mathcal C_M,
\qquad
\rho:\mathcal C_M\longrightarrow C,
\qquad
\rho\circ\iota=\operatorname{id}_C,
\tag{4.4}
$$

which preserve public transitions, replay, and fork. The retraction makes the representation faithful: distinct learning states of \(U\) remain recoverable inside \(M\).

**Corollary 4.2 (nonconservative implementation dichotomy).** Suppose a replay-nonconservative learner \(M\) is capable of implementing \(U\).

1. If the implementation remains faithful, the image \(\iota(C)\) forms a replay-conservative subsystem of \(M\), even if other parts of \(M\) are nonconservative.
2. If a host operation \(q\) identifies the images of two learning-distinguishable \(U\)-configurations, then no retraction exists after \(q\). The operation is irreversible learning erasure, and the resulting host no longer implements the full replay-fork structure of \(U\).

**Proof.** In the first case, replay in \(U\), followed by \(\iota\), reconstructs every configuration in the implementation image. In the second, if \(q(\iota(c_0))=q(\iota(c_1))\) for distinguishable \(c_0,c_1\), any post-erasure retraction would assign one value to the common host state and could not recover both. This is Theorem 4.1 applied through the embedding. \(\square\)

Thus every nonconservative learner capable of hosting the universal learner faces an exact choice: externalize a conservative record for the universal subsystem, or implement forgetting as irreversible erasure of a learning path.

Recovery from another copy, a backup, or a renewed observation does not contradict the theorem. It supplies information outside the erased state. The recovery mechanism is itself the conservative record that the original state lacked.

## 4.3 Dead ends

The Forgetting Theorem is retrospective: it concerns re-entry into the past. Erasure also acts on the future. This subsection makes the abstract's warning exact and shows that the resulting condition, unlike replay loss, cannot in general be recognized from inside.

Fix a learner \(L_e\). A **boundary class** \(I\) is a prefix-closed, effectively enumerable set of finite continuations of packets and exogenous replies; it declares which future inputs the environment may supply. For configurations \(c,c'\), write \(c\simeq_e^I c'\) when every continuation in \(I\) produces the same public outputs and commits from both; this coarsens (2.5) by quantifying only over admissible futures. For a configuration \(c\), let

$$
\operatorname{Reach}_I(c)
=
\bigl\{(\eta,\omega):\eta\in I,\ \omega=\operatorname{out}_e(c,\eta)\bigr\}
\tag{4.5}
$$

be its reachable behaviours, where \(\operatorname{out}_e(c,\eta)\) is the public output-and-commit record produced by running \(L_e\) from \(c\) on \(\eta\). Determinism gives the factorization on which everything below rests: \(\operatorname{Reach}_I(c)\) depends on the past only through \(c\).

**Definition 4.3 (dead end).** A forgetting operation \(q\) creates a **dead end at \(c\) relative to \(I\)** when some behaviour in \(\operatorname{Reach}_I(c)\) is absent from \(\operatorname{Reach}_I(q(c))\): a continuation available before the erasure is available on no forward path after it.

**Theorem 4.4 (dead-end existence).** Let \(q\) identify configurations \(c_0\not\simeq_e^I c_1\) — configurations still separated by some continuation in the declared boundary class. Then \(q\) creates a dead end at \(c_0\) or at \(c_1\) relative to \(I\). Moreover, such triples exist: there are an effective learner, a computable forgetting operation, and an effectively enumerable boundary class realizing the hypothesis with both dead ends nonvacuous.

**Proof.** Let \(\eta^*\in I\) separate the pair, \(\omega_0=\operatorname{out}_e(c_0,\eta^*)\neq\operatorname{out}_e(c_1,\eta^*)=\omega_1\). Determinism assigns the erased configuration a single record \(\operatorname{out}_e(q(c_0),\eta^*)\), which differs from \(\omega_0\) or from \(\omega_1\); the corresponding pair \((\eta^*,\omega_i)\) lies in \(\operatorname{Reach}_I(c_i)\) but in \(\operatorname{Reach}_I(q(c_i))\) for no \(i\), since each \(\eta\) carries exactly one record.

For existence, let the first packet carry a bit \(b\in\{0,1\}\), stored in a register; on every later \(\mathsf{recall}\) packet the learner outputs the register, on other packets \(0\); the register is writable only by the initial packet. Let \(q\) set the register to \(0\), and let \(I\) contain exactly the continuations whose packets exclude the initial writable position. Then \(c_0\not\simeq_e^I c_1\) via \(\eta^*=\mathsf{recall}\), and every configuration reachable from \(q(c_1)\) under \(I\) carries register \(0\): the behaviour \((\mathsf{recall},1)\) is permanently unreachable, though it was immediate before the erasure. \(\square\)

The relativization to \(I\) is the content of the theorem, not a concession. A boundary that re-supplies the erased information reopens the branch; §4.2 already recorded that such recovery imports a conservative record from outside the erased state. A dead end is an erasure whose complement the boundary declines to fund.

**Corollary 4.5 (enrichment dead ends; reachable Perfection is path-dependent).** There exist an effective learner, a finality contract \(\mathfrak F\) in the sense of [2], a boundary class \(I\), and a forgetting operation \(q\) such that before the erasure some continuation in \(I\) commits to a presentation that is Perfect for \(\mathfrak F\), and after it no continuation in \(I\) commits to any Perfect presentation. Relative to reachable candidates, the availability of Perfection — globally \(\Sigma^0_2\)-complete and path-independent [2, Thm. 7.5] — can be destroyed by a single commit of the learner itself.

**Proof.** In the construction of Theorem 4.4, replace the output on \((\mathsf{recall},1)\) by a commit installing presentation \(P_1\), and take a contract whose unique Perfect candidate is \(P_1\), every other reachable candidate carrying strictly larger loss at some target. Before the erasure the committing continuation lies in \(I\). After it, no reachable configuration issues the commit; and because proposal laws assign mass only to candidates their current language can formulate, the excluded presentation cannot re-enter through proposal [1, §3.5]. \(\square\)

**Theorem 4.6 (undetectability of entrapment).** Fix a sound effective verifier \(V_X\) accepting escape certificates: finite records establishing that a continuation from the given configuration has produced a declared target behaviour. For instances \(\langle e,c,I\rangle\) with effectively enumerable \(I\), define

$$
\mathsf{DEADEND}
=
\bigl\{\langle e,c,I\rangle:
\text{no }\eta\in I\text{ yields a record accepted by }V_X\text{ from }c\bigr\}.
\tag{4.6}
$$

Over instance classes containing the construction below, \(\mathsf{ESCAPE}\), its complement, is \(\Sigma^0_1\)-complete, and \(\mathsf{DEADEND}\) is \(\Pi^0_1\)-complete. Consequently no sound effective verifier certifies every true instance of entrapment, while every false instance is refuted by a finite escape witness.

**Proof.** Membership: dovetail the continuations in \(I\) from \(c\) and run \(V_X\) on each finite record; acceptance is a finite event, so \(\mathsf{ESCAPE}\) is computably enumerable and \(\mathsf{DEADEND}\) co-c.e. For hardness, given a machine--input pair \((M,w)\), let the learner simulate \(M(w)\) one step per packet and emit the certifiable target record exactly when the simulation halts; then \(\langle e,c,I\rangle\in\mathsf{DEADEND}\iff M(w)\uparrow\). A sound verifier complete for entrapment would computably enumerate a \(\Pi^0_1\)-complete set whose complement is already c.e., and would therefore decide it. \(\square\)

Escape is thus literally the halting problem of the learning itinerary, and entrapment its divergence:

$$
\boxed{
\begin{gathered}
\text{whether a learning state still has a way forward}\\
\text{is the halting problem of language learning:}\\
\text{escape certifies itself; entrapment is never certifiable.}
\end{gathered}}
\tag{4.7}
$$

The asymmetry inverts the announcement asymmetry of [2, §5.2]. There, the favourable claim — completion — could only be presumed, while its refutation was certifiable. Here the favourable claim — a way forward — is certifiable, while its refutation never is. Between the two, continued exploration is not a temperament but the only sound policy on both sides of the boundary: a learner can never prove that it is stuck, and can only discover that it was not.

> // **Author's comment.** This is what the universal machine is *for*. Branches are preserved not because deletion is impolite but because no effective agent can certify which deletions are fatal.

# 5. Conservatization

The theorems of Section 4 are necessity results: faithful replay requires retained distinctions, and unretained distinctions can close futures that no admissible boundary reopens — undetectably. The converse question is constructive. Does replay-conservativity exclude behaviours available to ordinary effective learners? In the unbounded model, it does not.

## 5.1 The full execution ledger

Let \(L_e\) be any effective learner of the form (2.2). Define its full record at step \(t\) by

$$
a_t^\dagger
=
\langle y_t,r_t\rangle,
\qquad
E_t^\dagger
=
a_1^\dagger\cdots a_t^\dagger.
\tag{5.1}
$$

The record includes every exogenous finite input that affected the transition. The learner \(L_e^\dagger\) carries the same current simulated configuration as \(L_e\), emits the same public output, makes the same commits, and additionally appends \(a_t^\dagger\).

**Theorem 5.1 (Conservatization).** For every effective learner \(L_e\), there is a replay-conservative learner \(L_e^\dagger\) such that, on every stream of packets and exogenous replies:

1. \(L_e\) and \(L_e^\dagger\) have identical public outputs and commit itineraries step by step;
2. every forward configuration reached by \(L_e\) has a behaviourally equivalent configuration reached by \(L_e^\dagger\);
3. every finite configuration of \(L_e^\dagger\) is replayable and forkable;
4. the additional current-run work is the work of encoding and appending the full record, while replay of stage \(k\) costs at most a fresh simulation of the first \(k\) transitions plus decoding overhead.

**Proof.** On the current run, \(L_e^\dagger\) executes the transition of \(L_e\) and carries its resulting state incrementally. Hence the public outputs and commits agree exactly. Given \((e,c_{e,0},E_t^\dagger)\), reconstruct \(c_{e,t}\) by simulating \(T_e\) from the initial configuration on the recorded pairs \(\langle y_s,r_s\rangle\) for \(s\leq t\). Every transition on the valid recorded trajectory halts, so the reconstruction is finite. This supplies the replay map required by Definition 2.1. The cost statements follow from the construction. \(\square\)

Conservatization does not claim equal bounded accessibility. If ledger storage, write bandwidth, replay time, or privacy is charged, \(L_e^\dagger\) may exceed a budget that \(L_e\) satisfies. The theorem says that no forward learning itinerary is available only through forgetting when unbounded effective resources determine reachability. Resource-bounded differences remain real and belong in the charged realization.

## 5.2 Minimal sufficient ledgers

The raw ledger in (5.1) is sufficient but rarely minimal. A retention map \(\sigma\) may compress the history while preserving replay whenever

$$
\sigma(h)=\sigma(h')
\Longrightarrow
c(h)\simeq_e c(h').
\tag{5.2}
$$

Condition (5.2) says that every fibre of \(\sigma\) lies inside one behavioural-equivalence class. It is the exact boundary between compression and forgetting.

**Proposition 5.2 (ledger sufficiency).** A computable retention map supports replay precisely when the behavioural state induced by every valid history is a computable function of the retained ledger. If (5.2) fails, the map performs learning erasure; if it holds but no reconstruction is computable, the information is retained extensionally but not operationally replayable by the learner.

The last distinction parallels the separation between generative addressability and operational accessibility in [1]. A state may be determined by the ledger yet remain too costly for a bounded agent to reconstruct.

# 6. The Universal Language Learning Machine

## 6.1 Universality over branches

Fix an acceptable effective enumeration

$$
L_0,L_1,L_2,\ldots
\tag{6.1}
$$

of packet-driven learners, together with their conservatizations from Theorem 5.1. An index includes the initial presentation, transition procedure, retention rule, and public boundary. Randomized learners appear through their logged reply streams.

The **Universal Language Learning Machine**, written \(\mathbb U\), maintains one master evidential ledger and a computably enumerable tree of simulation branches. A branch address contains at least

$$
b=\langle e,c_{e,0},\zeta\rangle,
\tag{6.2}
$$

where \(e\) is a learner index and \(\zeta\) specifies any branch-local exogenous replies not already fixed by the common ledger. At universal stage \(s\), \(\mathbb U\) dovetails the first \(s\) simulation tasks for \(s\) steps each. A diverging transition delays only its own branch.

The machine records a node whenever a simulated learner completes a finite transition. Each node contains the branch address, ledger prefix, simulated configuration, public output, and commit edge. Its append-only master ledger also records branch allocations, incoming packets and replies, and the current universal stage. Together with the fixed dovetail schedule, this is enough to reconstruct partially executed as well as completed branch computations. Replay may allocate a new node at an earlier prefix; fork attaches an effective continuation beneath it.

Universality is therefore not the assertion that one public output equals the outputs of all learners. Incompatible learners occupy incompatible branches. A separate selector may make one branch active for external action, but selection does not delete the others.

## 6.2 The universality theorem

**Theorem 6.1 (Universal Language Learning Machine).** There exists a replay-conservative effective machine \(\mathbb U\) such that, for every effective learner \(L_e\):

1. **Branch simulation.** For every valid finite trajectory of \(L_e\), some branch of \(\mathbb U\) eventually contains a behaviourally identical trajectory.
2. **Embedding with retraction.** There are computable branch maps \(\iota_e\) and \(\rho_e\) satisfying

   $$
   \rho_e\circ\iota_e
   =
   \operatorname{id}
   \tag{6.3}
   $$

   on the learning-relevant configurations of the conservatized learner \(L_e^\dagger\).
3. **Replay and fork preservation.** The embedding sends retained prefixes to retained prefixes, replay to replay, and effective continuations to forked continuations.
4. **Self-inclusion.** Since \(\mathbb U\) is effective, it has an index \(u\) in (6.1), and its behaviour appears on branch \(u\).

**Proof.** The universal interpreter enumerates branch addresses and dovetails their transition simulations. For any completed finite trajectory of \(L_e\), all of its finitely many computations eventually receive enough universal stages to halt, so the corresponding nodes enter the tree. Map a configuration of \(L_e^\dagger\) to its branch node, including the learner index and full ledger prefix. The retraction reads the simulated configuration from that node, giving (6.3). Because the ledger prefix and index are retained, Theorem 3.2 is available within the branch, and the universal scheduler can enumerate every effective continuation. Finally, the current universal stage and every exogenous input are retained. The complete finite master state is therefore computable by rerunning the fixed dovetail schedule to that stage, so \(\mathbb U\) is replay-conservative. Self-inclusion follows from the enumeration. \(\square\)

The theorem covers nonconservative learners through their behaviourally equivalent conservatizations. It does not claim that the original lossy ledger becomes replayable. The universal branch retains the fuller ledger required to represent that learner without erasure.

## 6.3 Canonicity

Let \(\mathbb U\) and \(\mathbb U'\) use acceptable enumerations of the same effective learner class. A compiler from one enumeration to the other maps each learner index to an index with the same public behaviour. Applying the universal construction branchwise gives mutual computable embeddings.

**Corollary 6.2 (canonicity up to translation).** Any two Universal Language Learning Machines for the same effective learner class simulate each other's branches through computable translations.

This is deliberately weaker than isomorphism of the entire itinerary trees. Different machines may duplicate branches, use different padding, or schedule the same simulations in different orders. Universality supplies a canonical capacity, not a unique concrete tree.

# 7. The cost of universality

Universality as reachability uses unbounded time. A finite agent still needs to know what the universal schedule charges for a branch.

## 7.1 Weighted dovetailing

Let \(g\) be an effectively given rational proposal law over prefix-free branch addresses with

$$
g(b)>0,
\qquad
\sum_b g(b)\leq1.
\tag{7.1}
$$

Choose a weighted dovetail schedule that gives branch \(b\) at least a constant fraction of \(g(b)\) of the available simulation work. Let \(T_b(n)\) be the universal-interpreter work required to complete the first \(n\) local steps of that branch when run without competition, including interpretation and logging.

**Theorem 7.1 (surprisal price).** There is a constant \(c\), independent of \(b\) and \(n\), such that the weighted universal schedule completes the first \(n\) steps of branch \(b\) within work

$$
T_{\mathbb U}(b,n)
\leq
\frac{c}{g(b)}
\bigl(T_b(n)+1\bigr).
\tag{7.2}
$$

Consequently,

$$
\log_2 T_{\mathbb U}(b,n)
\leq
\log_2\bigl(T_b(n)+1\bigr)
-
\log_2 g(b)
+O(1).
\tag{7.3}
$$

**Proof.** Weighted dovetailing assigns branch \(b\) one unit of simulation work in at most \(c/g(b)\) units of master work. Repeating this allocation for the \(T_b(n)\) work units required by the branch gives (7.2); taking logarithms gives (7.3). \(\square\)

The additive universal price is therefore the surprisal

$$
I_g(b)
=
-\log_2g(b).
\tag{7.4}
$$

For the prefix prior \(g(b)=2^{-|b|}\), this becomes description length. For a task-adapted proposal law it need not. The equality between address length and search price is a property of the chosen universal schedule, not of arbitrary bounded proposal procedures.

## 7.2 Itinerary weights

A language-learning branch may be minted incrementally. If the proposal law assigns conditional weights

$$
g(a_k\mid h_{<k})
$$

to successive commits, the weight of a finite itinerary \(h=a_1\cdots a_m\) is

$$
g(h)
=
\prod_{k=1}^m
g(a_k\mid h_{<k}),
\tag{7.5}
$$

and its scheduling charge is

$$
I_g(h)
=
-\log_2g(h)
=
\sum_{k=1}^m
-\log_2g(a_k\mid h_{<k}).
\tag{7.6}
$$

Thus the universal price of an itinerary is the cumulative surprise of the language changes required to reach it. Replay affects this price in a precise way: revisiting a retained prefix requires work, but it does not require proposing the prefix again. A fork pays only for the new continuation plus replay cost.

# 8. Relative universality

## 8.1 Oracle-relative machines

Let \(R\) be an installed oracle or, more generally, the effective code of the computational and reference operations available to the learner. An \(R\)-effective learner may query \(R\) during its transitions. Repeating the construction with an oracle universal interpreter gives \(\mathbb U^R\).

**Theorem 8.1 (relative universality).** For every oracle \(R\):

1. \(\mathbb U^R\) embeds every \(R\)-effective learner as a replayable branch.
2. There is an \(R'\)-effective learner whose public behaviour is not behaviourally equivalent to any \(R\)-effective learner.
3. Hence \(\mathbb U^R\) is not universal for the \(R'\)-effective learner class, while \(\mathbb U^{R'}\) is.

**Proof.** The first claim relativizes the dovetailing proof of Theorem 6.1. For the second, let a learner receive an index \(n\) and emit the bit deciding whether the \(n\)th \(R\)-oracle program halts. This behaviour is computable from \(R'\). If an \(R\)-effective learner had the same behaviour on every input, it would decide the \(R\)-halting problem, contradicting the jump theorem. The third claim follows. \(\square\)

Define

$$
\mathbb U^R
\preccurlyeq
\mathbb U^S
$$

when every \(R\)-effective branch is computably translatable into an \(S\)-effective branch. If \(R\leq_T S\), then \(\mathbb U^R\preccurlyeq\mathbb U^S\).

**Corollary 8.2 (no greatest universal learner).** The oracle-indexed extension order has no greatest element. For every \(\mathbb U^R\), the machine \(\mathbb U^{R'}\) realizes a strictly larger class of effective boundary behaviours.

This is the constructive companion to the Omnipotence Theorem of [2]. *Perfect Theory* shows that granting \(R\) moves the next completion problem to \(R'\). The present theorem supplies the corresponding learner: \(\mathbb U^{R'}\) is universal for the enlarged effective class. No claim of cofinality for the finite jump sequence is required; the construction applies separately above every oracle base.

# 9. Itineraries, selection, and completion

## 9.1 A tree, not a posterior state

Nonconservative language changes need not commute. Starting from one presentation, commits \(a\) then \(b\) may produce a different presentation from commits \(b\) then \(a\). The Universal Language Learning Machine therefore retains nodes of the form

$$
(P,h,E),
\tag{9.1}
$$

not merely the terminal presentation \(P\). Two branches reaching extensionally equivalent presentations may still differ in their retained evidence, available retractions, or future proposal laws.

Replay does not collapse these paths. It makes them separately accessible. If two paths are later proved behaviourally equivalent for the declared task, they may be compressed into one node without forgetting by Proposition 5.2. Without that proof, merging them risks the erasure identified by Theorem 4.1.

## 9.2 Selection

The universal tree describes what the machine can continue. It does not by itself decide what the agent should execute in the external world. Let

$$
\chi(E,T)
$$

be a selector that chooses an active branch from ledger \(E\) and current universal tree \(T\). The selector may use posterior risk, expected improvement, verification status, accessibility, reversibility, or the value of further information. It is itself an effective learner and therefore appears as a branch of \(\mathbb U\).

Separating enumeration from selection avoids a false notion of universality. A single action cannot equal every incompatible action proposed by every learner. Universality means that the alternatives and their routes remain representable and recoverable before the selector commits.

## 9.3 Local Done and global openness

A universal learner may certify local completion. An active branch can be Good, Final, or Perfect under a declared finality contract, and a sound certificate may license calling that branch Done [2]. Universality does not invalidate the certificate.

What universality forbids is a silent change of quantifiers. A certificate for one candidate class, target domain, comparison structure, and resource base does not close the full extension tree. New branches may change any of those components. Determining that no universal branch ever produces an accepted improvement is again a completion problem, not a consequence of running the universal machine for a long time.

The two statements are compatible:

$$
\boxed{
\begin{gathered}
\text{a branch may be Done under a fixed contract,}\\
\text{while the universal extension process remains open.}
\end{gathered}}
\tag{9.2}
$$

Under a contract whose admissible successors include oracle extensions and whose objective rewards strict increases in simulation coverage, Corollary 8.2 supplies a better successor above every resource base. Such a contract has no Final universal learner. Other contracts may close. The distinction is the same contract-relativity that governs Perfection throughout [2].

# 10. Relation and scope

## 10.1 Universal computation and search

The universal interpreter descends from Turing's universal machine [3] and the theory of acceptable programming systems [4]. Mutual translation between universal machines is standard; the new object here is the preserved tree of language-changing itineraries and the replay/fork structure carried by its ledger.

Weighted dovetailing follows universal search [5]. Equation (7.3) separates two costs that are often merged: the cost of simulating a branch once addressed, and the surprisal cost of allocating search mass to its address. This is the universal-schedule case of the broader accessibility distinction in [1].

## 10.2 Learning in the limit and retained memory

Gold's model identifies languages from streams of data [6]. Iterative and bounded-example-memory learners restrict what earlier evidence remains directly available [7,8]. The present paper asks a different but adjacent question: which earlier *learning configurations* remain constructively accessible after the learner is allowed to revise its presentation itself?

The Conservatization Theorem uses unbounded storage and time to establish an extensional result. It does not collapse the bounded-memory hierarchies. When storage is charged, forgetting may improve performance within one budget even though it destroys replay reachability. The choice is then economic rather than logical, and the erased path cannot later be recovered without another copy.

## 10.3 Self-modifying machines

Gödel machines perform self-rewrites after proving, relative to an initial axiomatic description of utility and hardware, that the rewrite is useful [9]. A Universal Language Learning Machine does not require every branch to be proof-gated. It records proof-gated learners, experimental learners, Bayesian selectors, and arbitrary effective self-modifiers as separate branches. Verification affects which branch a selector should trust; it does not determine which branches are representable.

The difference is not that proof is dispensable. Proof-carrying commits may be essential for safe external action. The difference is architectural: the universal tree retains unselected and currently unjustified continuations without executing them as the active presentation.

## 10.4 Scope conditions

The results depend on the following assumptions.

1. Packets, configurations, replies, and presentations are finitely encoded.
2. Every completed local transition is effective and halts; divergent branches are handled by dovetailing.
3. Realized randomness and oracle replies needed for replay are recorded.
4. Replay and fork concern the learner's internal configuration. External-world restoration requires a separate apparatus.
5. Unbounded tape and time determine reachability. Finite budgets may make replay inaccessible and must charge logging, storage, and recomputation.
6. Forgetting means the identification of learning-distinguishable configurations. Compression within one behavioural-equivalence class is not forgetting.
7. Universality is branchwise. A selector, not the universal tree itself, produces the active external action.
8. Relative universality is indexed by an oracle or resource interface. No finite jump chain is claimed to be cofinal in all computational degrees.
9. Local finality certificates remain valid under their contracts. They do not close undeclared extensions of those contracts.
10. Dead ends are relative to a declared boundary class of admissible continuations. A boundary that re-supplies the erased information reopens the branch; the dead-end and undetectability theorems concern boundaries that do not, and their instance classes must contain the stated constructions.

# 11. Conclusion

A universal language learner must preserve more than a menu of hypotheses. When language changes are path-dependent, the route to a presentation determines which evidence, meanings, and future continuations remain available. The appropriate universal object is therefore a replayable tree of itineraries.

For a replay-conservative learner, every retained finite state can be reconstructed and used as a new branch. For a replay-nonconservative learner, identifying two behaviourally distinct states is irreversible learning erasure. Infinite computation does not repair the loss because the erased state no longer contains the distinction to be computed. The loss is not only retrospective: relative to boundaries that do not re-teach what was discarded, erasure closes continuations permanently — it can remove the only reachable Perfect presentation — and no effective procedure can certify from inside that the closure has occurred. Universality is therefore not an ornament but the only sound response to an undetectable hazard. Every effective learner nevertheless has a replay-conservative realization when the full finite causes of its transitions are logged.

The Universal Language Learning Machine dovetails these realizations branchwise. Its universality does not force incompatible learners into one output, and its selector does not destroy branches it declines to execute. The cost of admitting a branch is the surprisal of its address under the declared proposal law, together with the work of simulating and replaying it.

The machine is universal only relative to its resources. Above every oracle \(R\) lies a learner available at \(R'\) that \(\mathbb U^R\) cannot reproduce. This is not a defect in the construction. It is the operational form of the completion boundary established in *Perfect Theory*.

The three papers can therefore be read in order:

$$
\boxed{
\begin{gathered}
\textit{On Learning Languages}\text{ explains how languages change;}\\
\textit{Perfect Theory}\text{ explains when one branch may close;}\\
\textit{Universal Language Learning Machine}\text{ preserves the paths along which learning continues.}
\end{gathered}}
\tag{11.1}
$$

# References

1. *On Learning Languages: Bayesian Updating of Epistemic Theories and the Meta-Complexity of Representational Choice*, companion manuscript, revised draft, 14 August 2026.
2. *Perfect Theory*, companion manuscript, revised draft, 16 August 2026.
3. A. M. Turing, “On Computable Numbers, with an Application to the Entscheidungsproblem,” *Proceedings of the London Mathematical Society* s2-42(1), 1936--37, 230--265.
4. H. Rogers, Jr., *Theory of Recursive Functions and Effective Computability*, McGraw--Hill, 1967.
5. L. A. Levin, “Universal Sequential Search Problems,” *Problems of Information Transmission* 9(3), 1973, 265--266.
6. E. M. Gold, “Language Identification in the Limit,” *Information and Control* 10(5), 1967, 447--474.
7. R. Wiehagen, “Limes-Erkennung rekursiver Funktionen durch spezielle Strategien,” *Journal of Information Processing and Cybernetics* 12, 1976, 93--99.
8. S. Lange, T. Zeugmann, “Refined Incremental Learning,” in X. Yao, ed., *Proceedings of the Eighth Australian Joint Conference on Artificial Intelligence---AI'95*, World Scientific, 1995, 147--154.
9. J. Schmidhuber, “Gödel Machines: Fully Self-Referential Optimal Universal Self-Improvers,” in B. Goertzel and C. Pennachin, eds., *Artificial General Intelligence*, Springer, 2006, 199--226.
