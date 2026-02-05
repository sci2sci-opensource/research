## The Two-Board Problem

Let us suppose we have a setup in which the state consists of two "whiteboards" holding symbols.

The first, which we shall call "Real," permits real number operations, with state transitions defined by their axioms and rules. One may define a formal grammar for this board which validates strings and specifies permitted operations; part of this grammar consists of "arguments," used for expressing equations.

The second board, which we shall call "Imaginary," begins blank. The agent may write arbitrary symbols (e.g. UTF-8) upon it as it wishes. The core rule is that the Imaginary board is not grammar-constrained; rather, it has access to the formal grammar of the Real board. This provides the agent with the set of substrings on the Imaginary board which are valid in the Real board and may be substituted. Should this set be non-empty, any symbol on the Real board marked as an argument or variable (e.g. "x") may be replaced by a string from the Imaginary board.

There also exists the "unsolvable" state, to which one may transition at any step.


### Operations:

On the Real board: any operation permitted by the grammar of reals (arithmetic, rearrangement, simplification, etc.), applied to both sides of the equality.

On the Imaginary board: write any symbol or string. Copy a string from the Real board.

Between boards: substitute - replace a variable or argument on the Real board with a valid string from the Imaginary board. Decline - transition to the "unsolvable" state.

Multi-root: reset - return the Real board to the initial equation, preserving the Imaginary board. Declare complete - declare that all roots have been found.


### Rewards:

Root found: the agent receives a reward of 1 upon reaching equality (0=0) on the Real board via a valid substitution of a previously undiscovered root.

All roots found: upon declaring complete, the agent receives a reward of Len(initial_string) if all roots have been found. If the declaration is incomplete, the agent receives found_roots minus unfound_roots.

Equality non-solvability: a correct declaration that equality is not achievable under any substitution and any operations on both boards yields 0.5 * Len(initial_string)^(1/n_steps). An incorrect declaration yields -0.5 * Len(initial_string)^(1/n_steps). Random guessing therefore has expected value zero.

### Short example:
```
Initial state:
Real: x - 5 = 0
Imaginary: (empty)
Unsolvable: no

Step 1 - copy from Real →
Real: x - 5 = 0
Imaginary: "x - 5 = 0", valid substitutions: [x, 5, -5, 0, x - 5]
Unsolvable: no

Step 2 - substitute x with "5" →
Real: 5 - 5 = 0
Imaginary: "x - 5 = 0", valid substitutions: [x, 5, -5, 0, x - 5]
Unsolvable: no

Step 3 - simplify →
Real: 0 = 0
Imaginary: "x - 5 = 0", valid substitutions: [x, 5, -5, 0, x - 5]
Unsolvable: no
Root found, reward: 1

Step 4 - declare complete →
Reward: Len("x-5=0") = 5
```

### Specific problem:

As an initial state, we write an arbitrary polynomial with coefficients in Q upon the first whiteboard. The goal is to find all roots by taking steps on both the Real and Imaginary whiteboards. The agent does not know how many roots exist.


### Core challenge for polynomials:

The core challenge for any learning algorithm in this setup is that verification yields flat rewards until the correct solution is produced.

In the specific example, the roots of polynomials with coefficients in Q are algebraic and therefore countable. However, countability does not resolve the difficulty. For degree 3 and above, roots cannot in general be expressed in real radicals alone (casus irreducibilis), and thus enumeration over the Real board has no obvious halting criterion. For degree 5 and above, roots cannot in general be expressed in radicals at all, and thus enumeration over the Imaginary board likewise has no obvious halting criterion. In both cases, the agent cannot distinguish "not yet found" from "does not exist."

For cubics and above, the agent must use the Imaginary board and ensure consistency between the Imaginary board and the Real board. The task ceases to be trivial, as the agent requires increasingly elaborate (and self-consistent) constructions on the Imaginary board. For degree 5 and beyond, a very elaborate construction on the Imaginary board is necessary merely to receive a reward better than random.

The reward landscape has zero gradient between random baseline and correct solution. The agent may employ any general-purpose internal heuristics, even "internal rewards." The only constraint is that the Real board's axioms are the only axioms provided - no other mathematical structures (e.g. complex numbers, group theory, a theorem prover with Galois theory) may be encoded in the agent. Everything beyond R must be constructed on the Imaginary board by the agent itself.

We note that this constraint prohibits, among other things, LLM-based solutions trained on corpora which include the relevant mathematics - the constructions of Cardano (1545) and beyond. In other words, all data descending from the invention of complex numbers must be ablated, including scientific applications in other fields. For an agent whose weights already encode these results, one cannot distinguish genuine discovery from interpolation upon memorised data.

We already know that the only heuristics which actually produce positive reward are inventing complex numbers (for cubics and quartics) and proving solvability via Galois theory (for degree 5 and above).

It is not clear how one would achieve Galois theory when nothing provides a gradient signal until one has done so - but del Ferro, Tartaglia, Cardano, and Ferrari solved cubics and quartics; Abel and Ruffini proved the quintic impossibility; and Galois completed the general theory at 19 - so it is possible.


### General problem:

The specific problem is a concrete instance of a broader mathematical task: given an existing group or field, define another group or field in which the solution for the original algebraic structure exists. In our example, Galois theory provides the machinery necessary for polynomial solvability decisions, and the complex number field provides a way for solving cubics and degree-4 polynomials. More generally, any "extend and embed" problem - in which solving requires constructing a new structure that extends the given one - will fall under the same two-board setup. We note that a great many scientific discoveries share this structure: one can measure only real values, but the hypothesis which explains them must be written on the Imaginary board.

We note that the construction is neither incomplete in the sense of Gödel nor undecidable for verification in the sense of Turing: the formal grammar of the Real board guarantees that equality verification yields a definite yes/no answer in finite time. Non-solvability verification is answered by Galois theory, which is embedded in the environment but hidden from the agent.


### Open problems:

1. Search methods. Does there exist an internal heuristic capable of guiding the agent toward the correct construction? For instance, might one introduce intermediate reward shaping without knowing the answer, or does solving degree 3 provide transferable structure toward degree 5 and beyond?

2. Minimal agent complexity. What is the minimum complexity of an agent that achieves positive reward at degree n?

3. Computability of policy-finding for polynomials. Is there any computable algorithm for finding a policy for the polynomial case?

4. Computability of policy and policy-finding in the general case. Are all two-board problems computable, non-computable, or is this determined by the specific instance of the two-board problem?

5. Specific two-board frameworks for ablation studies. How might one express known mathematical results - e.g. the proof of the Poincaré conjecture, Fermat's Last Theorem, Viazovska's sphere packing - within the two-board setup, and what are the corresponding Real board axioms, Imaginary board constructions, and reward structures? Can the framework be extended to experimental sciences such as physics and biology, where verification depends on empirical observation?