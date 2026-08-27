---
title: "On Learning Languages"
subtitle: "Bayesian Updating of Epistemic Theories and the Meta-Complexity of Representational Choice"
date: "25 August 2026 — Revised Draft v32"
lang: en
---

# Abstract

Learning theory usually fixes a hypothesis language and studies inference within it. But agents can also learn by changing the language in which hypotheses are formed. I model this process as Bayesian updating over candidate language presentations and the bounded procedures that search and verify within them. A presentation specifies a language, a partial map by which opaque internal encodings become expressions in that language, and an interpreter that runs expressions to produce further expressions. Candidates receive the same opaque packets but construct their likelihoods through their own expressions and generative theories. I also extend the comparison to phase-sensitive reference operations, which can distinguish presentation states that every block-diagonal classical comparison identifies, but only when the required reference resources are available. Finally, I instantiate the generative layer using presentation-relative resource-bounded Kolmogorov complexity, \(\mathrm{KT}\). Within the resulting decidable syntactic class, comparing two presentations on any fixed finite target is decidable, while deciding whether one dominates the other on every finite target is \(\Pi^0_1\)-complete.

This paper is the first in a trilogy. Its two extensions, *Perfect Theory* [1] and *Universal Language Learning Machine* [53], ask, respectively, when a language-learning process may stop and call a theory complete, and what such a machine must preserve to remain universal over its possible continuations.

\tableofcontents

# 1. Introduction: The problem of language expressiveness

Asymptotic analyses of universal computation and description length often suppress additive constants and translation costs. In the real world, under finite resource bounds, those costs may determine whether a representation is accessible at all. Universal encodings allow agents to exchange the same bytes in principle, but they do not make the compiler, interpreter, search, or verification required to use those bytes free. Put simply, universality guarantees transmissibility, not practical intelligibility.

Hence, the analysis in this paper is deliberately agent-relative. When analysing languages and their representations, I ask not only whether a representation exists or whether two languages are equivalent in principle, but what a finite agent can express, construct, run, and verify with the resources available to it. For an unbounded observer, the difference may disappear into a constant; for a bounded agent, life is too short to follow every impractical idealisation [7–10,45].

## 1.1 Semantic occlusion

Agents often encounter phenomena they cannot yet represent or express. Languages do not all make the same distinctions available. If we reach for real-world examples, Pirahã has no general system of exact number words, while languages also differ in whether they use an absolute spatial frame of reference as a basic way of describing location [37–40]. Such differences affect what speakers can encode, preserve, and recover.

Scientific languages also reach their limits. Greek mathematicians encountered incommensurable magnitudes before those magnitudes had a settled theory. Sixteenth-century algebraists manipulated square roots of negative numbers while solving cubic equations before complex numbers had a stable interpretation [47]. Most readers know a more ordinary version of the problem from learning a second language: searching for words to say what one already means.

While these cases are not identical, they admit a shared formal description. The problem is not simply uncertainty about which statement is true within a fixed language. In each case, the current language or theory lacks a distinction, object, or operation required to represent the phenomenon in question. Yet these limits move. Individuals learn new languages, communities develop new concepts, and scientific theories acquire new objects and operations.

I call the phenomenon of being unable to express a concept in one's current language **semantic occlusion**. This can happen for various reasons. To examine its nature more closely, I first distinguish the external generator, the apparatus through which an agent observes it, the language in which an observation becomes available, and the operations that can be performed once an expression has been formed. The decomposition resembles a communication system, but the question here is semantic rather than merely transmissive: receiving a signal does not by itself supply a language in which its significance can be expressed [43,44].

Let \(G_*\) denote an external generator, and let \(\mathcal S_o\) be the signal space of observation interface \(o\). In an observational context \(z_n\), the generator produces a signal

$$
s_n\sim G_*(\cdot\mid z_n),
\qquad
s_n\in\mathcal S_o.
\tag{1.1}
$$

An encoder

$$
E_o:\mathcal S_o\longrightarrow T_o
$$

belonging to the observation apparatus converts this signal into an internal state

$$
\tau_n=E_o(s_n)\in T_o.
\tag{1.2}
$$

The carrier \(T_o\) is deliberately left opaque. Its elements may be implemented as perceptual features, activation patterns, tokens, or some other internal structure. They are not linguistic objects, and the agent cannot inspect or manipulate them directly.

A presentation \(P_e\) supplies a language \(\mathcal L_e\) and a partial linguistic map

$$
D_e:T_o\rightharpoonup\mathcal E_e,
\qquad
\mathcal E_e:=\operatorname{Expr}(\mathcal L_e).
\tag{1.3}
$$

When \(D_e\) is defined at \(\tau_n\), it produces an expression

$$
\varphi_{e,n}=D_e(\tau_n)\in\mathcal E_e.
\tag{1.4}
$$

This expression, rather than the opaque internal state \(\tau_n\), is available to the agent. The presentation also supplies an interpreter

$$
U_e:\mathcal E_e\rightharpoonup\mathcal E_e^{<\omega},
\tag{1.5}
$$

which runs an expression and produces a finite sequence of further expressions in the same language. Whenever \(U_e\) is applied to a finite sequence, I mean pointwise application, wherever defined, followed by concatenation of the resulting sequences. Its outputs may therefore be supplied to \(U_e\) again, producing an internal generative cycle:

$$
\varphi
\xrightarrow{U_e}
\psi_1,\psi_2,\ldots
\xrightarrow{U_e}
\chi_1,\chi_2,\ldots .
\tag{1.6}
$$

The complete path is therefore

$$
G_*
\longrightarrow s_n
\xrightarrow{E_o}\tau_n
\xrightarrow{D_e}\varphi_{e,n}
\xrightarrow{U_e}\psi_1,\psi_2,\ldots .
\tag{1.7}
$$

The first two stages belong to the observational interface. The agent's linguistic operations begin only once \(D_e\) has produced an expression.

Semantic occlusion can now be located within this process. It may occur at the linguistic boundary because the decoding produces no expression. It may also occur because the transmission from the opaque internal state to the language is lossy. In this paper, I consider only losses that affect the construction of a generative theory. Other forms of loss may occur, but they lie outside the present model.

Occlusion may also occur after a fully valid expression has been formed. The agent interprets that expression through \(U_e\), thereby generating further expressions. These are compared with expressions formed from subsequent signals produced by the external generator. A divergence between the two linguistic sequences indicates that the current presentation lacks an adequate generative theory.

There is a further, operational case. A suitable generative theory may be expressible in the current language, yet the agent may be unable to find and certify it. The failure then lies neither in decoding the signal nor in the expressive resources of the language, but in the agent's proposal and verification procedures under the available budgets.

The external generator need not change when the agent learns a language.

The learning of a language can therefore be described as the construction of progressively richer presentations. Here, by a presentation I mean the triple

$$
P_e=(\mathcal L_e,D_e,U_e),
\tag{1.8}
$$

consisting of a language \(\mathcal L_e\), a linguistic map \(D_e\) from opaque internal encodings to expressions in that language, and an interpreter \(U_e\) that runs those expressions and produces further expressions. Under a **conservative enrichment**—one that preserves the expressions and generative behaviour already available (§3.4)—and for a fixed apparatus and task, a more expressive presentation leaves fewer encounters occluded; conversely, resolving an occlusion enriches the presentation available to the agent. Nonconservative changes need not be monotone: they may acquire some distinctions while losing others.

I intentionally distinguish semantic occlusion from ordinary uncertainty about the world or about a theory. Once an agent has obtained an interpretable expression and formulated competing generative theories within a common observation space, it can use differences in their predictions to select among them. Statistical and Bayesian inference [2–4], together with causal inference in Pearl's framework [42], study this problem extensively. The problem considered here arises earlier: the agent does not yet possess the linguistic or theoretical resources required to formulate the relevant alternatives.

I therefore distinguish:

1. **World/encoding uncertainty:** the relevant variables are represented, but their values remain uncertain because of variation in the external process, signal noise, or loss during encoding.
2. **Theory uncertainty:** several represented generative theories compete within a common observation space.
3. **Semantic occlusion:** the internal encoding yields no interpretable expression, or the resulting expression reveals a failure of generative theory that the agent cannot represent or resolve.

$$
\boxed{
\text{world or encoding uncertainty}
\neq
\text{theory uncertainty}
\neq
\text{semantic occlusion}.
}
\tag{1.9}
$$

## 1.2 Extensional and operational occlusion

The preceding cycle reveals three sites at which an agent may fail:

| Site | Failure |
|---|---|
| Linguistic boundary | \(D_e\) produces no expression, or the map is lossy in a way that obstructs generative-theory construction. |
| Generative expressivity | A valid expression is formed, but no \(q\in\mathcal E_e\) yields an adequate generative theory under \(U_e\). |
| Operational accessibility | Such a \(q\) exists, but the agent cannot find and certify it within the available budgets. |

The two linguistic-boundary cases distinguished above—undefined decoding and generatively relevant loss—occupy the first site. Failure after a valid expression has been formed occupies the second. Failure to find or certify an expressible theory occupies the third.

The first two are **extensional** relative to the presentation: the required expression or generative theory is absent from what the presentation can supply, irrespective of how search is organized. The third is **operational** relative to the bounded agent: the required theory exists in the presentation but is not accessible through the agent's proposal and verification procedures. These categories are presentation- and task-relative. A theory may be adequate for one family of future signals and inadequate for another; a generative expression may be accessible under one proposal law and effectively absent under another.

The distinction between failure at \(D_e\) and failure under \(U_e\) matters. In the first case the agent has no adequate linguistic object with which to begin. In the second it possesses an expression of the observation, can run its current theory, and can detect a divergence between internally generated expressions and expressions formed from later signals. The divergence does not by itself provide the missing theory. It exposes a demand on the language: construct a presentation in which the sequence becomes generatively addressable in the sense defined in §2.2.

This gives the central problem of the paper. How can a bounded agent compare candidate presentations using a shared observation when the candidates may decode and interpret that observation differently? And what can such a comparison establish about which presentation should be retained? The construction requires packet-level evidential commensurability: candidates may form different, mutually untranslated expressions from the same opaque packet and remain comparable because their likelihoods are defined on a shared packet space. This contrasts with prior linguistic commensurability, which would require the candidates to share expressions or translations before comparison. Sections 2–5 give a typed classical construction: candidate presentations receive the same opaque packet, form their own linguistic expressions, generate further expressions internally, and update their weights at the common evidential boundary. Section 6 extends the comparison to phase-sensitive reference structures. Sections 7 and 8 isolate the generative layer in resource-bounded Kolmogorov complexity. Every fixed finite comparison is decidable there, while uniform dominance over all targets is \(\Pi^0_1\)-complete.

# 2. Language presentations for bounded agents

Unless a section says otherwise, all measurable spaces are standard Borel, candidate families are countable, kernels are Markov, and the displayed maps have the stated measurability or computability properties. Sections 1–5 are classical. Phase-sensitive operator-algebraic structure enters in Section 6.

## 2.1 Presentations and bounded realizations

The unit of representational choice is the language presentation already introduced in (1.8):

$$
P_e=(\mathcal L_e,D_e,U_e).
\tag{2.1}
$$

The language \(\mathcal L_e\) contains its alphabet, grammar, and well-formed expressions \(\mathcal E_e\). The partial map \(D_e:T_o\rightharpoonup\mathcal E_e\) supplies the linguistic boundary. The interpreter \(U_e\) supplies the internal generative operation. Public contexts and finite linguistic histories may be encoded as expressions; when they matter I write \(U_e(q;h,z)\), suppressing these arguments otherwise.

A language is not identical to the bounded procedures through which an agent searches and verifies within it. I write

$$
\mathcal B_{e,a}
=
\bigl(P_e,V_{e,a},\Lambda_{e,a}\bigr)
\tag{2.2}
$$

for bounded realization \(a\) of presentation \(P_e\). Here \(\Lambda_{e,a}\) is a proposal law over finite derivation trajectories, and \(V_{e,a}\) checks finite certificates produced by those trajectories. Two agents—or two realizations belonging to the same agent—may therefore possess the same presentation but differ in what theories they can discover and certify. When a single realization is fixed, I suppress \(a\) and write \(\mathcal B_e\), \(V_e\), and \(\Lambda_e\).

I do not assume that presentations are universal. Bounded agents ordinarily inhabit non-universal presentations. Universality is useful as a coding theorem; however, it does not make the relevant compiler or program available to an agent with a finite budget.

## 2.2 Generative addressability

For \(q\in\mathcal E_e\) and fixed \(h,z\), let \(\operatorname{Cl}_{U_e}(q;h,z)\) be the least set containing \(q\) such that, whenever \(\psi\) belongs to the set and \(U_e(\psi;h,z)\) is defined, every expression in the resulting finite sequence also belongs to the set. The history \(h\) and context \(z\) remain fixed throughout this closure. Searches in which the history changes along a trajectory belong to the bounded realization and are represented by \(\Lambda_{e,a}\).

The closure is deliberately unbudgeted: it records what can be obtained through some finite iteration of the interpreter, independently of whether a particular agent can find that iteration within its resources.

Expressions written in different languages need not be literally equal. A declared task therefore supplies a partial public readout

$$
R_{e,o}:\mathcal E_e\rightharpoonup\mathcal X_o,
\tag{2.3}
$$

where \(\mathcal X_o\) is a common, effectively encoded comparison domain. The readout is relative to the declared task and interface. If \(R_{e,o}\) is undefined at an expression, that expression is incomparable for the present task; it is not thereby false or malformed. In the computational specialization of §§7–8, \(R_{e,o}\) is partial computable and the supplied target encodings are effective.

The readout does not expose the opaque carrier \(T_o\), nor does it impose a universal semantics. It records only enough shared structure to ask whether two presentations have produced the same declared target.

A target \(x\in\mathcal X_o\) is **generatively addressable** in presentation \(e\) when

$$
\operatorname{Gen}_e(x\mid h,z)
\iff
\exists q,\psi\in\mathcal E_e\;
\bigl[
\psi\in\operatorname{Cl}_{U_e}(q;h,z)
\ \wedge\
R_{e,o}(\psi)=x
\bigr].
\tag{2.4}
$$

The quantifier over \(q\) is deliberately unrestricted. Thus \(\operatorname{Gen}_e\) measures the extensional competence of the presentation, including generative seeds that a particular bounded agent may never discover. Situated access to such a seed is measured separately by \(\mathsf A_{\mathcal B_{e,a}}^B\).

This is not the same as successful perceptual decoding. The map \(D_e\) determines whether an observation becomes an expression. Generative addressability asks what the presentation can subsequently produce from expressions available within it.

## 2.3 Description length and accessibility

I fix the task readout \(R_{e,o}\) and omit it from the notation below. Let \(\ell_e(q)\) be the length of an expression in the code of \(\mathcal L_e\). The presentation-relative description length of a target is

$$
\mathsf K_{P_e}(x\mid h,z)
=
\min\left\{
\ell_e(q):
\exists\psi\in\operatorname{Cl}_{U_e}(q;h,z),
\ R_{e,o}(\psi)=x
\right\},
\tag{2.5}
$$

with value \(\infty\) when the set is empty.

For a bounded realization \(\mathcal B_{e,a}\), let \(B\) be a finite resource vector limiting such quantities as proposal count, derivation work, and verification work. The law \(\Lambda_{e,a}^B\) is the distribution over finite trajectories induced by stopping the proposer at those limits. A successful trajectory contains a proposed seed, a finite \(U_e\)-derivation, and a certificate accepted by \(V_{e,a}\) that the resulting expression has readout \(x\). Define

$$
\mathsf A_{\mathcal B_{e,a}}^B(x\mid h,z)
=-
\log_2
\Pr_{\gamma\sim\Lambda_{e,a}^B(\cdot\mid h,z)}
\!\left[
V_{e,a}(\gamma,x)=1
\right],
\tag{2.6}
$$

where \(-\log_2 0:=\infty\). Under independent repetitions of the same budgeted search, \(2^{\mathsf A_{\mathcal B_{e,a}}^B}\) is the expected number of runs required to obtain the first certified success.

The quantities answer different questions:

| Notion | Question for a finite agent |
|---|---|
| Generative addressability | Does an adequate generative expression exist in this presentation? |
| Description | How short can such an expression be? |
| Accessibility | Can this proposer find and certify one within budget \(B\)? |

Assuming that \(V_{e,a}\) is sound,

$$
\mathsf A_{\mathcal B_{e,a}}^B(x\mid h,z)<\infty
\ \Longrightarrow\
\mathsf K_{P_e}(x\mid h,z)<\infty
\ \Longleftrightarrow\
\operatorname{Gen}_e(x\mid h,z).
\tag{2.6a}
$$

The reverse of the first implication need not hold: an adequate expression may exist in the presentation while remaining inaccessible to the bounded realization. This is precisely the third site of semantic occlusion identified in §1.2.

A target may be addressable only through a long expression; it may have a short expression that the agent's proposal law never finds; or it may not be generatively addressable at all. When budgets are nested and later searches retain earlier discoveries, \(\mathsf A_{\mathcal B_{e,a}}^B\) is nonincreasing in \(B\). No general identification of \(\mathsf K_{P_e}\) with \(\mathsf A_{\mathcal B_{e,a}}^B\) is available. Levin search couples length and runtime under a particular universal schedule [8]; an arbitrary bounded apparatus does not inherit that guarantee.

## 2.4 Presentation costs under finite budgets

A language with a primitive for every target would trivialize description length. I therefore charge for the presentation itself. Let \(W\) denote the agent's current epistemic theory, defined formally in §3, and suppose its current presentation is \(P_{e_0}\). When the argument of \(\mathsf K_{P_{e_0}}\) is a finitely specified presentation, readout, verifier, or proposal procedure rather than an ordinary task target, the notation refers to the same description construction under a declared effective meta-level readout for such finite objects; it does not introduce a universal reference machine.

For a finite task family \(\mathbf x=(x_1,\ldots,x_n)\), define

$$
\mathsf L(e_1;\mathbf x\mid e_0,W,o,z)
=
\mathsf K_{P_{e_0}}
\left(
\left\langle P_{e_1},R_{e_1,o}\right\rangle
\mid W,o,z
\right)
+
\sum_{i=1}^n\mathsf K_{P_{e_1}}(x_i\mid h_i,z_i).
\tag{2.7}
$$

The first term charges the new language, linguistic map, interpreter, and task readout relative to the current presentation before the new presentation receives credit for shorter descriptions. If the transition also replaces the proposal or verification procedures, their descriptions and execution costs must be charged separately. Description gain and discovery gain remain distinct:

$$
\begin{aligned}
\Delta_{\mathrm{desc}}
&=
\sum_i\mathsf K_{P_{e_0}}(x_i\mid h_i,z_i)
-\mathsf L(e_1;\mathbf x\mid\cdots),\\
\Delta_{\mathrm{find}}^B
&=
\sum_i
\left[
\mathsf A_{\mathcal B_{e_0,a}}^B(x_i\mid h_i,z_i)
-
\mathsf A_{\mathcal B_{e_1,a}}^B(x_i\mid h_i,z_i)
\right].
\end{aligned}
\tag{2.8}
$$

For universal computational presentations, the invariance theorem gives an additive simulation constant. That constant contains a compiler and is directional: in general, \(c(e_0,e_1)\neq c(e_1,e_0)\). Although asymptotically harmless, it may dominate a finite task. A compiler that exists but cannot be described, found, run, or verified within the available budget does not remove operational occlusion [7–10].

# 3. Epistemic theories and representational change

## 3.1 Classical epistemic theories

A classical epistemic theory must contain more than a probability space. I write

$$
W=
\bigl(
P_W,
\Omega_W,\mathcal F_W,\mu_W,
\llbracket\cdot\rrbracket_W,
\mathcal O_o,
\mathcal K_W,
V_W,\Lambda_W,
\mathsf{Commit}_W,
\mathcal H_W
\bigr),
\tag{3.1}
$$

where \(P_W\) is the current presentation; \((\Omega_W,\mathcal F_W,\mu_W)\) is its represented world and belief state; \(\llbracket\cdot\rrbracket_W\) interprets linguistic expressions as measurable events; \(\mathcal O_o=(\mathcal S_o,E_o,T_o)\) is the observation interface; \(\mathcal K_W\) is the epistemic structure developed in §3.3; \(V_W\) and \(\Lambda_W\) are the current verifier and proposal law; and the last two entries record executable commitment and history. The represented world \(\Omega_W\) is not the external generator \(G_*\). It is the theory's current model of that generator.

## 3.2 Linguistic observations and EUH verdicts

A verdict can be formed only after the presentation has produced a linguistic expression. Fix a finite sequence generated by the candidate theory,

$$
\widehat{\Phi}\in\mathcal E_e^{<\omega},
$$

a newly formed expression

$$
\varphi\in\mathcal E_e,
$$

and a verification budget \(B^{\mathrm v}\). Let

$$
\Sigma=\{\mathsf E,\mathsf U,\mathsf H\}
\tag{3.2}
$$

be the basic verdict carrier. Here \(\mathsf E\), \(\mathsf U\), and \(\mathsf H\) denote **exemplified**, **unknown**, and **hallucinated**, respectively. The local classifier is

$$
c_{e,B^{\mathrm v}}:
\mathcal E_e^{<\omega}\times\mathcal E_e
\longrightarrow\Sigma.
\tag{3.3}
$$

It is implemented by \(V_e\) and compares the expressions generated by the candidate theory with the newly formed expression. Both inputs are linguistic. The classifier receives neither the external signal nor the opaque carrier.

For fixed \(\widehat{\Phi}\), the classifier partitions the expression space into the verdict-indexed regions

$$
\mathcal C_{e,\widehat{\Phi}}^{s,B^{\mathrm v}}
=
\left\{
\varphi\in\mathcal E_e:
c_{e,B^{\mathrm v}}(\widehat{\Phi},\varphi)=s
\right\},
\qquad
s\in\Sigma.
\tag{3.4}
$$

Thus \(\mathcal C^{\mathsf E}\), \(\mathcal C^{\mathsf U}\), and \(\mathcal C^{\mathsf H}\) are the regions producing witnessed, unobservable, and refuted observations—and hence exemplified, unknown, and hallucinated verdicts—respectively.

The linguistic outcome is therefore either silence or a classified expression:

| Verdict | Observation | Condition | Classifier | Interpretation |
|---|---|---|---|---|
| No verdict | **Silence** | No new expression is available | Not invoked | No linguistic object is available for comparison with \(\widehat{\Phi}\). |
| **Exemplified** (\(\mathsf E\)) | **Witnessed** | \(\varphi\in\mathcal C_{e,\widehat{\Phi}}^{\mathsf E,B^{\mathrm v}}\) | Invoked | The expression is witnessed relative to the theory-generated expressions. |
| **Unknown** (\(\mathsf U\)) | **Unobservable** | \(\varphi\in\mathcal C_{e,\widehat{\Phi}}^{\mathsf U,B^{\mathrm v}}\) | Invoked | The comparison is proven unresolved under the declared verification budget. |
| **Hallucinated** (\(\mathsf H\)) | **Refuted** | \(\varphi\in\mathcal C_{e,\widehat{\Phi}}^{\mathsf H,B^{\mathrm v}}\) | Invoked | The expression exposes a certified incoherence in the candidate theory. |

Silence is the absence of a signal, carrier, expression, or response at some boundary of the process. It may occur whether or not it is measured. When an observation procedure detects and records silence, I denote the resulting observational record by \(\bot\). Unrecorded silence supplies no observation and prompts no epistemic update. Recorded silence is not a verdict: no linguistic expression is available for the classifier to classify as witnessed, unobservable, or refuted. Thus

$$
\bot\notin\Sigma.
\tag{3.5}
$$

The external model may contain several mechanisms capable of leaving the agent without an expression. Unless a further expression identifies the mechanism, those causes are indistinguishable from the agent's perspective. When the silence is recorded, the observational outcome is simply \(\bot\).

### The unknown verdict

The word *unknown* has a defined operational meaning here. It does not mean that the agent is uncertain about whether the verdict is \(\mathsf E\), \(\mathsf U\), or \(\mathsf H\). When the classifier returns \(\mathsf U\), the agent has observed one definite result:

> The current epistemic regime does not resolve this linguistic comparison.

The evidential ledger may distinguish two grounds for that result:

- \(\mathsf U_B\): the admissible procedure obtained no resolution within the declared budget;
- \(\mathsf U_{\mathrm{eff}}\): a metacertificate establishes that the comparison is not resolvable by the admissible effective procedures of the current theory—for example, because of undecidability, incompleteness, or independence.

Both project to the basic EUH verdict:

$$
\pi_{\mathsf U}(\mathsf U_B)
=
\pi_{\mathsf U}(\mathsf U_{\mathrm{eff}})
=
\mathsf U.
\tag{3.6}
$$

A timeout returns \(\mathsf U_B\). The stronger annotation \(\mathsf U_{\mathrm{eff}}\) requires an accepted metacertificate; nontermination alone does not establish it.

Neither verdict asserts absolute unknowability. A richer language, proof system, theory, or oracle may make the comparison resolvable. Nor is either verdict a probability distribution over \(\mathsf E\) and \(\mathsf H\). The uncertainty belongs to the object of inquiry; the verdict that the current regime cannot resolve it is definite.

### System-level inverse images

For likelihood construction, the linguistic regions in (3.4) may be pulled back through \(D_e\):

$$
\mathsf{Evt}_{e,\widehat{\Phi}}^{s,B^{\mathrm v}}
=
D_e^{-1}
\left(
\mathcal C_{e,\widehat{\Phi}}^{s,B^{\mathrm v}}
\right),
\qquad
s\in\Sigma.
\tag{3.7}
$$

These are system-level inverse images on the opaque carrier space. They permit the probabilistic model to state likelihood constraints, but their definition does not give the agent access to the carrier. The agent observes only silence or a linguistic expression and its resulting verdict.

Lossy decoding is likewise not assigned a general event or numerical measure. I model only its consequences for linguistic generation and comparison.

### Increasing the verification budget

Assume a **monotone certificate regime**: verification runs are nested, and a larger run retains every certificate accepted by an earlier run. If

$$
B_1^{\mathrm v}\preceq B_2^{\mathrm v},
$$

then, suppressing the fixed indices \(e,\widehat\Phi\),

$$
\mathsf{Evt}^{\mathsf E,B_1^{\mathrm v}}\subseteq\mathsf{Evt}^{\mathsf E,B_2^{\mathrm v}},
\qquad
\mathsf{Evt}^{\mathsf H,B_1^{\mathrm v}}\subseteq\mathsf{Evt}^{\mathsf H,B_2^{\mathrm v}},
\qquad
\mathsf{Evt}^{\mathsf U,B_2^{\mathrm v}}\subseteq\mathsf{Evt}^{\mathsf U,B_1^{\mathrm v}}.
\tag{3.8}
$$

This monotonicity is an assumption about the verification regime, not a general property of epistemic revision. It excludes defeasible regimes in which later evidence can withdraw an earlier certificate.

A structurally unobservable comparison may remain in the unknown region at every finite budget. A budget-relative unknown verdict may later become exemplified or hallucinated when the comparison becomes witnessed or refuted.

The derivation budget \(B^{\mathrm d}\) is separate. It limits the construction of generative expressions and candidate certificates. The verification budget \(B^{\mathrm v}\) limits how far an obtained linguistic comparison can be checked.

## 3.3 Observation joins and epistemic algebra

The classifier above supplies individual verdicts. I now define the epistemic states in which those verdicts may be represented and the algebra by which several linguistic observations are joined.

### Epistemic objects and states

The classifier supplies a definite verdict only after a linguistic comparison has been performed. Before that verdict is observed, the comparison may instead be represented by a possibility set or a probability distribution. These objects have different types:

| Object | Type | Meaning |
|---|---|---|
| Silence | \(\bot\) | No linguistic expression is available; the classifier is not invoked and no verdict exists. |
| Classified observation | \((\varphi,s)\in\mathcal E_e\times\Sigma\) | A linguistic expression together with the definite verdict returned for it. |
| Verdict | \(s\in\Sigma\) | One definite classifier result: \(\mathsf E\), \(\mathsf U\), or \(\mathsf H\). |
| Possibility set | \(A\in2^\Sigma\setminus\{\varnothing\}\) | The verdicts not yet excluded when classification has not fixed one. |
| Distribution | \(p\in\Delta(\Sigma)\) | Probabilistic uncertainty over possible verdicts. |
| Join | \(\bigvee_i s_i\in\Sigma\) | A lossy aggregation of several definite verdicts under the contamination order. |

The possibility-set layer is the support projection of the probabilistic layer: for \(\mu\in\Delta(\Sigma)\), the corresponding possibility set is \(\operatorname{supp}(\mu)\). Equation (3.20) records how that support contracts under partial observation.

In particular,

$$
\mathsf U
\neq
\{\mathsf E,\mathsf U,\mathsf H\}
\neq
p(\mathsf E,\mathsf U,\mathsf H).
\tag{3.9}
$$

The first object is a definite verdict of non-resolution. The second is a set of verdicts that remain possible. The third is a probability distribution over verdicts.

### The observation join

Once a linguistic comparison is well typed, its verdict may be considered before or after observation. Working within a fixed epistemic theory \(W\), let

$$
S:\Omega_W\longrightarrow\Sigma,
\qquad
\Sigma=\{\mathsf E,\mathsf U,\mathsf H\},
$$

be the verdict-valued variable associated with one comparison. Before its value is observed, its epistemic state is

$$
\mu_S
:=
S_*\mu_W
=
\bigl(
p_S(\mathsf E),
p_S(\mathsf U),
p_S(\mathsf H)
\bigr)
\in\Delta(\Sigma).
\tag{3.10}
$$

After the comparison is observed with verdict \(s\), this state is the corresponding point mass \(\delta_s\).

The verdict carrier is ordered by contamination:

$$
\mathsf E\preceq\mathsf U\preceq\mathsf H.
\tag{3.11}
$$

The join of two realized verdicts is

$$
s_1\vee s_2
=
\max_{\preceq}\{s_1,s_2\}.
\tag{3.12}
$$

This is a contamination order, not a truth order or an information order. The value higher in the order governs the aggregate without thereby being truer or more informative. Here \(\mathsf E\) is neutral and \(\mathsf H\) is absorbing:

$$
\mathsf E\vee s=s,
\qquad
\mathsf H\vee s=\mathsf H.
\tag{3.13}
$$

The operation is commutative, associative, and idempotent:[^kleene]

$$
s_1\vee s_2=s_2\vee s_1,
\qquad
(s_1\vee s_2)\vee s_3
=
s_1\vee(s_2\vee s_3),
\qquad
s\vee s=s.
\tag{3.14}
$$

[^kleene]: Restricted to realized verdicts, this operation has the same table as strong Kleene conjunction under the correspondence \(\mathsf E\leftrightarrow\mathrm{true}\), \(\mathsf U\leftrightarrow\mathrm{indeterminate}\), and \(\mathsf H\leftrightarrow\mathrm{false}\) [51]. The coincidence is algebraic, not semantic: here \(\mathsf U\) is a definite observed verdict of non-resolution, not an indeterminate truth value. The prospective, probabilistic, and partially observed constructions in (3.10) and (3.15)–(3.21) are additional structure, not part of that truth table.

### Joinability before observation

Two simultaneous comparisons \(S_1\) and \(S_2\) are **joinable** when they are defined on a common probability space and take values in the same verdict algebra \(\Sigma\). Within one theory \(W\), the common space is \(\Omega_W\). Verdict variables originating in different models require a declared coupling before their pointwise join is defined. Joinability depends on their types, not on whether their values have already been observed. Their aggregate is therefore defined prospectively by

$$
J=S_1\vee S_2,
\qquad
J(\omega)
=
S_1(\omega)\vee S_2(\omega).
\tag{3.15}
$$

Thus the aggregate exists as a verdict-valued variable before either constituent verdict is known. Observation supplies its realized value; it does not create the composite.

If both comparisons remain unobserved, let

$$
\pi(s_1,s_2)
=
\Pr(S_1=s_1,S_2=s_2)
$$

be their joint epistemic state. The state of their aggregate is the pushforward of \(\pi\) through the join:

$$
\mu_J(s)
=
\sum_{\substack{s_1,s_2\in\Sigma\\s_1\vee s_2=s}}
\pi(s_1,s_2).
\tag{3.16}
$$

The joint state \(\pi\) records any dependence between the comparisons. When independence is part of the model, \(\pi=\mu_{S_1}\otimes\mu_{S_2}\); otherwise their marginals alone do not determine \(\mu_J\).

### Partial observation and early determination

The lattice may determine the aggregate before every constituent verdict has been observed. Let

$$
\mu=(p_E,p_U,p_H)
$$

be the state of an unobserved comparison.

If an already observed constituent has verdict \(\mathsf E\), it leaves the state of the aggregate unchanged:

$$
\delta_{\mathsf E}\vee\mu
=
\mu.
\tag{3.17}
$$

If an observed constituent has verdict \(\mathsf U\), the aggregate can no longer have verdict \(\mathsf E\). The probability formerly assigned to \(\mathsf E\) is absorbed into \(\mathsf U\):

$$
\delta_{\mathsf U}\vee\mu
=
(0,p_E+p_U,p_H).
\tag{3.18}
$$

If an observed constituent has verdict \(\mathsf H\), the absorbing element fixes the aggregate immediately:

$$
\delta_{\mathsf H}\vee\mu
=
\delta_{\mathsf H}.
\tag{3.19}
$$

Consequently, the possible state of an aggregate contracts as contaminating evidence arrives:

$$
\{\mathsf E,\mathsf U,\mathsf H\}
\xrightarrow{\ \vee\mathsf U\ }
\{\mathsf U,\mathsf H\}
\xrightarrow{\ \vee\mathsf H\ }
\{\mathsf H\}.
\tag{3.20}
$$

This permits sound short-circuit evaluation. Once any constituent has verdict \(\mathsf H\), no still-unobserved constituent can alter the aggregate:

$$
\mathsf H\vee S_1\vee\cdots\vee S_n
=
\mathsf H.
\tag{3.21}
$$

For a finite family, let \(r_k\) be the join of the first \(k\) observed verdicts. Then:

- \(r_k=\mathsf E\): the unobserved comparisons retain all three possible aggregate outcomes;
- \(r_k=\mathsf U\): only \(\mathsf U\) and \(\mathsf H\) remain possible;
- \(r_k=\mathsf H\): the final aggregate is already determined.

The join therefore states both the current aggregate and whether further observation can still change it.

### Complete join table

Embed each realized verdict \(s\) into \(\Delta(\Sigma)\) as \(\delta_s\). For arbitrary unobserved states

$$
\mu=(p_E,p_U,p_H),
\qquad
\nu=(q_E,q_U,q_H),
$$

the observation-join algebra acts as follows:

| \(\vee\) | \(\delta_{\mathsf E}\) | \(\delta_{\mathsf U}\) | \(\delta_{\mathsf H}\) | Unobserved \(\nu\) |
|---:|:---:|:---:|:---:|:---:|
| \(\delta_{\mathsf E}\) | \(\delta_{\mathsf E}\) | \(\delta_{\mathsf U}\) | \(\delta_{\mathsf H}\) | \(\nu\) |
| \(\delta_{\mathsf U}\) | \(\delta_{\mathsf U}\) | \(\delta_{\mathsf U}\) | \(\delta_{\mathsf H}\) | \((0,q_E+q_U,q_H)\) |
| \(\delta_{\mathsf H}\) | \(\delta_{\mathsf H}\) | \(\delta_{\mathsf H}\) | \(\delta_{\mathsf H}\) | \(\delta_{\mathsf H}\) |
| Unobserved \(\mu\) | \(\mu\) | \((0,p_E+p_U,p_H)\) | \(\delta_{\mathsf H}\) | \(\vee_*\pi_{\mu,\nu}\) |

Here \(\pi_{\mu,\nu}\) is the joint state of the two unobserved comparisons and \(\vee_*\pi_{\mu,\nu}\) is its pushforward under the deterministic join. The lower-right entry covers the only case in which neither constituent has yet supplied a realized value.

The table shows that joinability is defined before observation and that contamination may determine the aggregate before observation is complete.

Silence remains outside the observation-join algebra. Without a linguistic expression, the classifier is not invoked and supplies no verdict-valued operand to the join.

## 3.4 Conservative and nonconservative change

Let \(e\) be a candidate extension of \(W\). It supplies a successor presentation \(P_e\), world space \(\Omega_e\), prior \(\nu_e\), interpretation, a generative-theory seed \(q_e\in\mathcal E_e\), and a bounded realization. A conservative extension includes an embedding of old expressions

$$
\iota_e:\mathcal E_W\hookrightarrow\mathcal E_e
\tag{3.22}
$$

and an admissible retraction \(r_e:\mathcal E_e\rightharpoonup\mathcal E_W\) with \(r_e\circ\iota_e=\operatorname{id}\) on the old language. It also supplies a projection \(\pi_e:\Omega_e\to\Omega_W\).

The usual semantic and probabilistic preservation conditions are

$$
\llbracket\iota_e(\varphi)\rrbracket_e(\omega')
=
\llbracket\varphi\rrbracket_W(\pi_e\omega'),
\tag{3.23}
$$

and

$$
(\pi_e)_*\nu_e=\mu_W.
\tag{3.24}
$$

The new presentation must also preserve what the old linguistic boundary and interpreter could already do. For the linguistic map I require

$$
\begin{gathered}
\operatorname{dom}(D_W)
\subseteq
\operatorname{dom}(D_e),\\
D_e\bigl(\operatorname{dom}(D_W)\bigr)
\subseteq
\operatorname{dom}(r_e),\\
r_e(D_e(\tau))=D_W(\tau),
\qquad
\tau\in\operatorname{dom}(D_W).
\end{gathered}
\tag{3.25}
$$

For the interpreter I require

$$
\begin{gathered}
\iota_e\bigl(\operatorname{dom}(U_W)\bigr)
\subseteq
\operatorname{dom}(U_e),\\
U_e\!\left(
\iota_e\bigl(\operatorname{dom}(U_W)\bigr)
\right)
\subseteq
\operatorname{dom}\!\left(r_e^{<\omega>}\right),\\
r_e^{<\omega>}
\bigl(U_e(\iota_e(\varphi))\bigr)
=
U_W(\varphi),
\qquad
\varphi\in\operatorname{dom}(U_W).
\end{gathered}
\tag{3.26}
$$

These conditions allow the new language to make finer distinctions and generate additional expressions while recovering the old behaviour under projection. Proof-theoretic conservativity remains separate: preservation of consequences, existence of an effective proof translation, and a genuine proof retraction do not follow from one another without additional assumptions.

A nonconservative candidate is not a malformed conservative one. It may revise, split, merge, or forget old distinctions, alter the old generative cycle, or change old marginals. It must state how old queries and commitments are transformed. Bayesian comparison remains available as long as candidates assign likelihoods on the same public packet space. Nonconservativity changes the theory transition, not Bayes' rule.

## 3.5 Priors, proposals, and commitment

Let \(q(e\mid W,o)\) be the prior mass on candidate presentations, and let \(\nu_e\) be the prior within candidate \(e\). The classical successor space is

$$
\Omega^+_{W,o}
=
\bigsqcup_e\{e\}\times\Omega_e,
\qquad
\Pi_0=q\otimes\nu.
\tag{3.27}
$$

**Remark (belief-neutral entertainment).** Let \(\mathcal C\) be a conservative candidate family on which the prior is supported:

$$
\sum_{e\in\mathcal C}q(e\mid W,o)=1.
$$

If every \(e\in\mathcal C\) satisfies (3.24), then merely entertaining those extensions does not alter beliefs about the old world. For every \(A\in\mathcal F_W\),

$$
\sum_{e\in\mathcal C}
q(e\mid W,o)\,
\nu_e(\pi_e^{-1}A)
=
\mu_W(A).
\tag{3.28}
$$

An absent candidate cannot acquire posterior mass by conditioning. Let

$$
g(\mathrm de\mid W,o,z)
$$

denote the proposal kernel over successor presentations induced by the current proposal procedure \(\Lambda_W\) in context \((W,o,z)\). New presentations must be predeclared through a generator, proposed through \(g\), or explicitly minted together with a prospective evaluation rule and a ledger entry. Data-dependent invention is a selection event and must be included in the model.

Let \(\alpha\) index the stages of representational revision, with \(W_\alpha\) denoting the executable theory at stage \(\alpha\). Conditioning changes its belief state; commitment constructs its successor:

$$
W_{\alpha+1}
=
\mathsf{Commit}_{W_\alpha}(e,\varphi,s).
\tag{3.29}
$$

I retain a double ledger \(\mathcal H_\alpha=(\mathcal H_\alpha^{\mathrm{sem}},\mathcal H_\alpha^{\mathrm{ev}})\). The semantic ledger records admitted meanings and preserved invariants. The evidential ledger records packets, decoded expressions, generated expressions, claims, verdicts, rejections, silences, and superseded states. Their overlap permits audit; their nonidentity prevents a later linguistic commitment from rewriting the evidence on which it was based. This separation explains why a nonconservative commitment may change the executable semantics recorded in \(\mathcal H^{\mathrm{sem}}\), while Bayesian conditioning remains attached to public evidential records in \(\mathcal H^{\mathrm{ev}}\) that the commitment cannot retrospectively alter.

# 4. Public evidence and local semantics

## 4.1 The common evidential boundary

Bayesian comparison requires a common observation space. It does not require a common internal semantics. Let \(\widehat\Sigma\) be a finite alphabet of public reports and define the packet space

$$
\mathcal Y_o
=
\{\bot\}\sqcup(\widehat\Sigma\times T_o).
\tag{4.1}
$$

The symbol \(\bot\in\mathcal Y_o\) denotes the public observational record produced when silence is detected. Silence itself may occur without being measured; in that case no packet is returned and no update is prompted. Silence may also occur at a candidate-local boundary—for example, when \(D_e(\tau)\) is undefined. If that boundary is monitored, the silence may be recorded in the candidate's evidential ledger, but it is not an additional public packet unless it is publicly emitted. A nonsilent packet \(y=(\hat s,\tau)\) contains a public report \(\hat s\) and the opaque carrier supplied by the observational apparatus. Every candidate is evaluated on the same packet. This is the sense in which the evidence is public. It does not make \(\tau\) available as a linguistic object: within candidate \(e\), the carrier enters only through \(D_e\).

Thus the candidate-local construction has two linguistic routes, followed by their comparison:

$$
\begin{aligned}
y_n=(\hat s_n,\tau_n)
&\xrightarrow{D_e}
\varphi_{e,n},\\
(q_e,h_{e,n},z_n)
&\xrightarrow{\operatorname{Run}_{\mathcal B_e}^{B^{\mathrm d}}}
\widehat\Phi_{e,n}^{B^{\mathrm d}},\\
\bigl(
\widehat\Phi_{e,n}^{B^{\mathrm d}},
\varphi_{e,n}
\bigr)
&\xrightarrow{c_{e,B^{\mathrm v}}}
s_{e,n}\in\Sigma.
\end{aligned}
\tag{4.2}
$$

The first route forms a new expression from the current packet. The second runs the candidate's generative theory by the bounded procedure defined in §4.2. The classifier compares their linguistic outputs. If \(D_e(\tau_n)\) is undefined, the comparison is not formed.

## 4.2 Linguistic comparison inside a candidate

Let \(q_e\in\mathcal E_e\) express the current generative theory of candidate \(e\). Let

$$
\operatorname{Run}_{\mathcal B_e}^{B^{\mathrm d}}
(q_e;h_{e,n},z_n)
\in\mathcal E_e^{<\omega}
$$

denote the finite, ordered sequence returned when the derivation procedure of the bounded realization executes \(U_e\) from \(q_e\) within budget \(B^{\mathrm d}\). I write

$$
\widehat\Phi_{e,n}^{B^{\mathrm d}}
=
\operatorname{Run}_{\mathcal B_e}^{B^{\mathrm d}}
(q_e;h_{e,n},z_n).
\tag{4.3}
$$

Unlike \(\operatorname{Cl}_{U_e}\), which records unbudgeted extensional reachability, \(\operatorname{Run}_{\mathcal B_e}^{B^{\mathrm d}}\) records one actual bounded derivation. If the derivation procedure is randomized, its internal randomness is included in the candidate's construction of the kernel below.

When the next nonsilent packet arrives and \(D_e(\tau_n)\) is defined, the agent obtains the new expression \(\varphi_{e,n}=D_e(\tau_n)\). It can then classify the relation between the expressions generated by its theory and this newly formed expression:

$$
s_{e,n}
=
c_{e,B^{\mathrm v}}
\bigl(\widehat\Phi_{e,n}^{B^{\mathrm d}},\varphi_{e,n}\bigr).
\tag{4.4}
$$

Equation (4.4) is the operative comparison. The agent neither compares \(\tau_n\) with an earlier carrier nor interprets the carrier directly. It compares linguistic expressions produced along two routes: expressions generated by running its theory, and an expression formed from a subsequent external signal.

Different candidates may therefore form different expressions from the same carrier and obtain different local verdicts. Those expressions need not be translated into one another. What must be shared is the packet on which the candidates place likelihoods.

## 4.3 Packet kernels

Each candidate supplies a Markov kernel satisfying

$$
K_e(\,\cdot\mid\omega,z,h_e)
\in\Delta(\mathcal Y_o),
\qquad
\omega\in\Omega_e.
\tag{4.5}
$$

Thus \(K_e(A\mid\omega,z,h_e)\) is the candidate's probability for a measurable public event \(A\subseteq\mathcal Y_o\). One useful factorization is

$$
\begin{aligned}
K_e(\{\bot\}\mid\omega,z,h_e)
&=\eta_e(\omega,z,h_e),\\
K_e(\mathrm d\hat s,\mathrm d\tau\mid\omega,z,h_e)
&=
\bigl(1-\eta_e(\omega,z,h_e)\bigr)
\rho_e(\mathrm d\tau\mid\omega,z)
m_e(\mathrm d\hat s\mid\tau,\omega,z,h_e).
\end{aligned}
\tag{4.6}
$$

Here

$$
\eta_e(\omega,z,h_e)\in[0,1],
\qquad
\rho_e(\,\cdot\mid\omega,z)\in\Delta(T_o),
\qquad
m_e(\,\cdot\mid\tau,\omega,z,h_e)\in\Delta(\widehat\Sigma).
$$

In (4.6), \(\eta_e\) is the probability of silence, \(\rho_e\) is the conditional distribution of the carrier when a non-silent observation occurs, and \(m_e\) is the conditional distribution of the public report attached to that carrier. This decomposition is only one way to construct \(K_e\); the subsequent comparison requires only that every candidate define a kernel on the shared packet space \(\mathcal Y_o\). Integrating out the candidate's world state gives its predictive measure

$$
\mathbb P_e(\mathrm dy\mid W,o,z)
=
\int_{\Omega_e}
K_e(\mathrm dy\mid\omega,z,h_e)\,
\nu_e(\mathrm d\omega).
$$

In particular, a candidate may model correlations between silence, report, and carrier without assuming (4.6).

The causal order represented here is

$$
\text{external state}
\longrightarrow
\text{signal and opaque carrier}
\longrightarrow
\text{public report},
\tag{4.7}
$$

while the candidate's expression and verdict are local observations and computations used to assess the likelihood of that public outcome. They are not additional **public** observations unless they are themselves emitted as later public packets.

## 4.4 Verification and hard zeros

A verified contradiction may impose a zero likelihood, but only when the verifier establishes that the public report and the candidate's linguistic consequences are mutually exclusive. Suppose \(\widehat\Sigma\) contains distinguished reports

$$
\widehat{\mathsf E},
\widehat{\mathsf U},
\widehat{\mathsf H}
\in\widehat\Sigma.
$$

Under a strict, noiseless reporting protocol, for example, coherence may require

$$
\begin{aligned}
m_e(\widehat{\mathsf E}\mid\tau,\omega,z,h_e)&=0
&&\text{on }\mathsf{Evt}_{e,\widehat\Phi}^{\mathsf H,B^{\mathrm v}},\\
m_e(\widehat{\mathsf H}\mid\tau,\omega,z,h_e)&=0
&&\text{on }\mathsf{Evt}_{e,\widehat\Phi}^{\mathsf E,B^{\mathrm v}}.
\end{aligned}
\tag{4.8}
$$

With a noisy or strategically unreliable reporter, these zeros are replaced by declared error probabilities. An unknown verdict imposes no hard zero. Neither does a timeout: failure to find a proof within budget is not a proof of failure.

The same discipline applies when several agents or instruments report on one packet. Their ordered verdict tuple contains more information than its join in the contamination order. If only \(s_1\vee\cdots\vee s_k\) is published, the identities and disagreements of the reporters have been discarded. The Bayesian model must use the statistic that was actually observed and account for that loss. Silence remains a separate public outcome, not a synonym for \(\mathsf U\).

A recorded public silence has its own likelihood \(K_e(\{\bot\}\mid\omega,z,h_e)\). Silence that occurs but is not measured produces no packet; whether its absence from the data may be ignored depends on the observation protocol and requires an explicit missingness condition [18]. Candidate-local failure to form an expression is different again: it affects the local linguistic route, but becomes public evidence only if the failure is publicly reported.

## 4.5 Shared packets and candidate-local languages

The construction separates three levels:

| Level | Shared between candidates? | Object |
|---|---:|---|
| Apparatus | Yes | Public context and the same public outcome \(y\in\mathcal Y_o\); a nonsilent outcome carries \(\tau\in T_o\) |
| Language | Not in general | \(\varphi_e=D_e(\tau)\) and expressions generated under \(U_e\) |
| Statistical comparison | Yes | Candidate predictive measure \(\mathbb P_e(\mathrm dy)\) on \(\mathcal Y_o\) |

The shared likelihood boundary is deliberately thin. It allows Bayesian comparison without pretending that candidate languages already possess a common translation, a common ontology, or a common internal expression space.

# 5. Bayesian updating over presentations

## 5.1 The posterior

On the disjoint successor space (3.27), the prior and candidate kernels define the joint measure

$$
\Gamma(\mathrm de,\mathrm d\omega,\mathrm dy\mid W,o,z)
=
q(\mathrm de\mid W,o)\,
\nu_e(\mathrm d\omega)\,
K_e(\mathrm dy\mid\omega,z,h_e).
\tag{5.1}
$$

Because the spaces are standard Borel, the posterior \(\Pi(\mathrm de,\mathrm d\omega\mid y,W,o,z)\) may be taken as a regular conditional distribution of \((e,\omega)\) given \(y\) under \(\Gamma\).

Let the prior predictive mixture be

$$
\mathbb M(\mathrm dy\mid W,o,z)
=
\sum_f
q(f\mid W,o)\,
\mathbb P_f(\mathrm dy\mid W,o,z).
\tag{5.2}
$$

For every candidate with positive prior mass, \(\mathbb P_e\ll\mathbb M\), and a version of the marginal update over presentations is, for \(\mathbb M\)-almost every \(y\),

$$
q(e\mid y,W,o,z)
=
q(e\mid W,o)
\frac{\mathrm d\mathbb P_e}
{\mathrm d\mathbb M}(y).
\tag{5.3}
$$

Nothing in (5.1) requires candidate expressions to be identical. Each candidate uses its own decoder, interpreter, theory, and verifier to construct a predictive measure on the common packet space. That measure, not a direct comparison of candidate meanings, is the Bayesian interface. In discrete or commonly dominated models, the Radon–Nikodym derivative in (5.3) reduces to the usual likelihood divided by the mixture likelihood.

For a sequence \(y_{1:n}\), let

$$
\nu_{e,k}(\mathrm d\omega)
=
\Pi(\mathrm d\omega\mid e,y_{1:k},W,o,z_{1:k})
$$

denote the current conditional world-state law of a candidate that retains positive posterior mass. Its next predictive measure is

$$
\mathbb P_{e,k+1}(\mathrm dy\mid W,o,z_{1:k+1})
=
\int_{\Omega_e}
K_e(\mathrm dy\mid\omega,z_{k+1},h_{e,k})\,
\nu_{e,k}(\mathrm d\omega).
$$

The histories \(h_{e,k}\) are candidate-relative and evolve through their own linguistic cycles. The public sequence is common, but its internal expression is not. Standard sequential conditioning applies whenever the candidate kernels are adapted to the common filtration.

## 5.2 Certificates and probabilistic evidence

Evidence may affect a candidate in two distinct ways. Ordinary predictive evidence changes its weight by a finite likelihood ratio. A checkable certificate of incompatibility may set its likelihood to zero. The second operation is stronger and requires an explicit proof object or finite computation that the declared verifier accepts.

This distinction prevents a bounded absence of discovery from being silently promoted into an extensional impossibility. It also makes the role of verification budgets visible: enlarging \(B^{\mathrm v}\) may convert \(\mathsf U\) into \(\mathsf E\) or \(\mathsf H\), but nested verification does not reverse an already retained certificate.

## 5.3 Example: a finite Bayesian update

For a finite discrete example, consider three candidate presentations with prior weights

$$
q_0=(0.5,0.3,0.2).
\tag{5.4}
$$

Suppose the first public packet has likelihoods

$$
p(y_1\mid e_1,e_2,e_3)=(0.9,0.285,0.23).
\tag{5.5}
$$

The unnormalised weights are \((0.45,0.0855,0.046)\), giving

$$
q_1\approx(0.774,0.147,0.079).
\tag{5.6}
$$

Now all three candidates receive the same second packet. Each forms its own expression, runs its own generative theory, and compares the resulting predicted expressions with the newly formed expression. Suppose \(e_1\) obtains a refuted observation and hence a hallucinated verdict, while \(e_2\) and \(e_3\) obtain unobservable observations and hence unknown verdicts under their present budgets. Under the declared reporting model, let

$$
p(y_2\mid e_1,e_2,e_3)=(0,0.405,1).
\tag{5.7}
$$

Then

$$
q_2\approx(0,0.430,0.570).
\tag{5.8}
$$

The example is deliberately small, but it contains the whole architecture—shared evidence, candidate-local expressions, bounded linguistic comparison, and a common Bayesian update. Its outcome also shows how the update treats different forms of evidence. The initially favoured presentation is eliminated because the contradiction is certified, rather than merely being displaced by an unexplained classification. The two unresolved candidates retain different weights because they assigned different likelihoods to the public packet.

## 5.4 Selection, commitment, and path dependence

We separate posterior concentration from language updates. The posterior changes candidate weights; a decision rule selects a candidate, after which \(\mathsf{Commit}_W\) changes the executable presentation and records the change in both ledgers. The choice may depend on posterior risk, presentation cost, accessibility, reversibility, or the value of further exploration.

Because commitment changes what can later be expressed and proposed, representational learning is generally path-dependent. Two agents who receive the same public packets may adopt different presentations, form different later expressions, and consequently entertain different successor families. Bayesian coherence at each step does not imply convergence when proposal and commitment policies differ.

# 6. Phase-sensitive comparison and reference resources

## 6.1 Classical mixtures and cross-presentation operators

The classical successor space introduced in (3.27),

$$
\Omega^+_{W,o}
=
\bigsqcup_e \{e\}\times\Omega_e,
$$

is the disjoint union of the candidate-indexed state spaces and therefore represents the presentations as mutually exclusive classical alternatives. Algebraically, its bounded observables form a direct sum of commutative algebras. This is sufficient when the experiment can only ask which candidate sector generated a packet. It is not sufficient when an admissible reference operation can compare phases or transformations between presentations.

Let each candidate \(e\) be represented on a Hilbert space \(\mathcal H_e\). A classical mixture retains block-diagonal states on

$$
\mathcal H=\bigoplus_e\mathcal H_e.
\tag{6.1}
$$

It omits the off-diagonal operators

$$
X_{ef}\in\mathcal B(\mathcal H_f,\mathcal H_e),
\qquad e\neq f,
\tag{6.2}
$$

that encode a coherent comparison between sectors. Whether such operators are empirically meaningful is not decided by notation. It depends on the reference transformations and measurement procedures actually available to the agent [12–16].

## 6.2 Declared reference structure

A phase-sensitive model must therefore declare a reference system. Let \(\mathcal H_R\) be a common reference space and let

$$
J_e:\mathcal H_e\longrightarrow\mathcal H_R
\tag{6.3}
$$

be an admissible isometric embedding. A more general calibrated channel must instead be typed as a completely positive map between operator algebras. A reference observable \(X\in\mathcal B(\mathcal H_R)\) induces the cross-presentation component

$$
X_{ef}=J_e^*XJ_f.
\tag{6.4}
$$

Let \(\mathcal A_e\subseteq\mathcal B(\mathcal H_e)\) be the declared accessible \(C^*\)-algebra of sector \(e\). Let \(\mathcal X_{ef}\subseteq\mathcal B(\mathcal H_f,\mathcal H_e)\) be a closed \(\mathcal A_e\)-\(\mathcal A_f\) bimodule, set \(\mathcal X_{fe}=\mathcal X_{ef}^*\), and require

$$
\overline{\operatorname{span}}(\mathcal X_{ef}\mathcal X_{fe})
\subseteq\mathcal A_e,
\qquad
\overline{\operatorname{span}}(\mathcal X_{fe}\mathcal X_{ef})
\subseteq\mathcal A_f.
$$

Then the two sectors can be placed in the linking algebra

$$
\mathfrak L_{ef}
=
\begin{pmatrix}
\mathcal A_e & \mathcal X_{ef}\\
\mathcal X_{fe} & \mathcal A_f
\end{pmatrix},
\tag{6.5}
$$

whose off-diagonal entries are the declared admissible intertwiners [12,13]. The embeddings \(J_e\) are reference maps: they say how two already specified sectors can participate in a common experiment; they do not map opaque observation states into expressions.

The component \(X_{ef}\) is not by itself an observable. On \(\mathcal H_e\oplus\mathcal H_f\), it supplies the self-adjoint cross-sector observable

$$
\widetilde X_{ef}
=
\begin{pmatrix}
0 & X_{ef}\\
X_{ef}^* & 0
\end{pmatrix}.
$$

If the accessible observable algebra is block diagonal, then two density operators with the same diagonal blocks but different off-diagonal blocks are observationally indistinguishable. If an accessible \(\widetilde X_{ef}\) has nonzero pairing with their difference, they are distinguishable. This follows immediately from the trace pairing \(\operatorname{tr}(\rho\widetilde X_{ef})\): block-diagonal observables annihilate off-diagonal differences, while an admitted cross term need not.

## 6.3 A two-sector example

Take one normalized vector \(|e\rangle\) in sector \(e\) and one \(|f\rangle\) in sector \(f\). Compare the coherent state

$$
|+\rangle=\frac{|e\rangle+|f\rangle}{\sqrt2}
\tag{6.6}
$$

with the classical mixture

$$
\rho_{\mathrm{mix}}
=
\tfrac12|e\rangle\!\langle e|
+
\tfrac12|f\rangle\!\langle f|.
\tag{6.7}
$$

Every block-diagonal measurement gives the same statistics for the two states. The reference observable

$$
X=|e\rangle\!\langle f|+|f\rangle\!\langle e|
\tag{6.8}
$$

separates them: \(\langle+|X|+\rangle=1\), whereas \(\operatorname{tr}(\rho_{\mathrm{mix}}X)=0\). The distinction is operational only if the agent can implement the calibration that makes \(X\) available. Without that resource, adding complex amplitudes merely redescribes an empirically classical mixture.

Temporal tests such as Leggett--Garg inequalities make the same methodological point in a different setting: a claimed phase-sensitive distinction must be tied to an explicit family of interventions and measurements, not inferred from a preferred representation alone [14,15].

## 6.4 State-relative conservativity

In a noncommutative setting, the appropriate analogue of an admissible retraction is a state-preserving conditional expectation. Let \(\mathcal N\subseteq\mathcal M\) be von Neumann algebras and let \(\phi\) be a faithful normal state on \(\mathcal M\). A map

$$
E:\mathcal M\longrightarrow\mathcal N
\tag{6.9}
$$

is an admissible state-relative retraction when it is normal, positive, unital, idempotent, \(\mathcal N\)-bimodular, and \(\phi\circ E=\phi\). Tomiyama's theorem supplies the bimodule structure for norm-one projections, while Takesaki's theorem identifies the modular-invariance condition under which a \(\phi\)-preserving conditional expectation exists [16,17].

This matters for representational change. An inclusion \(\mathcal N\subseteq\mathcal M\) does not by itself guarantee that the old theory is recoverable without disturbing the relevant state. Conservativity is conditional on the state and on the available reference algebra.

## 6.5 Phase-sensitive comparison in *Perfect Theory*

*Perfect Theory* studies the limitations imposed by a language and asks under what conditions a learning process can nevertheless be optimal. Commensurability is central to both questions: any certificate comparing two presentations requires a reference structure in which their outputs, predictions, and revisions can be compared. Phase-sensitive resources enlarge that structure. They can distinguish presentations that agree under every classical packet statistic and may therefore support relative-optimality certificates unavailable to block-diagonal comparison.

Such commensurability is itself resource-dependent. Reference maps, intertwiners, calibrations, and verification procedures must be available and charged. Moreover, representational and dynamical commensurability can come apart: presentations may admit an operationally adequate joint description while their revision procedures remain order-dependent. When the available comparison statistics form an empirical model, joint measurability and contextuality test the first boundary, while the contextual fraction grades how much of the observed comparison behaviour admits a neutral classical representation [48–50]. When revision maps are realized by conditional expectations, commuting-square conditions test the stronger dynamical compatibility [52]. These distinctions determine which claims of learning-process optimality *Perfect Theory* can certify and what exploration or refutation remains available when certification fails.

# 7. Resource-bounded specialization

## 7.1 Presentation-relative KT

I now give a computational realization of the generative layer. This specialization begins after linguistic decoding has succeeded. A target \(x\in\{0,1\}^*\) is an effective serialization of a linguistic output under the declared readout \(R_{e,o}\).

Let \(M_e\) realize the relevant composition of the interpreter \(U_e\) and the readout \(R_{e,o}\). A description \(d\) specifies a generative procedure in presentation \(e\), while \(M_e^d(i,b)\) answers whether the resulting target has symbol \(b\) at position \(i\). The machine is therefore a computational bridge from expressions generated under \(U_e\) to their bitwise public representation.

Following Allender et al. [11], define

$$
\mathrm{KT}_e(x)
=
\min
\left\{
|d|+t:
\begin{array}{l}
\forall i\leq |x|+1\;\forall b\in\{0,1,*\},\\[2pt]
M_e^d(i,b)\text{ decides }[x_i=b]\text{ within }t\text{ steps}
\end{array}
\right\}.
\tag{7.1}
$$

Here \(x_{|x|+1}=*\) is an end marker. A successful description therefore certifies both the contents and the length of \(x\). The associated threshold problem is

$$
\mathrm{MKtP}_e(x,\theta)
\iff
\mathrm{KT}_e(x)\leq\theta.
\tag{7.2}
$$

The presentation \(e\) varies. This differs from standard MKTP, which fixes the decoding machine and varies only the target and threshold. Here the purpose is to compare the generative economy of candidate presentations.

## 7.2 Finite decision by bounded exhaustion

For the remainder of this section I restrict attention to the syntactic class \(\mathcal C_{\mathrm{KT}}\) defined in §8.1. Every machine in this class has a mandatory literal branch. Let \(B_e(x)\) be the known cost of the literal description of \(x\). Since every threshold \(\theta\geq B_e(x)\) is immediately satisfied, it is enough to consider

$$
\theta<B_e(x).
$$

**Proposition 7.1 (finite two-sided decision).** For every \(e\in\mathcal C_{\mathrm{KT}}\) and every finite instance \((x,\theta)\), the truth of \(\mathrm{MKtP}_e(x,\theta)\) is decidable uniformly in \((e,x,\theta)\). Under the literal normalization of §8.1, the exhaustive procedure runs in deterministic exponential time.

**Proof.** For a fixed threshold \(\theta\), the set

$$
S_\theta
=
\left\{
(d,t): |d|+t\leq\theta
\right\}
$$

is finite and has size \(2^{O(\theta)}\). For every \((d,t)\in S_\theta\), simulate each of the \(3(|x|+1)\) bit and end-marker queries for at most \(t\) steps. Accept if some pair answers every query correctly; reject after all pairs have failed.

Up to the polynomial overhead of the fixed simulator, this takes

$$
2^{O(\theta)}
\operatorname{poly}(|e|,|x|,\theta)
$$

time. The literal branch gives \(B_e(x)=|x|+O(\log |x|)\), so normalization yields a deterministic bound of

$$
2^{O(|x|)}
\operatorname{poly}(|e|,|x|).
$$

A positive certificate consists of one successful pair \((d,t)\) and its finite run logs. A negative record lists, for every pair in \(S_\theta\), a query on which that pair fails. The positive certificate is polynomial after normalization; the exhaustive negative record may be exponentially large, but remains finite and mechanically checkable. \(\square\)

Both hard EUH outcomes are therefore eventually certifiable on a fixed instance. A temporary \(\mathsf U\) records unfinished finite work, not inexpressibility of the target.

## 7.3 Presentation-relative accessibility under bounded search

Pointwise decidability does not make the successful description equally accessible under every presentation.

**Proposition 7.2 (universality does not imply bounded access).** For every finite enumerative budget \(B\geq1\), there are two extensionally universal prefix presentations and a computable target expressible in both such that the same length-lexicographic syntactic search certifies the target within \(B\) tests in one presentation but not in the other.

**Proof.** Let \(M_0\) be a universal prefix machine. Run the declared search for its first \(B\) finite tests and let \(F_B\) be the finite set of targets certified during those tests. Choose a computable target \(x\notin F_B\), and define

$$
M_1^{0}(i,b)
=
\operatorname{Lit}(x,i,b),
\qquad
M_1^{1p}(i,b)
=
M_0^p(i,b).
\tag{7.3}
$$

The descriptions \(0\) and \(1p\) preserve prefix-freeness, while the second branch preserves universality. The first branch makes \(x\) available on the first test in \(M_1\). By the choice of \(x\), the same bounded search has not certified it during its first \(B\) tests in \(M_0\). \(\square\)

The target is neither undecidable nor absent from \(M_0\): universality ensures that it has a description there, and Proposition 7.1 makes each fixed threshold test decidable. What differs is its position in the presentation-relative search. Thus

$$
\boxed{
\text{expressible in both}
\;+\;
\text{pointwise decidable}
\;\not\Longrightarrow\;
\text{equally accessible under bounded search}.
}
$$

# 8. Uniform dominance over serialized targets

Section 7 showed that a supplied presentation can be evaluated on any fixed finite target. I now ask whether one presentation is at least as economical as another on every target in the common readout domain.

For this specialization, the declared task readouts land in the shared effective serialization space

$$
\mathcal X_o=\{0,1\}^*.
$$

Thus the universal quantifier below ranges over all finite linguistic outputs expressible in that common serialized form. It does not range over opaque carriers or internal expressions.

## 8.1 The effective presentation class

A presentation code is a finite string \(e=\langle q\rangle\). A fixed wrapper interprets it as

$$
M_e^{1x}(i,b)
=
\operatorname{Lit}(x,i,b),
\qquad
M_e^{0p}(i,b)
=
\operatorname{Sim}(q,p,i,b).
\tag{8.1}
$$

The literal branch answers bit and end-marker queries for \(x\) within a known time. The simulated branch executes the presentation-specific program \(q\), but only for the time supplied by the tested pair \((d,t)\).

Consequently,

$$
\mathcal C_{\mathrm{KT}}
=
\{\langle q\rangle:q\in\{0,1\}^*\}
$$

is a decidable class of presentations. The literal branch supplies a computable ceiling \(B_e(x)\), and Proposition 7.1 therefore gives a uniform terminating procedure for computing \(\mathrm{KT}_e(x)\) from \((e,x)\).

Let \(c(e)=|\langle e\rangle|\) be the presentation charge and define the charged loss

$$
L_e(x)
=
c(e)+\mathrm{KT}_e(x).
$$

For every supplied triple \((e_0,e_1,x)\), the comparison

$$
L_{e_0}(x)\leq L_{e_1}(x)
$$

is decidable. Uniform dominance is the set

$$
\mathsf{KT\text{-}DOM}
=
\left\{
\langle e_0,e_1\rangle\in\mathcal C_{\mathrm{KT}}^2:
\forall x\in\{0,1\}^*,
\;
L_{e_0}(x)\leq L_{e_1}(x)
\right\}.
\tag{8.2}
$$

A failure of dominance therefore has one finite serialized target as a witness. A successful pointwise comparison, however, says nothing about targets not yet examined.

## 8.2 A halting-controlled pair

The hardness construction uses a simulated branch whose useful descriptions become available exactly when a supplied computation halts.

**Lemma 8.1.** For every Turing machine \(N\) and input \(w\), one can effectively construct \(e_0,e_1\in\mathcal C_{\mathrm{KT}}\), with \(c(e_0)<c(e_1)\), such that:

1. if \(N(w)\) does not halt, then
   $$
   \mathrm{KT}_{e_0}(x)=\mathrm{KT}_{e_1}(x)
   \quad\text{for every }x;
   $$
2. if \(N(w)\) halts, then
   $$
   L_{e_1}(x)<L_{e_0}(x)
   $$
   for infinitely many \(x\).

**Proof.** Let the simulated branch of \(e_0\) reject every predicate query. It therefore supplies no successful description, and the literal branch gives

$$
\mathrm{KT}_{e_0}(x)
=
B_{e_0}(x)
=
|x|+O(\log |x|).
\tag{8.3}
$$

For \(e_1\), let a simulated description \(p=\operatorname{bin}(n)\) first run \(N(w)\) for \(n\) steps. If that computation has not halted, the branch rejects every query. If it has halted, the branch acts as a local decoder for

$$
x_n=1^{2^n};
\tag{8.4}
$$

It answers any requested bit of \(x_n\), as well as the end-marker query, without printing the full string. Add an ignored padding field to the code of \(e_1\) so that \(c(e_1)>c(e_0)\).

If \(N(w)\) never halts, the simulated branches of both presentations remain inert. Their shared literal construction then gives identical pointwise \(\mathrm{KT}\) values, while the smaller presentation charge makes

$$
L_{e_0}(x)<L_{e_1}(x)
$$

for every target.

Suppose instead that \(N(w)\) halts after \(s\) steps. For every \(n\geq s\), the simulated branch of \(e_1\) decodes \(x_n\) using a description of length \(O(\log n)\) and per-query time \(O(n\log n)\). Hence

$$
\mathrm{KT}_{e_1}(x_n)
\leq
O(n\log n),
$$

whereas

$$
\mathrm{KT}_{e_0}(x_n)
=
2^n+O(n).
\tag{8.5}
$$

For all sufficiently large \(n\), this gap exceeds the fixed difference \(c(e_1)-c(e_0)\), and therefore

$$
L_{e_1}(x_n)<L_{e_0}(x_n).
$$

Thus the comparison reverses on infinitely many finite serialized targets. \(\square\)

Local decoding is essential to the separation. The gated description answers any requested bit and the end-marker query in time polynomial in \(n\), even though the represented string has length \(2^n\). Requiring the machine to print the entire target would remove this gap.

## 8.3 The uniform boundary

**Theorem 8.2 (KT Presentation-Dominance).** \(\mathsf{KT\text{-}DOM}\) is \(\Pi^0_1\)-complete.

**Proof.** For membership, define the pointwise predicate

$$
Q(e_0,e_1,x)
\iff
L_{e_0}(x)\leq L_{e_1}(x).
$$

Proposition 7.1 makes \(Q\) decidable uniformly in \((e_0,e_1,x)\). Equation (8.2) therefore has the form

$$
\forall x\;Q(e_0,e_1,x)
$$

with a decidable matrix, so \(\mathsf{KT\text{-}DOM}\in\Pi^0_1\). Equivalently, its complement is computably enumerable: enumerate finite strings \(x\) and stop when one satisfies

$$
L_{e_1}(x)<L_{e_0}(x).
$$

For hardness, map \(\langle N,w\rangle\) to the pair \(\langle e_0,e_1\rangle\) constructed in Lemma 8.1. If \(N(w)\) never halts, the smaller charge makes \(e_0\) dominate \(e_1\) on every target. If \(N(w)\) halts, \(e_1\) has lower charged loss on infinitely many targets. Therefore

$$
\langle e_0,e_1\rangle
\in
\mathsf{KT\text{-}DOM}
\iff
N(w)\text{ does not halt}.
\tag{8.6}
$$

This is an effective many-one reduction from the complement of the halting problem. \(\square\)

**Corollary 8.3.** Charged dominance between any two supplied presentations is decidable on every fully enumerated finite target set. Dominance over all finite serialized targets is \(\Pi^0_1\)-complete.

The boundary is therefore

$$
\boxed{
\begin{gathered}
\text{two supplied presentations}
+\text{finitely many serialized targets}\\
\Longrightarrow
\text{decidable dominance};\\[3pt]
\text{two supplied presentations}
+\text{all finite serialized targets}\\
\Longrightarrow
\Pi^0_1\text{-complete dominance}.
\end{gathered}
}
\tag{8.7}
$$

The obstruction does not lie in evaluating a supplied target. Every such comparison terminates. It lies in certifying that no target outside every finite search conducted so far will reverse the comparison.

## 8.4 Neighbouring computability boundaries

The theorem is proved for the transparent syntactic class \(\mathcal C_{\mathrm{KT}}\), not for a class of optimal universal machines. This is substantively appropriate for bounded agents, whose presentations need not be universal. For universal machines the invariance theorem constrains the possible pointwise gaps, and the corresponding restriction requires a separate analysis. Schnorr's optimal Gödel numberings provide the natural classical comparison [34].

The result is also distinct from minimal-index theorems. For example,

$$
\mathrm{MIN}
=
\left\{
e:
\forall i<e,\;
\varphi_i\neq\varphi_e
\right\}
\tag{8.8}
$$

starts from a pairwise equivalence problem that is already nondecidable. In \(\mathsf{KT\text{-}DOM}\), by contrast, every pointwise target comparison is decidable. The \(\Pi^0_1\) obstruction arises only when those comparisons are closed under the universal quantifier over all finite targets.

## 8.5 EUH at the schema level

Let \(F(e_0,e_1)\) assert that \(e_0\) uniformly dominates \(e_1\). A target \(x\) satisfying

$$
L_{e_1}(x)<L_{e_0}(x)
$$

is a finite \(\mathsf H\)-certificate for \(F\). Its validity can be checked by the finite exhaustion procedure of Proposition 7.1.

There can be no sound effective \(\mathsf E\)-verifier that certifies every true instance of \(F\). The claims accepted by such a verifier would form a computably enumerable set; completeness and soundness would therefore make \(\mathsf{KT\text{-}DOM}\) computably enumerable, contrary to its \(\Pi^0_1\)-completeness.

A counterexample search may therefore leave a true dominance claim in \(\mathsf U\) forever. Stronger proof systems can certify particular true cases, but no fixed sound effective system certifies all of them. This is not indecision about a supplied target: every pointwise comparison terminates. It is a limit on certifying the unbounded schema, and marks the point at which the exploration and refutation strategies of *Perfect Theory* become necessary [1].

# 9. Discussion and scope

## 9.1 What the framework establishes

The framework models a kind of learning that ordinary model selection presupposes rather than explains. In ordinary inference, hypotheses disagree about values or laws stated in a common representation. Here the candidate presentations may disagree about which expressions can be formed, which generative theories can be run, and which certificates a bounded agent can obtain.

The external generator can remain fixed throughout. Learning changes the route from its signals to the agent's linguistic and generative resources. The same carrier may yield no expression under one presentation, a coarse but usable expression under another, and, under a richer generative theory, support accurate expressions for later encounters. What changes is not necessarily the world but what the agent can say and do about it.

Bayesian updating remains valid because the candidates meet at a common evidential boundary. They need not share internal expressions or translations. Each assigns a likelihood to the same packet, using its own decoder, interpreter, generative theory, and verifier. This separation is the main formal device of the paper.

The KT specialization marks a sharp limit on representational comparison. Within the effective class \(\mathcal C_{\mathrm{KT}}\), the literal ceiling and bounded local decoding make every comparison on a supplied finite serialization decidable. They do not make uniform dominance decidable. The obstruction is not an inability to evaluate a supplied target, but the impossibility of exhausting the common serialized target domain.

## 9.2 Exploration and refutation

Semantic occlusion does not specify a unique response. It supplies a diagnosis and narrows the useful actions. At the linguistic boundary, an agent may vary the apparatus, seek a different decoder, or acquire a presentation in which the carrier forms a more discriminating expression. At the generative boundary, it may search for new primitives, rules, or theories. At the operational boundary, it may change the proposal order, enlarge a derivation or verification budget, or seek an external certificate.

The EUH verdicts organize these actions without pretending that they are interchangeable. An \(\mathsf H\)-certificate supports refutation of the current theory or presentation. An \(\mathsf E\)-certificate supports a local use or commitment. A persistent \(\mathsf U\) calls for exploration: new targets, interventions, proposal procedures, reference operations, or proof systems may be more valuable than another passive observation of the same kind.

Active discovery can be formulated as Bayesian experimental design over actions that change the expected packet distribution, the expected accessibility of a resolving theory, or both. The best action need not maximize immediate confirmation. It may instead expose a disagreement between candidate-generated expressions, test whether a presumed decoding is lossy for the task, search for a short compiler, or attempt to construct a finite counterexample to a dominance claim.

Proposal remains separate from conditioning. If \(g(\mathrm de\mid W,o,z)\) is a distribution over newly constructed presentations, then an apt presentation outside the support of \(g\) cannot be discovered by that procedure. A natural research question is to characterize proposal laws for which the surprisal of an apt presentation can be bounded in terms of the structure of the observed occlusion. Bayesian conditioning evaluates addressable candidates; it does not, by itself, manufacture the language in which the missing candidate becomes addressable.

## 9.3 Carrier-relative falsification

The asymmetry between confirmation and refutation depends on the evidence carrier. For a claim \(H=\forall n\,R(n)\) with decidable \(R\), an enumerative carrier can present a finite counterexample but cannot in general present a finite witness of the universal statement. A proof-carrying apparatus may certify particular instances of \(H\). In Section 7, each threshold comparison ranges over a finite set of bounded computations, so either outcome has finite evidence. In Section 8, a single serialized target can refute dominance, whereas no sound effective verifier can certify every true uniform-dominance claim.

Falsifiability is therefore not a bare property of a sentence. It is a relation between a sentence, an admissible carrier, and a verifier [19,20,24]. The phase-sensitive case adds a further dependence: some distinctions are testable only when a reference transformation makes the relevant cross-sector observable available.

## 9.4 Relation to existing work

Statistical inference, Bayesian model selection, and causal inference study choice among represented alternatives [2–4,42]. Models of unawareness and reverse Bayesianism allow state spaces or menus of acts to expand [21–23]. Logical induction studies uncertainty about logical statements under computational limits [5]. These literatures supply important parts of the present construction, but they do not usually treat the language, observation-to-expression map, interpreter, proposal law, and verifier as one revisable object.

Work on iterated learning and identification in the limit studies the acquisition or cultural evolution of languages and hypotheses [6,46]. The linguistic examples in the introduction belong to a broader literature on how number and spatial distinctions interact with language and cognition [37–40]. The present model is more abstract: it does not propose a psycholinguistic mechanism, but asks what must be represented when the hypothesis language itself is uncertain.

Algorithmic information theory, MDL, Levin search, and time-bounded Kolmogorov complexity provide the computational specialization [7–11]. Work connecting time-bounded Kolmogorov complexity, learning, cryptography, and reductions supplies a broader meta-complexity setting [25–27]. The neighbouring computability results on optimal numberings and minimal indices clarify why the uniform-dominance theorem has its particular arithmetical complexity [34–36]. Bounded rationality explains why the constants and procedures suppressed by an extensional equivalence matter to an actual agent [45].

Institution theory studies signatures, sentences, models, satisfaction, and structure-preserving translations across logical systems [41]. It is the nearest algebraic account of semantic change. The present framework adds uncertain comparison, bounded proposal and verification, a shared packet boundary, and an explicit commitment operation. The EUH labels and double-ledger device were initially motivated by the Parseltongue and Two-Board systems [32,33]. The operator-algebraic extension draws on Morita theory, reference frames, conditional expectations, and phase-sensitive tests [12–17]. Related quantum-like models in cognition and generalized probabilistic theories offer nearby operational languages, without implying that the agents considered here require quantum hardware [28–31].

Finally, Shannon's communication model motivates the separation of source, signal, and channel [43], while the symbol-grounding problem warns that successful transmission does not settle how a token becomes meaningful for an agent [44]. Semantic occlusion begins at precisely that gap, but extends it to the generative theories and bounded procedures that become possible after an expression has been formed.

## 9.5 Limitations

Several restrictions should remain explicit.

- The opaque carrier is a modelling boundary. I do not give a general metric for semantic loss inside \(D_e\); I track only failures that affect the construction and testing of generative theories.
- The common packet space presumes a sufficiently stable apparatus to evaluate candidates on the same encounters. If the apparatus changes, its transition must be included in the candidate or the intervention.
- Hard likelihood zeros inherit the soundness of the verifier and the adequacy of the reporting model. A mistaken certificate or an undeclared noise channel can eliminate the wrong candidate.
- Candidate families are countable in the classical construction. Newly minted candidates require an explicit proposal and selection model.
- Conservative enrichment gives a monotone notion of resolving occlusions only relative to a fixed task and readout. Nonconservative change may gain distinctions while losing others.
- The phase layer is operational, not decorative: without a declared reference procedure, off-diagonal terms make no empirical difference. I do not derive how such coherence is generated between presentations.
- The KT theorem concerns a deliberately transparent syntactic class and a declared common serialization domain. It isolates a computability obstruction to uniform comparison; it is not a complete theory of natural-language expressiveness.

# 10. Conclusion

An agent may receive a signal before it possesses an adequate expression for it, and may possess an expression before it possesses a theory that can generate what comes next. I have called this condition semantic occlusion and modelled its three principal locations: the linguistic boundary, generative expressivity, and bounded access to an otherwise expressible theory.

A language presentation \(P_e=(\mathcal L_e,D_e,U_e)\) makes these locations explicit. Candidate presentations receive the same opaque packet, but form and interpret their own linguistic expressions. Their semantics remain local; their likelihoods meet at a common public boundary. Bayesian updating can therefore compare representational alternatives without assuming in advance the common language whose absence created the problem.

Reference resources may enlarge the available comparison structure by making phase-sensitive relations operational. The computational specialization exposes a different boundary. Within \(\mathcal C_{\mathrm{KT}}\), two supplied presentations can be compared on any finite serialization in the common readout domain, with finite evidence on either side. Deciding whether one charged presentation dominates another throughout that unbounded domain is \(\Pi^0_1\)-complete.

The result leaves a bounded agent with a principled but unfinished task. It can compare, refute, revise, and continue exploring. What it cannot generally do is certify that no as-yet-unexamined target could reverse the comparison and justify a different language. That is the point at which this paper hands the problem to *Perfect Theory*.

# Appendix A. Generative form

The observational and inferential cycles can be collected in the following order.

The external process produces the actual encounter. When the observation procedure returns a public record, it has one of the following forms:

$$
s_n\sim G_*(\cdot\mid z_n),
\qquad
\tau_n=E_o(s_n),
\qquad
y_n=(\hat s_n,\tau_n)\ \text{or}\ \bot.
\tag{A.1}
$$

Silence may occur without being measured; in that case no \(y_n\) is returned. For a nonsilent public packet, the opaque carrier either fails to form an expression within a candidate or enters that candidate's linguistic cycle. When \(D_e(\tau_n)\) is defined,

$$
\varphi_{e,n}=D_e(\tau_n),
\qquad
\widehat\Phi_{e,n}^{B^{\mathrm d}}
=
\operatorname{Run}_{\mathcal B_e}^{B^{\mathrm d}}
(q_e;h_{e,n},z_n),
\qquad
s_{e,n}=c_{e,B^{\mathrm v}}(\widehat\Phi_{e,n}^{B^{\mathrm d}},\varphi_{e,n}).
\tag{A.2}
$$

If \(D_e(\tau_n)\) is undefined, the candidate-local outcome is silence and \(s_{e,n}\) is not formed. The candidate uses its local construction to assign a predictive measure to the common packet:

$$
\mathbb P_e(\mathrm dy_n\mid W_n,o,z_n)
=
\int_{\Omega_e}
K_e(\mathrm dy_n\mid\omega,z_n,h_{e,n})\,\nu_e(\mathrm d\omega),
\tag{A.3}
$$

after which the weights update by (5.3). Selection is followed, if warranted, by an explicit commitment:

$$
W_{n+1}=\mathsf{Commit}_{W_n}(e,\varphi_{e,n},s_{e,n}),
\qquad
\mathcal H_{n+1}
=(\mathcal H_{n+1}^{\mathrm{sem}},\mathcal H_{n+1}^{\mathrm{ev}}).
\tag{A.4}
$$

The equations are ordered to emphasize the boundary on which the paper depends: \(\tau_n\) is passed to \(D_e\), but the agent's comparisons and commitments concern the expressions produced from it.

# Appendix B. Core notation

| Symbol | Meaning |
|---|---|
| \(G_*,s_n,z_n\) | external generator, signal, and observational context |
| \(\mathcal O_o=(\mathcal S_o,E_o,T_o)\) | signal space, encoder, and opaque carrier space of the observation interface |
| \(P_e=(\mathcal L_e,D_e,U_e)\) | language presentation |
| \(\mathcal B_{e,a}=(P_e,V_{e,a},\Lambda_{e,a})\) | bounded realization \(a\) of presentation \(e\) |
| \(\mathcal E_e=\operatorname{Expr}(\mathcal L_e)\) | expressions of presentation \(e\) |
| \(\operatorname{Cl}_{U_e}(q;h,z)\) | expressions generated by iterating the interpreter |
| \(\operatorname{Run}_{\mathcal B_e}^{B^{\mathrm d}}(q;h,z)\) | ordered expression sequence returned by one bounded derivation |
| \(R_{e,o},\mathcal X_o\) | task readout and common comparison domain |
| \(\mathsf K_{P_e},\mathsf A_{\mathcal B_{e,a}}^B\) | presentation-relative description cost and bounded-realization-relative accessibility |
| \(\Sigma=\{\mathsf E,\mathsf U,\mathsf H\}\) | local verdict algebra |
| \(\widehat\Sigma,\mathcal Y_o\) | public report alphabet and packet space |
| \(K_e\) | candidate kernel on the public packet space |
| \((\eta_e,\rho_e,m_e)\) | optional silence–carrier–report factorization of \(K_e\) |
| \(\mathbb P_e,\mathbb M\) | candidate predictive measure and prior predictive mixture |
| \(q(e),\nu_e\) | prior over presentations and within-presentation prior |
| \(\iota_e,r_e,\pi_e\) | linguistic embedding, retraction, and world projection |
| \(J_e,X_{ef},\mathfrak L_{ef}\) | reference map, cross-sector operator, and linking algebra |
| \(M_e,\mathrm{KT}_e\) | computational realization and presentation-relative KT complexity |
| \(c(e),\mathsf{KT\text{-}DOM}\) | presentation charge and uniform dominance problem |
| \(\mathcal H^{\mathrm{sem}},\mathcal H^{\mathrm{ev}}\) | semantic and evidential ledgers |

# References

1. *Perfect Theory*, companion manuscript, current draft.
2. T. S. Ferguson, “A Bayesian Analysis of Some Nonparametric Problems,” *Annals of Statistics* 1(2), 1973, 209–230.
3. P. J. Green, “Reversible Jump Markov Chain Monte Carlo Computation and Bayesian Model Determination,” *Biometrika* 82(4), 1995, 711–732.
4. R. E. Kass, A. E. Raftery, “Bayes Factors,” *Journal of the American Statistical Association* 90(430), 1995, 773–795.
5. S. Garrabrant, T. Benson-Tilsen, A. Critch, N. Soares, J. Taylor, “Logical Induction,” 2016. arXiv:1609.03543.
6. S. Kirby, H. Cornish, K. Smith, “Cumulative Cultural Evolution in the Laboratory: An Experimental Approach to the Origins of Structure in Human Language,” *Proceedings of the National Academy of Sciences USA* 105(31), 2008, 10681–10686.
7. P. D. Grünwald, P. M. B. Vitányi, “Algorithmic Information Theory,” 2008.
8. L. A. Levin, “Universal Sequential Search Problems,” *Problems of Information Transmission* 9(3), 1973.
9. P. M. B. Vitányi, M. Li, “Minimum Description Length Induction, Bayesianism, and Kolmogorov Complexity,” *IEEE Transactions on Information Theory* 46(2), 2000, 446–464.
10. J. Schmidhuber, “Driven by Compression Progress,” 2009. arXiv:0812.4360.
11. E. Allender, H. Buhrman, M. Koucký, D. van Melkebeek, D. Ronneburger, “Power from Random Strings,” *SIAM Journal on Computing* 35(6), 2006, 1467–1493.
12. M. A. Rieffel, “Morita Equivalence for Operator Algebras,” 1982.
13. L. G. Brown, P. Green, M. A. Rieffel, “Stable Isomorphism and Strong Morita Equivalence of \(C^*\)-Algebras,” *Pacific Journal of Mathematics* 71(2), 1977, 349–363.
14. S. D. Bartlett, T. Rudolph, R. W. Spekkens, “Reference Frames, Superselection Rules, and Quantum Information,” *Reviews of Modern Physics* 79, 2007, 555–609.
15. A. J. Leggett, A. Garg, “Quantum Mechanics versus Macroscopic Realism: Is the Flux There when Nobody Looks?,” *Physical Review Letters* 54, 1985, 857–860.
16. J. Tomiyama, “On the Projection of Norm One in \(W^*\)-Algebras,” *Proceedings of the Japan Academy* 33, 1957, 608–612.
17. M. Takesaki, “Conditional Expectations in von Neumann Algebras,” *Journal of Functional Analysis* 9(3), 1972, 306–321.
18. D. B. Rubin, “Inference and Missing Data,” *Biometrika* 63(3), 1976, 581–592.
19. K. R. Popper, *The Logic of Scientific Discovery*, Hutchinson, 1959.
20. D. G. Mayo, *Statistical Inference as Severe Testing*, Cambridge University Press, 2018.
21. E. Karni, M.-L. Vierø, “Reverse Bayesianism: A Choice-Based Theory of Growing Awareness,” *American Economic Review* 103(7), 2013, 2790–2810.
22. A. Heifetz, M. Meier, B. C. Schipper, “Interactive Unawareness,” *Journal of Economic Theory* 130(1), 2006, 78–94.
23. E. Dekel, B. L. Lipman, A. Rustichini, “Standard State-Space Models Preclude Unawareness,” *Econometrica* 66(1), 1998, 159–173.
24. I. Lakatos, “Falsification and the Methodology of Scientific Research Programmes,” in *Criticism and the Growth of Knowledge*, Cambridge University Press, 1970.
25. M. Carmosino, R. Impagliazzo, V. Kabanets, A. Kolokolova, “Learning Algorithms from Natural Proofs,” *CCC*, 2016.
26. Y. Liu, R. Pass, “On One-Way Functions and Kolmogorov Complexity,” *FOCS*, 2020.
27. S. Hirahara, “Non-Black-Box Worst-Case to Average-Case Reductions within NP,” *FOCS*, 2018.
28. J. R. Busemeyer, P. D. Bruza, *Quantum Models of Cognition and Decision*, Cambridge University Press, 2012; Z. Wang, J. R. Busemeyer, “A Quantum Question Order Model Supported by Empirical Tests of an A Priori and Precise Prediction,” *Topics in Cognitive Science* 5(4), 2013, 689–710.
29. C. A. Fuchs, R. Schack, “Quantum-Bayesian Coherence,” *Reviews of Modern Physics* 85, 2013, 1693–1715.
30. J. Barrett, “Information Processing in Generalized Probabilistic Theories,” *Physical Review A* 75, 2007, 032304.
31. D. Schmid, J. H. Selby, M. F. Pusey, R. W. Spekkens, “A Structure Theorem for Generalized-Noncontextual Ontological Models,” 2020. arXiv:2005.07161.
32. *Parseltongue*. <https://github.com/sci2sci-opensource/parseltongue>.
33. *The Two-Board Problem*. <https://github.com/sci2sci-opensource/research>.
34. C. P. Schnorr, “Optimal Enumerations and Optimal Gödel Numberings,” *Mathematical Systems Theory* 8(2), 1975, 182–191.
35. A. R. Meyer, “Program Size in Restricted Programming Languages,” *Information and Control* 21(4), 1972, 382–394.
36. J. Teutsch, “On the Turing Degrees of Minimal Index Sets,” *Annals of Pure and Applied Logic* 148(1–3), 2007, 63–80.
37. P. Gordon, “Numerical Cognition Without Words: Evidence from Amazonia,” *Science* 306(5695), 2004, 496–499.
38. M. C. Frank, D. L. Everett, E. Fedorenko, E. Gibson, “Number as a Cognitive Technology: Evidence from Pirahã Language and Cognition,” *Cognition* 108(3), 2008, 819–824.
39. E. Pederson, E. Danziger, D. G. Wilkins, S. C. Levinson, S. Kita, G. Senft, “Semantic Typology and Spatial Conceptualization,” *Language* 74(3), 1998, 557–589.
40. S. C. Levinson, S. Kita, D. B. M. Haun, B. H. Rasch, “Returning the Tables: Language Affects Spatial Reasoning,” *Cognition* 84(2), 2002, 155–188.
41. J. A. Goguen, R. M. Burstall, “Institutions: Abstract Model Theory for Specification and Programming,” *Journal of the ACM* 39(1), 1992, 95–146.
42. J. Pearl, *Causality: Models, Reasoning, and Inference*, 2nd ed., Cambridge University Press, 2009.
43. C. E. Shannon, “A Mathematical Theory of Communication,” *Bell System Technical Journal* 27, 1948, 379–423 and 623–656.
44. S. Harnad, “The Symbol Grounding Problem,” *Physica D* 42, 1990, 335–346.
45. H. A. Simon, “A Behavioral Model of Rational Choice,” *Quarterly Journal of Economics* 69(1), 1955, 99–118.
46. E. M. Gold, “Language Identification in the Limit,” *Information and Control* 10(5), 1967, 447–474.
47. J. Stillwell, *Mathematics and Its History*, 3rd ed., Springer, 2010.
48. S. Abramsky, A. Brandenburger, “The Sheaf-Theoretic Structure of Non-Locality and Contextuality,” *New Journal of Physics* 13, 2011, 113036.
49. S. Abramsky, R. S. Barbosa, S. Mansfield, “The Contextual Fraction as a Measure of Contextuality,” *Physical Review Letters* 119, 2017, 050504.
50. R. Uola, T. Moroder, O. Gühne, “Joint Measurability of Generalized Measurements Implies Classicality,” *Physical Review Letters* 113, 2014, 160403.
51. S. C. Kleene, *Introduction to Metamathematics*, North-Holland, 1952.
52. S. Popa, “Relative Dimension, Towers of Projections and Commuting Squares of Subfactors,” *Pacific Journal of Mathematics* 137(1), 1989, 181–207.
53. *Universal Language Learning Machine*, companion manuscript, current draft.
