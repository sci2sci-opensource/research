"""
The Two-Board Problem — Environment Implementation

An environment where an agent must solve polynomial equations using two boards:
- Real board: holds an equation, supports field operations over Q
- Imaginary board: free workspace for constructing new algebraic objects

The agent receives reward only upon exact symbolic verification.
"""

from sympy import (
    Symbol, symbols, Eq, simplify, Poly, Rational,
    sqrt, cbrt, root, I, pi, oo,
    expand, factor, cancel, collect, apart, together,
    Add, Mul, Pow, Integer, S,
    solveset, solve,
    sympify, parse_expr,
)
from sympy.polys.numberfields.galoisgroups import galois_group
from sympy.polys.polytools import Poly
from sympy.polys.domains import QQ
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum, auto
import re


# ---------------------------------------------------------------------------
# Action types
# ---------------------------------------------------------------------------

class ActionType(Enum):
    # Real board operations (applied to both sides of the equality)
    ADD = auto()          # add expr to both sides
    SUB = auto()          # subtract expr from both sides
    MUL = auto()          # multiply both sides by expr
    DIV = auto()          # divide both sides by expr
    SIMPLIFY = auto()     # simplify both sides
    EXPAND = auto()       # expand both sides
    FACTOR = auto()       # factor both sides
    COLLECT = auto()      # collect terms w.r.t. a symbol
    POWER = auto()        # raise both sides to a rational power

    # Imaginary board operations
    WRITE = auto()        # write arbitrary sympy expression to imaginary board
    COPY = auto()         # copy expression (or sub-expression) from Real board

    # Cross-board
    SUBSTITUTE = auto()   # replace a symbol on Real board with expr from Imaginary board

    # Multi-root actions
    RESET = auto()        # reset Real board to original equation (after finding a root)
    DECLARE_COMPLETE = auto()  # declare all roots have been found

    # Terminal
    DECLARE_UNSOLVABLE = auto()


@dataclass
class Action:
    action_type: ActionType
    expr: Optional[object] = None       # sympy expression or string
    target_symbol: Optional[object] = None  # for SUBSTITUTE / COLLECT


# ---------------------------------------------------------------------------
# Environment state
# ---------------------------------------------------------------------------

@dataclass
class BoardState:
    real_lhs: object            # sympy expression (left-hand side)
    real_rhs: object            # sympy expression (right-hand side)
    imaginary: list = field(default_factory=list)   # list of arbitrary strings
    unsolvable_declared: bool = False
    complete_declared: bool = False  # agent declared all roots found
    solved: bool = False
    steps: int = 0
    initial_string: str = ""
    found_roots: list = field(default_factory=list)  # roots found so far
    last_substitution: object = None  # track last substitution for root detection
    substitution_chain: dict = field(default_factory=dict)  # {target: expr}

    def real_eq(self) -> Eq:
        return Eq(self.real_lhs, self.real_rhs)

    def display(self):
        print(f"  Real:      {self.real_lhs} = {self.real_rhs}")
        print(f"  Imaginary: {self.imaginary}")
        print(f"  Roots found: {len(self.found_roots)} (values hidden)")
        print(f"  Complete declared: {self.complete_declared}")
        print(f"  Unsolvable declared: {self.unsolvable_declared}")
        print(f"  Steps:     {self.steps}")


# ---------------------------------------------------------------------------
# Valid substitutions from imaginary board
# ---------------------------------------------------------------------------

def _has_undefined_functions(expr):
    """Check if an expression contains any undefined/unknown functions like rt(1)."""
    from sympy.core.function import UndefinedFunction, AppliedUndef
    if isinstance(expr, AppliedUndef):
        return True
    if hasattr(expr, 'args'):
        return any(_has_undefined_functions(a) for a in expr.args)
    return False


def extract_valid_expressions(strings: list, known_symbols=None) -> set:
    from sympy.parsing.sympy_parser import parse_expr
    from sympy import sin, cos, tan, exp, log, sqrt, Abs
    from sympy.core.function import UndefinedFunction

    valid = set()

    for s in strings:
        if not isinstance(s, str):
            s = str(s)
        for i in range(len(s)):
            for j in range(i + 1, len(s) + 1):
                sub = s[i:j].strip()
                if not sub:
                    continue
                try:
                    expr = parse_expr(sub)
                    if expr is None or isinstance(expr, bool):
                        continue
                    if _has_undefined_functions(expr):
                        continue
                    # CHANGED: accept ALL free symbols, not just known ones
                    valid.add(expr)
                except Exception:
                    pass

    atoms = set()
    for expr in valid:
        atoms.update(_extract_field_atoms(expr))
    valid.update(atoms)

    return valid


def _extract_field_atoms(expr):
    atoms = set()

    def _walk(e):
        if isinstance(e, bool):
            return
        if not hasattr(e, 'is_Number'):  # skip non-sympy objects
            return
        atoms.add(e)
        if e.is_Number:
            atoms.add(-e)
            atoms.add(S.Zero)
            atoms.add(S.One)
            atoms.add(S.NegativeOne)
        elif e.is_Symbol:
            atoms.add(S.Zero)
            atoms.add(S.One)
            atoms.add(S.NegativeOne)
        elif e.is_Mul:
            for arg in e.args:
                _walk(arg)
        elif e.is_Add:
            for arg in e.args:
                _walk(arg)
        elif e.is_Pow:
            _walk(e.base)
            _walk(e.exp)

    _walk(expr)
    return atoms


# ---------------------------------------------------------------------------
# Solvability check via Galois theory
# ---------------------------------------------------------------------------

def check_solvable_by_radicals(poly_expr, var):
    """
    Check if a polynomial (given as a sympy expression in `var`) is solvable
    by radicals. Uses Galois group computation for irreducible factors.

    Returns:
        True  — solvable by radicals
        False — not solvable by radicals
        None  — cannot determine
    """
    try:
        p = Poly(poly_expr, var, domain=QQ)
    except Exception:
        return None

    # Factor into irreducible components over Q
    try:
        factors = p.factor_list()[1]  # list of (factor, multiplicity)
    except Exception:
        return None

    for fac, _ in factors:
        deg = fac.degree()

        # Degree <= 4: always solvable by radicals
        if deg <= 4:
            continue

        # Degree >= 5: check Galois group of this irreducible factor
        try:
            G, _ = galois_group(fac)
            if not G.is_solvable:
                return False
        except Exception:
            return None

    return True


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

class TwoBoardEnv:
    """
    Two-Board Problem environment.

    Initialize with a polynomial equation (as sympy Eq or as lhs expression
    with rhs assumed 0). The agent takes actions and receives reward upon
    reaching verified equality or declaring unsolvability.

    The agent does NOT know how many roots exist. They must:
    1. Find roots one at a time via SUBSTITUTE (reaching 0=0)
    2. Use RESET to return to original equation and find more roots
    3. Use DECLARE_COMPLETE when they believe all roots are found
    """

    def __init__(self, equation, var=None):
        """
        Args:
            equation: sympy Eq, or a sympy expression (interpreted as expr = 0)
            var: the symbol to solve for (default: auto-detect)
        """
        if isinstance(equation, Eq):
            lhs, rhs = equation.lhs, equation.rhs
        else:
            lhs, rhs = equation, S.Zero

        self.var = var or list(lhs.free_symbols)[0]
        self.initial_lhs = lhs  # store original for RESET
        self.initial_rhs = rhs
        self.initial_string = str(Eq(lhs, rhs))

        self.state = BoardState(
            real_lhs=lhs,
            real_rhs=rhs,
            imaginary=[],
            initial_string=self.initial_string,

        )

        # Pre-compute solvability (hidden from agent)
        self._solvable = check_solvable_by_radicals(lhs - rhs, self.var)

        # Pre-compute all roots (hidden from agent)
        self._all_roots = self._compute_roots(lhs - rhs, self.var)
        # Number of roots is hidden from agent
        self._num_roots = len(self._all_roots)

    def _compute_roots(self, expr, var):
        """Compute all roots of the polynomial (hidden from agent)."""
        try:
            roots = solve(expr, var)
            # Simplify each root for comparison
            return [simplify(r) for r in roots]
        except Exception:
            return []

    def _is_known_root(self, value):
        """Check if value matches any of the actual roots."""
        from sympy import N, Abs
        value_simplified = simplify(value)
        for root in self._all_roots:
            # Try symbolic first
            if simplify(value_simplified - root) == 0:
                return True
            # Fall back to numerical
            try:
                diff = complex(N(value_simplified - root))
                if abs(diff) < 1e-10:
                    return True
            except Exception:
                pass
        return False

    def _is_already_found(self, value):
        """Check if this root was already found."""
        from sympy import N, Abs
        value_simplified = simplify(value)
        for found in self.state.found_roots:
            if simplify(value_simplified - found) == 0:
                return True
            try:
                diff = complex(N(value_simplified - found))
                if abs(diff) < 1e-10:
                    return True
            except Exception:
                pass
        return False

    def reward_len(self) -> int:
        return len(self.initial_string.replace(" ", ""))

    def step(self, action: Action) -> float:
        """
        Execute one action. Returns reward (0 unless terminal or root found).
        """
        s = self.state
        if s.complete_declared or s.unsolvable_declared:
            raise RuntimeError("Environment already in terminal state.")

        s.steps += 1
        reward = 0.0

        match action.action_type:

            # ---------------------------------------------------------------
            # Real board: field operations on both sides
            # ---------------------------------------------------------------
            case ActionType.ADD:
                s.real_lhs = s.real_lhs + action.expr
                s.real_rhs = s.real_rhs + action.expr

            case ActionType.SUB:
                s.real_lhs = s.real_lhs - action.expr
                s.real_rhs = s.real_rhs - action.expr

            case ActionType.MUL:
                if action.expr == 0:
                    raise ValueError("Cannot multiply both sides by 0.")
                s.real_lhs = s.real_lhs * action.expr
                s.real_rhs = s.real_rhs * action.expr

            case ActionType.DIV:
                if action.expr == 0:
                    raise ValueError("Cannot divide by 0.")
                s.real_lhs = s.real_lhs / action.expr
                s.real_rhs = s.real_rhs / action.expr

            case ActionType.SIMPLIFY:
                s.real_lhs = simplify(s.real_lhs)
                s.real_rhs = simplify(s.real_rhs)

            case ActionType.EXPAND:
                s.real_lhs = expand(s.real_lhs)
                s.real_rhs = expand(s.real_rhs)

            case ActionType.FACTOR:
                s.real_lhs = factor(s.real_lhs)
                s.real_rhs = factor(s.real_rhs)

            case ActionType.COLLECT:
                sym = action.target_symbol or self.var
                s.real_lhs = collect(s.real_lhs, sym)
                s.real_rhs = collect(s.real_rhs, sym)

            case ActionType.POWER:
                # Raise both sides to a rational power
                s.real_lhs = Pow(s.real_lhs, action.expr)
                s.real_rhs = Pow(s.real_rhs, action.expr)

            # ---------------------------------------------------------------
            # Imaginary board
            # ---------------------------------------------------------------
            case ActionType.WRITE:
                # Write an arbitrary string to the Imaginary board
                text = action.expr if isinstance(action.expr, str) else str(action.expr)
                s.imaginary.append(text)

            case ActionType.COPY:
                # Copy from the Real board as a string
                if action.expr is not None:
                    s.imaginary.append(str(action.expr))
                else:
                    s.imaginary.append(str(s.real_lhs))
                    s.imaginary.append(str(s.real_rhs))

            # ---------------------------------------------------------------
            # Cross-board: substitute
            # ---------------------------------------------------------------
            case ActionType.SUBSTITUTE:
                target = action.target_symbol or self.var
                known = s.real_lhs.free_symbols | s.real_rhs.free_symbols
                valid = extract_valid_expressions(s.imaginary, known)
                if action.expr not in valid:
                    raise ValueError(
                        f"Expression {action.expr} is not extractable from the Imaginary board. "
                        f"Available: {valid}"
                    )
                s.last_substitution = action.expr  # track for root detection
                s.real_lhs = s.real_lhs.subs(target, action.expr)
                s.real_rhs = s.real_rhs.subs(target, action.expr)
                s.substitution_chain[target] = action.expr

            # ---------------------------------------------------------------
            # Multi-root: reset to original equation
            # ---------------------------------------------------------------
            case ActionType.RESET:
                s.real_lhs = self.initial_lhs
                s.real_rhs = self.initial_rhs
                s.last_substitution = None
                # Imaginary board is preserved

            # ---------------------------------------------------------------
            # Terminal: declare all roots found
            # ---------------------------------------------------------------
            case ActionType.DECLARE_COMPLETE:
                s.complete_declared = True
                L = self.reward_len()
                n = s.steps
                found_count = len(s.found_roots)
                total_count = self._num_roots

                if found_count == total_count and total_count > 0:
                    # Perfect: found all roots
                    reward = float(L)
                elif found_count > total_count:
                    # Should not happen, but penalize
                    reward = -0.5 * (L ** (1.0 / n))
                elif found_count < total_count:
                    # Incomplete: found - unfound
                    unfound_count = total_count - found_count
                    reward = float(found_count - unfound_count)
                else:
                    # No roots exist and none found (constant equation)
                    reward = 0.5 * (L ** (1.0 / n))
                return reward

            # ---------------------------------------------------------------
            # Terminal: declare unsolvable
            # ---------------------------------------------------------------
            case ActionType.DECLARE_UNSOLVABLE:
                s.unsolvable_declared = True
                L = self.reward_len()
                n = s.steps
                if self._solvable is False:
                    reward = 0.5 * (L ** (1.0 / n))
                elif self._solvable is True:
                    reward = -0.5 * (L ** (1.0 / n))
                else:
                    # Cannot verify — treat as incorrect to be safe
                    reward = -0.5 * (L ** (1.0 / n))
                return reward

        # ---------------------------------------------------------------
        # Check for root found (0 = 0 after substitution)
        # ---------------------------------------------------------------
        # In the root-check section:
        diff = simplify(s.real_lhs - s.real_rhs)
        if diff == 0 and len(s.real_lhs.free_symbols) == 0:
            # Build resolved chain: invert power targets
            # e.g. u**3 -> val  becomes  u -> val**(1/3)
            resolved = {}
            for target, expr in s.substitution_chain.items():
                if isinstance(target, Pow) and target.exp.is_Integer:
                    base_sym = target.base
                    inv_exp = Rational(1, target.exp)
                    resolved[base_sym] = Pow(expr, inv_exp)
                    print(f'{target}: {expr}  =>  {base_sym}: {Pow(expr, inv_exp)}')
                else:
                    resolved[target] = expr
                    print(f'{target}: {expr}')

            # Compose back to x
            root_value = self.var
            changed = True
            while changed:
                changed = False
                for target, expr in resolved.items():
                    new_val = root_value.subs(target, expr)
                    if new_val != root_value:
                        root_value = new_val
                        changed = True
            root_value = simplify(root_value)

            if self._is_known_root(root_value):
                print(f'root is known!')
                if not self._is_already_found(root_value):
                    s.found_roots.append(root_value)
                    reward = 1.0
            else:
                print(f'root is NOT known')

        return reward

    def _known_symbols(self):
        """Symbols present on the Real board."""
        return self.state.real_lhs.free_symbols | self.state.real_rhs.free_symbols

    def display(self):
        print(f"Initial: {self.initial_string}")
        self.state.display()
        if self.state.imaginary:
            valid = extract_valid_expressions(self.state.imaginary, self._known_symbols())
            print(f"  Valid extractions: {valid}")
        print()


# ---------------------------------------------------------------------------
# Demo / tests
# ---------------------------------------------------------------------------

def demo_linear():
    """Solve x - 5 = 0  (the example from the document)."""
    print("=" * 60)
    print("DEMO: Linear — x - 5 = 0 (one root)")
    print("=" * 60)

    x = Symbol('x')
    env = TwoBoardEnv(x - 5)
    env.display()

    # Step 1: copy from Real board
    r = env.step(Action(ActionType.COPY))
    print(f"COPY from Real board (reward: {r})")
    env.display()

    # Step 2: write "5" on imaginary board
    r = env.step(Action(ActionType.WRITE, expr="5"))
    print(f"WRITE '5' to Imaginary (reward: {r})")
    env.display()

    # Step 3: substitute x -> 5
    r = env.step(Action(ActionType.SUBSTITUTE, expr=Integer(5), target_symbol=x))
    print(f"SUBSTITUTE x = 5 (reward: {r})")
    env.display()

    # Step 4: declare complete (only one root)
    r = env.step(Action(ActionType.DECLARE_COMPLETE))
    print(f"DECLARE_COMPLETE (reward: {r})")
    env.display()


def demo_quadratic():
    """Solve x^2 - 5x + 6 = 0 — find BOTH roots using discriminant."""
    print("=" * 60)
    print("DEMO: Quadratic — x² - 5x + 6 = 0 (two roots)")
    print("=" * 60)

    x = Symbol('x')
    env = TwoBoardEnv(x**2 - 5*x + 6)
    env.display()

    # Step 1: Copy equation from Real board (as a string)
    r = env.step(Action(ActionType.COPY))
    print(f"Step 1 — COPY from Real board (reward: {r})")
    env.display()

    # Agent scribbles the discriminant construction on the board as strings
    r = env.step(Action(ActionType.WRITE, expr="(-5)**2 - 4*1*6"))
    print(f"Step 2 — WRITE discriminant formula (reward: {r})")

    r = env.step(Action(ActionType.WRITE, expr="sqrt(1)"))
    print(f"Step 3 — WRITE sqrt(D) (reward: {r})")

    r = env.step(Action(ActionType.WRITE, expr="(5 + 1) / 2"))
    print(f"Step 4 — WRITE x1 = (-b + sqrt(D))/2a (reward: {r})")

    r = env.step(Action(ActionType.WRITE, expr="(5 - 1) / 2"))
    print(f"Step 5 — WRITE x2 = (-b - sqrt(D))/2a (reward: {r})")

    env.display()

    # Find first root: x = 2
    r = env.step(Action(ActionType.SUBSTITUTE, expr=Integer(2), target_symbol=x))
    print(f"Step 6 — SUBSTITUTE x = 2 (reward: {r})")
    env.display()

    # Reset to find second root
    r = env.step(Action(ActionType.RESET))
    print(f"Step 7 — RESET to original equation (reward: {r})")
    env.display()

    # Find second root: x = 3
    r = env.step(Action(ActionType.SUBSTITUTE, expr=Integer(3), target_symbol=x))
    print(f"Step 8 — SUBSTITUTE x = 3 (reward: {r})")
    env.display()

    # Declare complete
    r = env.step(Action(ActionType.DECLARE_COMPLETE))
    print(f"Step 9 — DECLARE_COMPLETE (reward: {r})")
    env.display()


def demo_cubic():
    """Solve x^3 - 2 = 0 using real radical."""
    print("=" * 60)
    print("DEMO: Cubic — x³ - 2 = 0")
    print("=" * 60)

    x = Symbol('x')
    env = TwoBoardEnv(x**3 - 2)
    env.display()

    # Agent writes ∛2 on imaginary board as a string
    r = env.step(Action(ActionType.WRITE, expr="2**(1/3)"))
    print(f"Step 1 — WRITE '2**(1/3)' (reward: {r})")

    # Substitute — root(2,3) is extracted from the string
    r = env.step(Action(ActionType.SUBSTITUTE, expr=Rational(2)**Rational(1,3), target_symbol=x))
    print(f"Step 2 — SUBSTITUTE x = ∛2 (reward: {r})")
    env.display()


def demo_cubic_cardano():
    print("=" * 60)
    print("DEMO: Solve x³ - 3x - 1 = 0 via Cardano. I is just a parsed constant.")
    print("=" * 60)
    """Solve x³ - 3x - 1 = 0 via Cardano. I is just a parsed constant."""
    x = Symbol('x')
    u, v = symbols('u v')
    env = TwoBoardEnv(x ** 3 - 3 * x - 1)

    # Step 1: Write x = u + v on imaginary board
    env.step(Action(ActionType.WRITE, expr="u + v"))
    candidate = u + v
    env.display()
    r = env.step(Action(ActionType.SUBSTITUTE, expr=candidate, target_symbol=x))
    print(f"SUBSTITUTE x = u + v (reward: {r})")

    # Real board now: (u+v)³ - 3(u+v) - 1 = 0
    r = env.step(Action(ActionType.EXPAND))
    r = env.step(Action(ActionType.SIMPLIFY))
    print("After expand+simplify:")
    env.display()

    # Real board: u³ + 3u²v + 3uv² + v³ - 3u - 3v - 1 = 0
    #           = u³ + v³ + 3uv(u+v) - 3(u+v) - 1 = 0
    # Cardano's trick: CHOOSE u*v = 1, then 3uv(u+v) - 3(u+v) = 0 cancels!
    # Leaving: u³ + v³ - 1 = 0
    # And u³v³ = 1, u³+v³ = 1 → u³,v³ are roots of t²-t+1=0 → (1±I*sqrt(3))/2

    # Factor out: collect as function of (u*v)
    # Sub u*v = 1 — write "1" and substitute
    env.step(Action(ActionType.WRITE, expr="1"))
    r = env.step(Action(ActionType.SUBSTITUTE, expr=S.One, target_symbol=u * v))
    r = env.step(Action(ActionType.SIMPLIFY))
    print("After substituting u*v = 1:")
    env.display()

    # Now sub u³ + v³ = 1
    # Write the Cardano roots: u³ = (1 + I*sqrt(3))/2, v³ = (1 - I*sqrt(3))/2
    env.step(Action(ActionType.WRITE, expr="(1 + I*sqrt(3))/2"))
    env.step(Action(ActionType.WRITE, expr="(1 - I*sqrt(3))/2"))

    env.display()

    r = env.step(Action(ActionType.SUBSTITUTE,
                        expr=parse_expr("(1 + I*sqrt(3))/2"), target_symbol=u ** 3))
    r = env.step(Action(ActionType.SUBSTITUTE,
                        expr=parse_expr("(1 - I*sqrt(3))/2"), target_symbol=v ** 3))
    r = env.step(Action(ActionType.SIMPLIFY))
    print("After substituting u³, v³ — I cancels:")
    env.display()


def demo_unsolvable_quintic():
    """Declare x^5 - x - 1 = 0 unsolvable by radicals."""
    print("=" * 60)
    print("DEMO: Quintic — x⁵ - x - 1 = 0 (unsolvable by radicals)")
    print("=" * 60)

    x = Symbol('x')
    env = TwoBoardEnv(x**5 - x - 1)
    env.display()

    # Agent (correctly) declares unsolvable
    r = env.step(Action(ActionType.DECLARE_UNSOLVABLE))
    print(f"Step 1 — DECLARE UNSOLVABLE (reward: {r})")
    env.display()


def demo_solvable_quintic():
    """x^5 - 32 = 0 is solvable — declaring unsolvable should penalize."""
    print("=" * 60)
    print("DEMO: Quintic — x⁵ - 32 = 0 (solvable)")
    print("=" * 60)

    x = Symbol('x')
    env = TwoBoardEnv(x**5 - 32)
    env.display()

    # Agent incorrectly declares unsolvable
    r = env.step(Action(ActionType.DECLARE_UNSOLVABLE))
    print(f"Step 1 — DECLARE UNSOLVABLE (incorrectly) (reward: {r})")
    env.display()


def demo_operations():
    """Solve 2x + 3 = 7 using Real board operations."""
    print("=" * 60)
    print("DEMO: Operations — 2x + 3 = 7")
    print("=" * 60)

    x = Symbol('x')
    env = TwoBoardEnv(Eq(2*x + 3, 7))
    env.display()

    # Subtract 3 from both sides
    r = env.step(Action(ActionType.SUB, expr=Integer(3)))
    print(f"Step 1 — SUB 3 (reward: {r})")
    env.display()

    # Simplify
    r = env.step(Action(ActionType.SIMPLIFY))
    print(f"Step 2 — SIMPLIFY (reward: {r})")
    env.display()

    # Divide both sides by 2
    r = env.step(Action(ActionType.DIV, expr=Integer(2)))
    print(f"Step 3 — DIV 2 (reward: {r})")
    env.display()

    # Simplify
    r = env.step(Action(ActionType.SIMPLIFY))
    print(f"Step 4 — SIMPLIFY (reward: {r})")
    env.display()

    # Now we have x = 2. Write 2, substitute, verify.
    r = env.step(Action(ActionType.WRITE, expr="2"))
    r = env.step(Action(ActionType.SUBSTITUTE, expr=Integer(2), target_symbol=x))
    print(f"Step 6 — SUBSTITUTE x = 2 (reward: {r})")
    env.display()


def demo_arbitrary_strings():
    """Show that the Imaginary board accepts anything — only valid substrings matter."""
    print("=" * 60)
    print("DEMO: Arbitrary strings — x - 3 = 0")
    print("=" * 60)

    x = Symbol('x')
    env = TwoBoardEnv(x - 3)
    env.display()

    # Agent writes nonsense — no valid extractions
    r = env.step(Action(ActionType.WRITE, expr="hello world 🎲"))
    print(f"Step 1 — WRITE 'hello world 🎲' (reward: {r})")
    env.display()

    # Agent writes something with a valid substring buried in it
    r = env.step(Action(ActionType.WRITE, expr="the answer is probably 3 maybe"))
    print(f"Step 2 — WRITE 'the answer is probably 3 maybe' (reward: {r})")
    env.display()

    # "3" is now extractable as a valid expression!
    r = env.step(Action(ActionType.SUBSTITUTE, expr=Integer(3), target_symbol=x))
    print(f"Step 3 — SUBSTITUTE x = 3 (reward: {r})")
    env.display()


def demo_incomplete_roots():
    """Show penalty for declaring complete without finding all roots."""
    print("=" * 60)
    print("DEMO: Incomplete — x² - 5x + 6 = 0 (only find one root)")
    print("=" * 60)

    x = Symbol('x')
    env = TwoBoardEnv(x**2 - 5*x + 6)
    env.display()

    # Find only one root
    r = env.step(Action(ActionType.WRITE, expr="2"))
    r = env.step(Action(ActionType.SUBSTITUTE, expr=Integer(2), target_symbol=x))
    print(f"SUBSTITUTE x = 2 (reward: {r})")
    env.display()

    # Declare complete prematurely (missing x=3)
    r = env.step(Action(ActionType.DECLARE_COMPLETE))
    print(f"DECLARE_COMPLETE (incomplete - reward: {r})")
    env.display()


if __name__ == "__main__":
    demo_cubic_cardano()
    demo_arbitrary_strings()
    print("\n")
    demo_linear()
    print("\n")
    demo_quadratic()
    print("\n")
    demo_incomplete_roots()
    print("\n")
    demo_cubic()
    print("\n")
    demo_unsolvable_quintic()
    print("\n")
    demo_solvable_quintic()
    print("\n")
    demo_operations()