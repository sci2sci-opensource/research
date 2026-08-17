---
title: "Universal Language Learning Machine"
date: "17 August 2026 — Draft 5"
lang: en
---

# Abstract

While learning, agents modify their internal states. This creates a problem that does not arise when learning is confined to a fixed representation: an update can erase not only an earlier answer, but also routes to alternatives that were reachable from the earlier state. Once the relevant distinction has been discarded, no amount of further computation can recover it from what remains, and the agent may be unable to determine whether every route to a desired result has been lost. This paper asks what a learning process must retain if it is to remain universal over its possible continuations. I construct a machine that records the finite external inputs on which each learning state depends, uses that record to reconstruct earlier states, and continues from them along new paths. Every effectively described learner is represented as a separate path, so incompatible updates need not be forced into a single sequence. I prove that every effective learner has an equivalent implementation of this form, whereas collapsing two states with different possible futures irreversibly destroys at least one of those futures and can eliminate the only reachable optimal representation. For any decidable target, finding a continuation that reaches it is \(\Sigma^0_1\)-complete, while establishing that no continuation does is \(\Pi^0_1\)-complete. The cost of retaining a path is governed by its weight under the machine's proposal rule. Stronger computational resources enlarge the machine's reach but do not make it final: each enlargement admits learning processes beyond the resulting machine. The construction therefore provides a universal discipline for continued learning, not a certificate that learning is complete.

# 1. The third problem

Learning theory usually fixes a hypothesis language. *On Learning Languages* [1] instead treats the presentation itself---its expressions, decoder, interpreter, proposal law, and verifier---as revisable. *Perfect Theory* [2] asks when such a process may stop and proves that completion is relative both to the available comparison structure and to the resources with which universal claims are decided.

Those papers leave a third problem. If language learning remains open, what should carry it? A universal machine for ordinary computation executes any effectively described program. A universal machine for language learning must do more. Its simulated programs may change the language in which later programs, evidence, and comparisons are expressed. Their commits may not commute. An earlier presentation may be recoverable only from the evidential route by which it was reached. A universal learner must therefore preserve itineraries, not merely terminal outputs. Section 2 makes the danger exact: without preservation, a learning trajectory can enter target dead ends that no input the declared boundary will reopen, and no effective finite-certificate procedure can recognize every such case from inside.

The construction developed here has three operations:

1. **Replay:** reconstruct the learning-relevant state at any retained finite stage.
2. **Fork:** install that state as the root of a new effective continuation.
3. **Embed:** represent every effective learner as a branch of one universal search tree.

Replay is not physical time reversal. Elapsed work is not refunded, and an external world is not restored. The theorem concerns internal reachability on a universal Turing machine with unbounded tape and time. Every finite replay has finite cost and therefore remains possible. If an agent has acted irreversibly on its environment, replay reconstructs the agent at the earlier boundary and can continue it in simulation or in a new interaction; it does not undo the old interaction.

This distinction makes forgetting exact. Computational difficulty concerns how long a retained distinction takes to use. Forgetting concerns whether the distinction remains present at all. Infinite time may overcome the first. It cannot invert a many-to-one erasure without information from outside the erased state.

The central results are consequently paired. The Replay--Fork Theorem shows that a retained finite learning history remains constructively re-enterable. The Forgetting Theorem shows that identifying two learning-distinguishable histories destroys at least one such re-entry. The Branch-Loss Theorem extends this result forward: a collapsed distinction that the boundary still separates destroys at least one counterfactual continuation tree. The Enrichment Dead-End Theorem shows that such a commit can remove every admissible route to a Perfect presentation. For any declared decidable target, escape is the halting side of reachability and entrapment the non-halting side. The Conservatization Theorem shows that every effective learner can avoid this destruction by logging enough. The Universality Theorem then constructs a single replay-conservative machine whose branch tree contains every effective learner up to public behaviour.

# 2. Learning trajectories and lost futures

Before constructing a universal learner, I isolate the failure that makes such a construction necessary. Only a minimal transition model is needed. The learner receives public packets, changes its internal presentation, and thereby changes which future expressions and commits remain reachable. A transition can preserve its current output while destroying a counterfactual route that later turns out to be indispensable.

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

## 2.2 Learning-relevant state

Exact machine configurations can differ in irrelevant cache contents. The distinctions at issue concern future learning behaviour, not the address of each unused tape cell. I therefore quotient configurations by future public behaviour.

For configurations \(c,c'\) of the same learner, write

$$
c\simeq_e c'
\tag{2.3}
$$

when every finite continuation of packets and exogenous replies produces the same public outputs and the same commit itinerary from both configurations, including the same pattern of divergence. The configurations are **learning-distinguishable** when \(c\not\simeq_e c'\). Equivalently, some finite continuation exposes a difference relevant to what the learner can say, commit to, or subsequently generate.

The relation (2.3) is semantic and need not be decidable. It prevents irrelevant hidden state from being mistaken for retained knowledge.

## 2.3 Forgetting as state collapse

Let \(\mathcal C_e\) be the valid learning configurations of \(L_e\). A **forgetting operation** is a computable map

$$
q:\mathcal C_e\longrightarrow\mathcal C_e
\tag{2.4}
$$

for which there are learning-distinguishable configurations \(c_0,c_1\) satisfying

$$
c_0\not\simeq_e c_1,
\qquad
q(c_0)=q(c_1).
\tag{2.5}
$$

The definition excludes harmless compression. If two configurations have identical future learning behaviour, identifying them removes no learning-relevant distinction. Forgetting begins when a behaviourally exposed distinction is collapsed.

**Theorem 2.1 (Forgetting).** A forgetting operation is irreversible from the retained state. There is no computable map \(s\) satisfying

$$
s(q(c))\simeq_e c
\tag{2.6}
$$

for every configuration in any set containing both \(c_0\) and \(c_1\) from (2.5). Consequently, after forgetting, at least one of their continuation trees is absent from internal replay.

**Proof.** Suppose such an \(s\) existed. Since \(q(c_0)=q(c_1)\), the value of \(s\) on both erased configurations would be the same. Equation (2.6) would then make that value behaviourally equivalent to both \(c_0\) and \(c_1\), contradicting \(c_0\not\simeq_e c_1\). \(\square\)

The obstruction is not undecidability. Both configurations may be finite and individually easy to compute. The obstruction is non-injectivity: after (2.5), the retained state contains no fact that selects which preimage was present.

> // **Author's comment.** Infinite time can search forever for a bit that is no longer present. It will not find it.

## 2.4 Boundary-relative branch loss

The Forgetting Theorem is retrospective: it concerns re-entry into the past. Erasure also acts on the future. Two claims must be distinguished. Collapsing states necessarily destroys at least one counterfactual response tree. Destroying every route to a particular target is stronger: it can occur, but does not follow from non-injectivity alone.

**Definition 2.2 (boundary-relative response).** Fix a learner \(L_e\). A **boundary class** \(I\) is a prefix-closed, effectively enumerable set of finite continuations of packets and exogenous replies. It declares which future inputs the environment may supply. Let \(\Omega_e\) be the space of finite public output-and-commit records, and totalize finite execution by adjoining the symbol \(\uparrow\) for divergence. The boundary-relative response tree of \(c\) is the function

$$
\beta_{e,c}^{I}:I\longrightarrow\Omega_e\cup\{\uparrow\},
\qquad
\beta_{e,c}^{I}(\eta)
=
\begin{cases}
\operatorname{out}_e(c,\eta),&\text{if the run completes},\\
\uparrow,&\text{otherwise.}
\end{cases}
\tag{2.7}
$$

Write \(c\simeq_e^I c'\) when \(\beta_{e,c}^{I}=\beta_{e,c'}^{I}\). This coarsens (2.3) by quantifying only over futures admitted by \(I\).

**Theorem 2.3 (branch loss under erasure).** Let \(q:\mathcal C_e\to\mathcal C_e\) be a forgetting operation. If

$$
c_0\not\simeq_e^I c_1,
\qquad
q(c_0)=q(c_1)=\bar c,
\tag{2.8}
$$

then \(\bar c\) is not boundary-equivalent to at least one of \(c_0,c_1\). Consequently the erasing commit destroys at least one of their counterfactual continuation trees relative to \(I\).

**Proof.** If \(\bar c\simeq_e^I c_0\) and \(\bar c\simeq_e^I c_1\), equality of the response functions in (2.7) would give \(c_0\simeq_e^I c_1\), contradicting (2.8). \(\square\)

The theorem concerns labelled responses: it says that the erased state cannot preserve both complete maps from admissible continuations to public records. The same output may nevertheless remain reachable through a different continuation. To say that the learner has lost every route to something requires a declared target.

## 2.5 Target dead ends

**Definition 2.4 (target dead end).** Let \(\mathcal T\subseteq\Omega_e\) be a nonempty decidable set of finite target records. Define

$$
\operatorname{Escape}_{\mathcal T}(e,c,I)
\iff
\exists\eta\in I\;
\bigl[
\operatorname{out}_e(c,\eta)\downarrow
\ \wedge\
\operatorname{out}_e(c,\eta)\in\mathcal T
\bigr],
\tag{2.9}
$$

and

$$
\operatorname{Dead}_{\mathcal T}(e,c,I)
\iff
\neg\operatorname{Escape}_{\mathcal T}(e,c,I).
\tag{2.10}
$$

A forgetting commit \(q\) creates a target dead end at \(c\) when escape is possible from \(c\) but impossible from \(q(c)\). The state may still have many outgoing transitions; it is dead only with respect to \((I,\mathcal T)\).

**Theorem 2.5 (enrichment dead ends; reachable Perfection is path-dependent).** There exist an effective learner \(L_e\), a computable forgetting operation \(q\), a decidable boundary class \(I\), and a fixed finality contract \(\mathfrak F\) such that:

1. before the erasing commit, an admissible continuation installs the unique presentation that is Perfect for \(\mathfrak F\);
2. after the commit, no admissible continuation installs any Perfect presentation.

Thus a single transition can destroy the reachable availability of Perfection without changing whether the fixed contract extensionally contains a Perfect candidate.

**Proof.** Let the learner carry a register \(b\in\{0,1,\bot\}\) while its current presentation is \(P_\bot\). The register is initialized externally but cannot be rewritten by any continuation in \(I\), where \(I\) consists of finite strings of \(\mathsf{recall}\) packets. On \(\mathsf{recall}\), state \(1\) commits to \(P_1\), state \(0\) commits to \(P_0\), and state \(\bot\) makes no such commit. Let \(q\) send both \(0\) and \(1\) to \(\bot\) and fix \(\bot\).

Take

$$
\mathcal Q=\{P_0,P_1,P_\bot\},
\qquad
\mathcal X=\{x\},
\tag{2.11}
$$

with total adequate comparison and losses

$$
L_{P_1}(x)=0,
\qquad
L_{P_0}(x)=L_{P_\bot}(x)=1.
\tag{2.12}
$$

Then \(P_1\) is uniquely Perfect for \(\mathfrak F\). The configurations carrying \(0\) and \(1\) are boundary-distinguishable, while \(q\) identifies them, so \(q\) is a forgetting operation. From the configuration carrying \(1\), the continuation \(\mathsf{recall}\) installs \(P_1\). From the erased configuration carrying \(\bot\), no continuation in \(I\) does. Taking \(\mathcal T\) to be the decidable set of records containing the commit to \(P_1\), the former state satisfies \(\operatorname{Escape}_{\mathcal T}\) and the latter satisfies \(\operatorname{Dead}_{\mathcal T}\). The contract and its Perfect member remain unchanged; only the learner's route to that member has been erased. \(\square\)

The distinction matters when this result is compared with [2, Thm. 7.5]. Existence of a Perfect member in a fixed effective contract is an extensional \(\Sigma^0_2\)-complete question. Availability among the candidates reachable by a particular learner is additionally path-dependent.

**Theorem 2.6 (complexity of target entrapment).** Fix a distinguished public event \(\mathsf{escape}\), and let \(\mathcal T_\star\) be the decidable set of finite records containing it. Over instances \(\langle e,c,I\rangle\) with effectively enumerable boundary class \(I\), define

$$
\mathsf{ESCAPE}_{\star}
=
\bigl\{
\langle e,c,I\rangle:
\operatorname{Escape}_{\mathcal T_\star}(e,c,I)
\bigr\},
\qquad
\mathsf{DEAD}_{\star}
=
\overline{\mathsf{ESCAPE}_{\star}}.
\tag{2.13}
$$

Over any effective instance class containing the construction below,

$$
\mathsf{ESCAPE}_{\star}
\text{ is }\Sigma^0_1\text{-complete},
\qquad
\mathsf{DEAD}_{\star}
\text{ is }\Pi^0_1\text{-complete}.
\tag{2.14}
$$

Every non-dead instance therefore has a finite escape witness. No sound effective finite-certificate procedure is complete for all true instances of target entrapment, although particular instances and restricted subclasses may be certifiable.

**Proof.** Enumerate the continuations in \(I\), dovetail their executions from \(c\), and inspect each completed finite record for \(\mathsf{escape}\). Its appearance is a finite event, so \(\mathsf{ESCAPE}_\star\) is computably enumerable and \(\mathsf{DEAD}_\star\) is co-c.e.

For hardness, given a machine--input pair \((M,w)\), construct a learner that simulates one step of \(M(w)\) on each \(\mathsf{tick}\) packet and emits \(\mathsf{escape}\) exactly when the simulation halts. Let

$$
I_{\mathsf{tick}}
=
\{\mathsf{tick}^n:n\in\mathbb N\}.
\tag{2.15}
$$

This class is decidable and prefix-closed, and

$$
\langle e_{M,w},c_0,I_{\mathsf{tick}}\rangle
\in
\mathsf{ESCAPE}_\star
\iff
M(w)\downarrow.
\tag{2.16}
$$

Thus \(\mathsf{ESCAPE}_\star\) is \(\Sigma^0_1\)-hard and its complement is \(\Pi^0_1\)-hard. A sound and complete finite-certificate procedure for \(\mathsf{DEAD}_\star\) would make that set c.e.; since its complement is already c.e., it would decide a \(\Pi^0_1\)-complete problem. \(\square\)

Escape and entrapment therefore reproduce the halting boundary:

$$
\boxed{
\begin{gathered}
\text{escape has a finite witness and is computably enumerable;}\\
\text{target entrapment is co-c.e. and has no complete}\\
\text{effective finite-certificate procedure.}
\end{gathered}}
\tag{2.17}
$$

The asymmetry inverts the announcement asymmetry of [2, §5.2]. There, completion may be true while a finite certificate remains unavailable, whereas a discovered improvement refutes it. Here a way forward can be witnessed by reaching the declared target, while the absence of every route cannot be uniformly certified. Dovetailed exploration is therefore the uniform semidecision procedure for escape; stopping requires additional structure or a contract-specific certificate.

> // **Author's comment.** This is what the universal machine is *for*. Branches are preserved not because deletion is impolite but because no effective agent can uniformly certify which deletions are fatal.

The result of this section is negative but precise. A learner may destroy a continuation tree by its own transition, may thereby lose every admissible route to Perfection, and cannot uniformly certify all resulting cases of entrapment. The next section introduces the retention discipline that preserves an exit before such a transition is taken.

# 3. Retention and constructive re-entry

The preceding section showed that an active trajectory may erase its only route to a declared target, while no uniform certificate identifies every fatal erasure. The response is to retain a state outside the image of the erasing transition before its importance is known. A ledger does not invert \(q\) from inside \(q(c)\); it preserves enough of the route to reconstruct \(c\) as a separate branch.

$$
\boxed{
\text{the active branch may forget locally, while the universal learner remembers globally.}
}
$$

Replay is therefore an exit retained before the dead end, not information recovered from it.

## 3.1 Ledgers

At step \(t\), the learner retains a self-delimiting record \(a_t\). Its ledger is

$$
E_t
=
a_1a_2\cdots a_t.
\tag{3.1}
$$

The records are append-only. Each record carries enough boundary information to recover its endpoint, so every prefix

$$
E_k=a_1\cdots a_k,
\qquad
k\leq t,
\tag{3.2}
$$

is computable from \((E_t,k)\). The ledger may be lossy: a learner need not retain the raw packet, oracle reply, or realized coin. Section 2 described the consequences of losing such information; Section 4 gives the general replay-conservative remedy.

The evidential and semantic ledgers of [1] remain distinct. The evidential ledger records what entered the learning process and what was publicly produced. The semantic ledger records the executable meanings and commitments currently in force. Replay is grounded in retained evidence; it reconstructs a semantic state rather than allowing that state to rewrite its own evidential history.

## 3.2 Replay-conservativity

The word *conservative* is overloaded in learning theory and in the theory of language extension. I use **replay-conservative** only for the following ledger property.

**Definition 3.1 (replay-conservative learner).** A learner \(L_e\) is replay-conservative when there is a partial computable map \(R_e\), defined on every valid finite ledger of \(L_e\), such that

$$
R_e(c_{e,0},E_t)
\simeq_e
c_{e,t}.
\tag{3.3}
$$

Thus the retained ledger determines the complete learning-relevant state. The definition permits caches and incremental execution. It requires only that their relevant contribution be reconstructible.

A learner is **replay-nonconservative** when no such map exists. Concretely, this occurs when two valid histories induce the same retained ledger but lead to learning-distinguishable configurations.

## 3.3 Prefix replay

**Lemma 3.2 (prefix recovery).** Given a valid self-delimiting ledger \(E_t\) and \(k\leq t\), the prefix \(E_k\) is computable.

**Proof.** Decode records from the beginning of \(E_t\) until the \(k\)th record boundary. Append-only writing ensures that the resulting string is exactly the ledger that existed at stage \(k\). \(\square\)

**Theorem 3.3 (Replay).** Let \(L_e\) be replay-conservative. There is a partial computable operation

$$
\operatorname{Replay}_e(c_{e,0},E_t,k)
\simeq_e
c_{e,k}
\qquad(k\leq t)
\tag{3.4}
$$

defined on every valid finite ledger.

**Proof.** Recover \(E_k\) by Lemma 3.2 and return \(R_e(c_{e,0},E_k)\). Equation (3.3) gives behavioural equivalence with the configuration originally reached at stage \(k\). \(\square\)

Replay is already stronger than a semantic snapshot. A snapshot preserves one configuration in the representation used when it was taken. The ledger records a derivation of that configuration from the declared boundary. If the replay procedure itself is later reimplemented, the derivation remains the public object against which the new implementation can be checked.

## 3.4 Fork

Let \(\eta\) be an effective continuation procedure. It may emit a simulated continuation of packets and replies, connect the reconstructed agent to a new live interaction, or implement a counterfactual intervention. Define

$$
\operatorname{Fork}_e(c_{e,0},E_t,k,\eta)
$$

to allocate a new branch, install

$$
\widehat c_k
=
\operatorname{Replay}_e(c_{e,0},E_t,k),
\tag{3.5}
$$

and continue \(L_e\) from \(\widehat c_k\) under \(\eta\).

**Theorem 3.4 (Replay--Fork).** Every finite itinerary position of a replay-conservative learner is constructively re-enterable. More precisely, for every valid \(E_t\), every \(k\leq t\), and every effective finite continuation \(\eta\), the forked branch reproduces the public behaviour that \(L_e\) would produce by receiving \(\eta\) from its original stage-\(k\) configuration.

**Proof.** Theorem 3.3 returns a configuration behaviourally equivalent to \(c_{e,k}\). Behavioural equivalence is defined by agreement on every finite continuation, so running \(\eta\) produces the same public outputs and commits. Each replay and each finite continuation consists of finitely many terminating computations, hence completes in finite time. \(\square\)

The theorem creates a reverse edge in the internal reachability graph: from a later universal-machine state one may allocate a branch rooted at an earlier learning state. It does not reduce the accumulated work counter. Under a finite budget, replay may be unaffordable and its cost must be charged. Under the unbounded machine used for the existence theorem, finite cost affects delay but not reachability.

For interactive systems, the re-entry is equally exact but differently interpreted. The learner's earlier internal state is recovered. The external world is not. A fork that requires the earlier world must use a recorded simulator, a restorable environment, or a new experiment. The absence of such an apparatus is a reference-resource limitation, not a failure of internal replay.

# 4. Conservatization

Section 2 established the hazard, and Section 3 gave a sufficient architecture for retaining exits from it. The remaining question is whether replay-conservativity excludes forward behaviours available to an ordinary effective learner. In the unbounded model it does not: every effective learner can be realized with enough retained evidence to reconstruct each finite state.

## 4.1 The full execution ledger

Let \(L_e\) be any effective learner of the form (2.2). Define its full record at step \(t\) by

$$
a_t^\dagger
=
\langle y_t,r_t\rangle,
\qquad
E_t^\dagger
=
a_1^\dagger\cdots a_t^\dagger.
\tag{4.1}
$$

The record includes every exogenous finite input that affected the transition. The learner \(L_e^\dagger\) carries the same current simulated configuration as \(L_e\), emits the same public output, makes the same commits, and additionally appends \(a_t^\dagger\).

**Theorem 4.1 (Conservatization).** For every effective learner \(L_e\), there is a replay-conservative learner \(L_e^\dagger\) such that, on every stream of packets and exogenous replies:

1. \(L_e\) and \(L_e^\dagger\) have identical public outputs and commit itineraries step by step;
2. every forward configuration reached by \(L_e\) has a behaviourally equivalent configuration reached by \(L_e^\dagger\);
3. every finite configuration of \(L_e^\dagger\) is replayable and forkable;
4. the additional current-run work is the work of encoding and appending the full record, while replay of stage \(k\) costs at most a fresh simulation of the first \(k\) transitions plus decoding overhead.

**Proof.** On the current run, \(L_e^\dagger\) executes the transition of \(L_e\) and carries its resulting state incrementally. Hence the public outputs and commits agree exactly. Given \((e,c_{e,0},E_t^\dagger)\), reconstruct \(c_{e,t}\) by simulating \(T_e\) from the initial configuration on the recorded pairs \(\langle y_s,r_s\rangle\) for \(s\leq t\). Every transition on the valid recorded trajectory halts, so the reconstruction is finite. This supplies the replay map required by Definition 3.1. The cost statements follow from the construction. \(\square\)

Conservatization does not claim equal bounded accessibility. If ledger storage, write bandwidth, replay time, or privacy is charged, \(L_e^\dagger\) may exceed a budget that \(L_e\) satisfies. The theorem says that no forward learning itinerary is available only through forgetting when unbounded effective resources determine reachability. Resource-bounded differences remain real and belong in the charged realization.

## 4.2 Minimal sufficient ledgers

The raw ledger in (4.1) is sufficient but rarely minimal. A retention map \(\sigma\) may compress the history while preserving replay whenever

$$
\sigma(h)=\sigma(h')
\Longrightarrow
c(h)\simeq_e c(h').
\tag{4.2}
$$

Condition (4.2) says that every fibre of \(\sigma\) lies inside one behavioural-equivalence class. It is the exact boundary between compression and forgetting.

**Proposition 4.2 (ledger sufficiency).** A computable retention map supports replay precisely when the behavioural state induced by every valid history is a computable function of the retained ledger. If (4.2) fails, the map performs learning erasure; if it holds but no reconstruction is computable, the information is retained extensionally but not operationally replayable by the learner.

The last distinction parallels the separation between generative addressability and operational accessibility in [1]. A state may be determined by the ledger yet remain too costly for a bounded agent to reconstruct.

# 5. The Universal Language Learning Machine

Replay-conservativity preserves the exits of one learner, and conservatization shows that doing so need not alter its forward behaviour. Universality now asks for one effective machine that retains the replayable itineraries of every effective learner without forcing their incompatible commits into a single trajectory.

## 5.1 Universality over branches

Fix an acceptable effective enumeration

$$
L_0,L_1,L_2,\ldots
\tag{5.1}
$$

of packet-driven learners, together with their conservatizations from Theorem 4.1. An index includes the initial presentation, transition procedure, retention rule, and public boundary. Randomized learners appear through their logged reply streams.

The **Universal Language Learning Machine**, written \(\mathbb U\), maintains one master evidential ledger and a computably enumerable tree of simulation branches. A branch address contains at least

$$
b=\langle e,c_{e,0},\zeta\rangle,
\tag{5.2}
$$

where \(e\) is a learner index and \(\zeta\) specifies any branch-local exogenous replies not already fixed by the common ledger. At universal stage \(s\), \(\mathbb U\) dovetails the first \(s\) simulation tasks for \(s\) steps each. A diverging transition delays only its own branch.

The machine records a node whenever a simulated learner completes a finite transition. Each node contains the branch address, ledger prefix, simulated configuration, public output, and commit edge. Its append-only master ledger also records branch allocations, incoming packets and replies, and the current universal stage. Together with the fixed dovetail schedule, this is enough to reconstruct partially executed as well as completed branch computations. Replay may allocate a new node at an earlier prefix; fork attaches an effective continuation beneath it.

Universality is therefore not the assertion that one public output equals the outputs of all learners. Incompatible learners occupy incompatible branches. A separate selector may make one branch active for external action, but selection does not delete the others.

## 5.2 The universality theorem

**Theorem 5.1 (Universal Language Learning Machine).** There exists a replay-conservative effective machine \(\mathbb U\) such that, for every effective learner \(L_e\):

1. **Branch simulation.** For every valid finite trajectory of \(L_e\), some branch of \(\mathbb U\) eventually contains a behaviourally identical trajectory.
2. **Embedding with retraction.** There are computable branch maps \(\iota_e\) and \(\rho_e\) satisfying

   $$
   \rho_e\circ\iota_e
   =
   \operatorname{id}
   \tag{5.3}
   $$

   on the learning-relevant configurations of the conservatized learner \(L_e^\dagger\).
3. **Replay and fork preservation.** The embedding sends retained prefixes to retained prefixes, replay to replay, and effective continuations to forked continuations.
4. **Self-inclusion.** Since \(\mathbb U\) is effective, it has an index \(u\) in (5.1), and its behaviour appears on branch \(u\).

**Proof.** The universal interpreter enumerates branch addresses and dovetails their transition simulations. For any completed finite trajectory of \(L_e\), all of its finitely many computations eventually receive enough universal stages to halt, so the corresponding nodes enter the tree. Map a configuration of \(L_e^\dagger\) to its branch node, including the learner index and full ledger prefix. The retraction reads the simulated configuration from that node, giving (5.3). Because the ledger prefix and index are retained, Theorem 3.3 is available within the branch, and the universal scheduler can enumerate every effective continuation. Finally, the current universal stage and every exogenous input are retained. The complete finite master state is therefore computable by rerunning the fixed dovetail schedule to that stage, so \(\mathbb U\) is replay-conservative. Self-inclusion follows from the enumeration. \(\square\)

The theorem covers nonconservative learners through their behaviourally equivalent conservatizations. It does not claim that the original lossy ledger becomes replayable. The universal branch retains the fuller ledger required to represent that learner without erasure.

## 5.3 Nonconservative hosts

Let \(\mathbb U\) be a replay-fork machine and \(M\) a host learner. A faithful implementation of a family \(C\) of \(\mathbb U\)-configurations consists of computable maps

$$
\iota:C\longrightarrow\mathcal C_M,
\qquad
\rho:\mathcal C_M\longrightarrow C,
\qquad
\rho\circ\iota=\operatorname{id}_C,
\tag{5.4}
$$

which preserve public transitions, replay, and fork. The retraction makes the representation faithful: distinct learning states of \(\mathbb U\) remain recoverable inside \(M\).

**Corollary 5.2 (nonconservative implementation dichotomy).** Suppose a replay-nonconservative learner \(M\) is capable of implementing \(\mathbb U\).

1. If the implementation remains faithful, the image \(\iota(C)\) forms a replay-conservative subsystem of \(M\), even if other parts of \(M\) are nonconservative.
2. If a host operation \(q\) identifies the images of two learning-distinguishable \(\mathbb U\)-configurations, then no retraction exists after \(q\). The operation is irreversible learning erasure, and the resulting host no longer implements the full replay-fork structure of \(\mathbb U\).

**Proof.** In the first case, replay in \(\mathbb U\), followed by \(\iota\), reconstructs every configuration in the implementation image. In the second, if \(q(\iota(c_0))=q(\iota(c_1))\) for distinguishable \(c_0,c_1\), any post-erasure retraction would assign one value to the common host state and could not recover both. This is Theorem 2.1 applied through the embedding. \(\square\)

Thus every nonconservative learner capable of hosting the universal learner faces an exact choice: externalize a conservative record for the universal subsystem, or implement forgetting as irreversible erasure of a learning path.

Recovery from another copy, a backup, or a renewed observation does not contradict the theorem. It supplies information outside the erased state. The recovery mechanism is itself the conservative record that the original state lacked.

## 5.4 Canonicity

Let \(\mathbb U\) and \(\mathbb U'\) use acceptable enumerations of the same effective learner class. A compiler from one enumeration to the other maps each learner index to an index with the same public behaviour. Applying the universal construction branchwise gives mutual computable embeddings.

**Corollary 5.3 (canonicity up to translation).** Any two Universal Language Learning Machines for the same effective learner class simulate each other's branches through computable translations.

This is deliberately weaker than isomorphism of the entire itinerary trees. Different machines may duplicate branches, use different padding, or schedule the same simulations in different orders. Universality supplies a canonical capacity, not a unique concrete tree.

# 6. The cost of universality

Universality as reachability uses unbounded time. A finite agent still needs to know what the universal schedule charges for a branch.

## 6.1 Weighted dovetailing

Let \(g\) be an effectively given rational proposal law over prefix-free branch addresses with

$$
g(b)>0,
\qquad
\sum_b g(b)\leq1.
\tag{6.1}
$$

Choose a weighted dovetail schedule that gives branch \(b\) at least a constant fraction of \(g(b)\) of the available simulation work. Let \(T_b(n)\) be the universal-interpreter work required to complete the first \(n\) local steps of that branch when run without competition, including interpretation and logging.

**Theorem 6.1 (surprisal price).** There is a constant \(c\), independent of \(b\) and \(n\), such that the weighted universal schedule completes the first \(n\) steps of branch \(b\) within work

$$
T_{\mathbb U}(b,n)
\leq
\frac{c}{g(b)}
\bigl(T_b(n)+1\bigr).
\tag{6.2}
$$

Consequently,

$$
\log_2 T_{\mathbb U}(b,n)
\leq
\log_2\bigl(T_b(n)+1\bigr)
-
\log_2 g(b)
+O(1).
\tag{6.3}
$$

**Proof.** Weighted dovetailing assigns branch \(b\) one unit of simulation work in at most \(c/g(b)\) units of master work. Repeating this allocation for the \(T_b(n)\) work units required by the branch gives (6.2); taking logarithms gives (6.3). \(\square\)

The additive universal price is therefore the surprisal

$$
I_g(b)
=
-\log_2g(b).
\tag{6.4}
$$

For the prefix prior \(g(b)=2^{-|b|}\), this becomes description length. For a task-adapted proposal law it need not. The equality between address length and search price is a property of the chosen universal schedule, not of arbitrary bounded proposal procedures.

## 6.2 Itinerary weights

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
\tag{6.5}
$$

and its scheduling charge is

$$
I_g(h)
=
-\log_2g(h)
=
\sum_{k=1}^m
-\log_2g(a_k\mid h_{<k}).
\tag{6.6}
$$

Thus the universal price of an itinerary is the cumulative surprise of the language changes required to reach it. Replay affects this price in a precise way: revisiting a retained prefix requires work, but it does not require proposing the prefix again. A fork pays only for the new continuation plus replay cost.

# 7. Relative universality

## 7.1 Oracle-relative machines

Let \(R\) be an installed oracle or, more generally, the effective code of the computational and reference operations available to the learner. An \(R\)-effective learner may query \(R\) during its transitions. Repeating the construction with an oracle universal interpreter gives \(\mathbb U^R\).

**Theorem 7.1 (relative universality).** For every oracle \(R\):

1. \(\mathbb U^R\) embeds every \(R\)-effective learner as a replayable branch.
2. There is an \(R'\)-effective learner whose public behaviour is not behaviourally equivalent to any \(R\)-effective learner.
3. Hence \(\mathbb U^R\) is not universal for the \(R'\)-effective learner class, while \(\mathbb U^{R'}\) is.

**Proof.** The first claim relativizes the dovetailing proof of Theorem 5.1. For the second, let a learner receive an index \(n\) and emit the bit deciding whether the \(n\)th \(R\)-oracle program halts. This behaviour is computable from \(R'\). If an \(R\)-effective learner had the same behaviour on every input, it would decide the \(R\)-halting problem, contradicting the jump theorem. The third claim follows. \(\square\)

Define

$$
\mathbb U^R
\preccurlyeq
\mathbb U^S
$$

when every \(R\)-effective branch is computably translatable into an \(S\)-effective branch. If \(R\leq_T S\), then \(\mathbb U^R\preccurlyeq\mathbb U^S\).

**Corollary 7.2 (no greatest universal learner).** The oracle-indexed extension order has no greatest element. For every \(\mathbb U^R\), the machine \(\mathbb U^{R'}\) realizes a strictly larger class of effective boundary behaviours.

This is the constructive companion to the Omnipotence Theorem of [2]. *Perfect Theory* shows that granting \(R\) moves the next completion problem to \(R'\). The present theorem supplies the corresponding learner: \(\mathbb U^{R'}\) is universal for the enlarged effective class. No claim of cofinality for the finite jump sequence is required; the construction applies separately above every oracle base.

# 8. Itineraries, selection, and completion

## 8.1 A tree, not a posterior state

Nonconservative language changes need not commute. Starting from one presentation, commits \(a\) then \(b\) may produce a different presentation from commits \(b\) then \(a\). The Universal Language Learning Machine therefore retains nodes of the form

$$
(P,h,E),
\tag{8.1}
$$

not merely the terminal presentation \(P\). Two branches reaching extensionally equivalent presentations may still differ in their retained evidence, available retractions, or future proposal laws.

Replay does not collapse these paths. It makes them separately accessible. If two paths are later proved behaviourally equivalent for the declared task, they may be compressed into one node without forgetting by Proposition 4.2. Without that proof, merging them risks the erasure identified by Theorem 2.1.

## 8.2 Selection

The universal tree describes what the machine can continue. It does not by itself decide what the agent should execute in the external world. Let

$$
\chi(E,T)
$$

be a selector that chooses an active branch from ledger \(E\) and current universal tree \(T\). The selector may use posterior risk, expected improvement, verification status, accessibility, reversibility, or the value of further information. It is itself an effective learner and therefore appears as a branch of \(\mathbb U\).

Separating enumeration from selection avoids a false notion of universality. A single action cannot equal every incompatible action proposed by every learner. Universality means that the alternatives and their routes remain representable and recoverable before the selector commits.

## 8.3 Local Done and global openness

A universal learner may certify local completion. An active branch can be Good, Final, or Perfect under a declared finality contract, and a sound certificate may license calling that branch Done [2]. Universality does not invalidate the certificate.

What universality forbids is a silent change of quantifiers. A certificate for one candidate class, target domain, comparison structure, and resource base does not close the full extension tree. New branches may change any of those components. Determining that no universal branch ever produces an accepted improvement is again a completion problem, not a consequence of running the universal machine for a long time.

The two statements are compatible:

$$
\boxed{
\begin{gathered}
\text{a branch may be Done under a fixed contract,}\\
\text{while the universal extension process remains open.}
\end{gathered}}
\tag{8.2}
$$

Under a contract whose admissible successors include oracle extensions and whose objective rewards strict increases in simulation coverage, Corollary 7.2 supplies a better successor above every resource base. Such a contract has no Final universal learner. Other contracts may close. The distinction is the same contract-relativity that governs Perfection throughout [2].

# 9. Relation and scope

## 9.1 Universal computation and search

The universal interpreter descends from Turing's universal machine [3] and the theory of acceptable programming systems [4]. Mutual translation between universal machines is standard; the new object here is the preserved tree of language-changing itineraries and the replay/fork structure carried by its ledger.

Weighted dovetailing follows universal search [5]. Equation (6.3) separates two costs that are often merged: the cost of simulating a branch once addressed, and the surprisal cost of allocating search mass to its address. This is the universal-schedule case of the broader accessibility distinction in [1].

## 9.2 Learning in the limit and retained memory

Gold's model identifies languages from streams of data [6]. Iterative and bounded-example-memory learners restrict what earlier evidence remains directly available [7,8]. The present paper asks a different but adjacent question: which earlier *learning configurations* remain constructively accessible after the learner is allowed to revise its presentation itself?

The Conservatization Theorem uses unbounded storage and time to establish an extensional result. It does not collapse the bounded-memory hierarchies. When storage is charged, forgetting may improve performance within one budget even though it destroys replay reachability. The choice is then economic rather than logical, and the erased path cannot later be recovered without another copy.

## 9.3 Self-modifying machines

Gödel machines perform self-rewrites after proving, relative to an initial axiomatic description of utility and hardware, that the rewrite is useful [9]. A Universal Language Learning Machine does not require every branch to be proof-gated. It records proof-gated learners, experimental learners, Bayesian selectors, and arbitrary effective self-modifiers as separate branches. Verification affects which branch a selector should trust; it does not determine which branches are representable.

The difference is not that proof is dispensable. Proof-carrying commits may be essential for safe external action. The difference is architectural: the universal tree retains unselected and currently unjustified continuations without executing them as the active presentation.

## 9.4 Scope conditions

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
10. Target dead ends are relative to a declared boundary class and a decidable set of finite target records. A boundary that re-supplies the erased information may reopen the branch. The complexity theorem concerns effective instance classes containing its stated reduction; particular dead ends and restricted subclasses may still be certifiable.

# 10. Conclusion

A universal language learner must preserve more than a menu of hypotheses. When language changes are path-dependent, the route to a presentation determines which evidence, meanings, and future continuations remain available. The appropriate universal object is therefore a replayable tree of itineraries.

For a replay-conservative learner, every retained finite state can be reconstructed and used as a new branch. For a replay-nonconservative learner, identifying two behaviourally distinct states is irreversible learning erasure. Infinite computation does not repair the loss because the erased state no longer contains the distinction to be computed. The loss is not only retrospective: relative to boundaries that do not re-teach what was discarded, erasure necessarily destroys a counterfactual continuation tree and can remove every reachable route to a Perfect presentation. Escape has finite witnesses, but target entrapment has no sound effective finite-certificate procedure complete for all instances. The universal construction answers this hazard by retaining the branches before their importance is known. Every effective learner nevertheless has a replay-conservative realization when the full finite causes of its transitions are logged.

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
\tag{10.1}
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
