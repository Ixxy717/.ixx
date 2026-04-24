"""
IXX interpreter: walks an AST and produces side effects.

The Environment maps variable names to values.
Child environments are created for if/loop blocks; FunctionEnvironment
is used for function calls to isolate local writes from the global scope.
"""

from __future__ import annotations
import re
import sys
from .ast_nodes import (
    Program, Assign, If, Loop, Say,
    IntLit, FloatLit, StrLit, BoolLit, ListLit, VarRef,
    NegOp, BinOp, Compare, AndOp, OrOp, NotOp,
    CallExpr, CallStmt, ReturnStmt, FuncDef,
    IXXValue, Expr, Stmt,
)

_INTERP_RE = re.compile(r'\{([A-Za-z_][A-Za-z0-9_]*)\}')

_LOOP_LIMIT = 10_000
_CALL_DEPTH_LIMIT = 100


# ── runtime errors ─────────────────────────────────────────────────────────────

class IXXRuntimeError(Exception):
    pass


# ── return signal ──────────────────────────────────────────────────────────────

class _ReturnSignal(Exception):
    """Used to unwind the call stack on a `return` statement."""
    def __init__(self, value: IXXValue):
        self.value = value


# ── environment ────────────────────────────────────────────────────────────────

class Environment:
    """A variable scope.  Looks up parent scopes when a name isn't found here."""

    def __init__(self, parent: "Environment | None" = None):
        self._vars: dict[str, IXXValue] = {}
        self._parent = parent

    def get(self, name: str) -> IXXValue:
        if name in self._vars:
            return self._vars[name]
        if self._parent is not None:
            return self._parent.get(name)
        raise IXXRuntimeError(
            f"I don't know what '{name}' is. Did you set it yet?\n"
            f"  Tip: {name} = \"your value\""
        )

    def set(self, name: str, value: IXXValue) -> None:
        # Write to the nearest scope that already owns this name,
        # otherwise create it in the current scope.
        if name in self._vars or self._parent is None:
            self._vars[name] = value
        elif self._parent._has(name):
            self._parent.set(name, value)
        else:
            self._vars[name] = value

    def _has(self, name: str) -> bool:
        return (
            name in self._vars
            or (self._parent is not None and self._parent._has(name))
        )

    def child(self) -> "Environment":
        return Environment(parent=self)


class FunctionEnvironment(Environment):
    """Local scope for a function call.

    Reads propagate up to the global scope (so globals are readable).
    Writes are always local — never propagate back to the global scope.
    This gives clean function isolation without requiring explicit 'global'.
    """

    def set(self, name: str, value: IXXValue) -> None:
        # Always write locally — never update the parent (global) scope.
        self._vars[name] = value


# ── built-in functions ─────────────────────────────────────────────────────────

def _ixx_type_name(value: IXXValue) -> str:
    """Return the IXX type name for a value (never exposes Python names)."""
    if value is None:       return "nothing"
    if isinstance(value, bool):  return "bool"
    if isinstance(value, (int, float)): return "number"
    if isinstance(value, str):   return "text"
    if isinstance(value, list):  return "list"
    return "unknown"


def _builtin_count(x: IXXValue) -> int:
    if isinstance(x, (str, list)):
        return len(x)
    raise IXXRuntimeError(
        f"'count' works on lists and text, not {_ixx_type_name(x)}."
    )


def _builtin_text(x: IXXValue) -> str:
    return _display(x)


def _builtin_number(x: IXXValue) -> int | float:
    if isinstance(x, bool):
        raise IXXRuntimeError(
            f"Cannot convert '{_display(x)}' to a number."
        )
    if isinstance(x, (int, float)):
        return x
    s = str(x)
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    raise IXXRuntimeError(
        f"Cannot convert '{x}' to a number."
    )


def _builtin_type(x: IXXValue) -> str:
    return _ixx_type_name(x)


def _builtin_ask(prompt: IXXValue = "") -> str:
    return input(str(prompt))


# ── v0.5 built-ins ─────────────────────────────────────────────────────────────

# -- text ---

def _builtin_upper(x: IXXValue) -> str:
    if not isinstance(x, str):
        raise IXXRuntimeError(f"'upper' works on text, not {_ixx_type_name(x)}.")
    return x.upper()


def _builtin_lower(x: IXXValue) -> str:
    if not isinstance(x, str):
        raise IXXRuntimeError(f"'lower' works on text, not {_ixx_type_name(x)}.")
    return x.lower()


def _builtin_trim(x: IXXValue) -> str:
    if not isinstance(x, str):
        raise IXXRuntimeError(f"'trim' works on text, not {_ixx_type_name(x)}.")
    return x.strip()


def _builtin_replace(x: IXXValue, find: IXXValue, replacement: IXXValue) -> str:
    if not isinstance(x, str):
        raise IXXRuntimeError(f"'replace' works on text, not {_ixx_type_name(x)}.")
    if not isinstance(find, str):
        raise IXXRuntimeError(
            f"'replace' second argument (find) must be text, not {_ixx_type_name(find)}."
        )
    return x.replace(str(find), str(replacement))


def _builtin_split(x: IXXValue, sep: IXXValue = None) -> list:  # type: ignore[assignment]
    if not isinstance(x, str):
        raise IXXRuntimeError(f"'split' works on text, not {_ixx_type_name(x)}.")
    if sep is None:
        return x.split()
    if not isinstance(sep, str):
        raise IXXRuntimeError(
            f"'split' separator must be text, not {_ixx_type_name(sep)}."
        )
    return x.split(sep)


def _builtin_join(items: IXXValue, sep: IXXValue = ", ") -> str:
    if not isinstance(items, list):
        raise IXXRuntimeError(f"'join' works on lists, not {_ixx_type_name(items)}.")
    if not isinstance(sep, str):
        raise IXXRuntimeError(
            f"'join' separator must be text, not {_ixx_type_name(sep)}."
        )
    return sep.join(str(item) for item in items)


# -- math ---

def _builtin_round(x: IXXValue, digits: IXXValue = 0) -> int | float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise IXXRuntimeError(f"'round' works on numbers, not {_ixx_type_name(x)}.")
    try:
        d = int(digits)
    except (TypeError, ValueError):
        raise IXXRuntimeError("'round' second argument (digits) must be a whole number.")
    result = round(x, d)
    return int(result) if d <= 0 else result


def _builtin_abs(x: IXXValue) -> int | float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise IXXRuntimeError(f"'abs' works on numbers, not {_ixx_type_name(x)}.")
    return abs(x)


def _builtin_min(*args: IXXValue) -> IXXValue:
    if len(args) == 1 and isinstance(args[0], list):
        items = args[0]
        if not items:
            raise IXXRuntimeError("'min' cannot find the minimum of an empty list.")
        return min(items)  # type: ignore[type-var]
    if len(args) < 2:
        raise IXXRuntimeError(
            "'min' needs at least two values, or a list.  Example: min(3, 7)"
        )
    return min(args)  # type: ignore[type-var]


def _builtin_max(*args: IXXValue) -> IXXValue:
    if len(args) == 1 and isinstance(args[0], list):
        items = args[0]
        if not items:
            raise IXXRuntimeError("'max' cannot find the maximum of an empty list.")
        return max(items)  # type: ignore[type-var]
    if len(args) < 2:
        raise IXXRuntimeError(
            "'max' needs at least two values, or a list.  Example: max(3, 7)"
        )
    return max(args)  # type: ignore[type-var]


# -- lists ---

def _builtin_first(items: IXXValue) -> IXXValue:
    if not isinstance(items, list):
        raise IXXRuntimeError(f"'first' works on lists, not {_ixx_type_name(items)}.")
    if not items:
        return None
    return items[0]


def _builtin_last(items: IXXValue) -> IXXValue:
    if not isinstance(items, list):
        raise IXXRuntimeError(f"'last' works on lists, not {_ixx_type_name(items)}.")
    if not items:
        return None
    return items[-1]


def _builtin_sort(items: IXXValue) -> list:
    if not isinstance(items, list):
        raise IXXRuntimeError(f"'sort' works on lists, not {_ixx_type_name(items)}.")
    try:
        return sorted(items)  # type: ignore[type-var]
    except TypeError:
        raise IXXRuntimeError(
            "'sort' cannot sort a list that mixes text and numbers."
        )


def _builtin_reverse(items: IXXValue) -> list:
    if not isinstance(items, list):
        raise IXXRuntimeError(f"'reverse' works on lists, not {_ixx_type_name(items)}.")
    return list(reversed(items))


# -- color ---

# Map of IXX color names to ANSI SGR codes
_COLOR_CODES: dict[str, str] = {
    "red":    "\033[31m",
    "green":  "\033[32m",
    "yellow": "\033[33m",
    "cyan":   "\033[36m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
}
_COLOR_RESET = "\033[0m"


def _ansi_enabled() -> bool:
    """Return True if ANSI is currently enabled (checks env vars, tty)."""
    import os, sys
    if os.environ.get("NO_COLOR", ""):
        return False
    ixx_color = os.environ.get("IXX_COLOR", "")
    if ixx_color == "0":
        return False
    if ixx_color == "1":
        return True
    return sys.stdout.isatty()


def _builtin_color(color_name: IXXValue, text_val: IXXValue) -> str:
    if not isinstance(color_name, str):
        raise IXXRuntimeError(
            f"'color' first argument must be a color name (text), "
            f"not {_ixx_type_name(color_name)}."
        )
    name = color_name.lower().strip()
    if name not in _COLOR_CODES:
        valid = ", ".join(sorted(_COLOR_CODES))
        raise IXXRuntimeError(
            f"Unknown color '{color_name}'.  Valid colors: {valid}."
        )
    text_str = str(text_val) if text_val is not None else ""
    if not _ansi_enabled():
        return text_str
    return f"{_COLOR_CODES[name]}{text_str}{_COLOR_RESET}"


BUILT_INS: dict[str, object] = {
    # v0.4
    "count":   _builtin_count,
    "text":    _builtin_text,
    "number":  _builtin_number,
    "type":    _builtin_type,
    "ask":     _builtin_ask,
    # v0.5 — text
    "upper":   _builtin_upper,
    "lower":   _builtin_lower,
    "trim":    _builtin_trim,
    "replace": _builtin_replace,
    "split":   _builtin_split,
    "join":    _builtin_join,
    # v0.5 — math
    "round":   _builtin_round,
    "abs":     _builtin_abs,
    "min":     _builtin_min,
    "max":     _builtin_max,
    # v0.5 — lists
    "first":   _builtin_first,
    "last":    _builtin_last,
    "sort":    _builtin_sort,
    "reverse": _builtin_reverse,
    # v0.5 — color
    "color":   _builtin_color,
}


# ── helpers ────────────────────────────────────────────────────────────────────

def _truthy(value: IXXValue) -> bool:
    if isinstance(value, bool):   return value
    if isinstance(value, int):    return value != 0
    if isinstance(value, float):  return value != 0.0
    if isinstance(value, str):    return value != ""
    if isinstance(value, list):   return len(value) > 0
    return False


def _display(value: IXXValue) -> str:
    if isinstance(value, bool): return "YES" if value else "NO"
    if isinstance(value, list): return ", ".join(_display(v) for v in value)
    if value is None:           return "nothing"
    return str(value)


# ── interpreter ────────────────────────────────────────────────────────────────

class Interpreter:
    """Evaluates an IXX Program."""

    def __init__(self) -> None:
        self._func_table: dict[str, FuncDef] = {}
        self._global_env: Environment = Environment()
        self._call_depth: int = 0

    def run(self, program: Program) -> None:
        self._global_env = Environment()
        self._func_table = {}
        self._call_depth = 0

        # First pass: collect all FuncDef nodes so forward calls work.
        for stmt in program.body:
            if isinstance(stmt, FuncDef):
                self._func_table[stmt.name] = stmt

        # Second pass: execute all statements.
        self._exec_block(program.body, self._global_env)

    # ── statement dispatch ─────────────────────────────────────────────────────

    def _exec_block(self, stmts: list[Stmt], env: Environment) -> None:
        for stmt in stmts:
            self._exec(stmt, env)

    def _exec(self, stmt: Stmt, env: Environment) -> None:
        match stmt:
            case Assign(name=name, value=expr):
                env.set(name, self._eval(expr, env))

            case If(condition=cond, then_body=then_body, else_body=else_body):
                if _truthy(self._eval(cond, env)):
                    self._exec_block(then_body, env.child())
                elif else_body:
                    self._exec_block(else_body, env.child())

            case Loop(condition=cond, body=body):
                iterations = 0
                while _truthy(self._eval(cond, env)):
                    iterations += 1
                    if iterations > _LOOP_LIMIT:
                        raise IXXRuntimeError(
                            f"Loop ran more than {_LOOP_LIMIT:,} times — did you mean to loop forever?\n"
                            "  Tip: Make sure your loop condition eventually becomes NO."
                        )
                    self._exec_block(body, env.child())

            case Say(args=args):
                parts = [_display(self._eval(a, env)) for a in args]
                print(" ".join(parts))

            case CallStmt(name=name, args=arg_exprs):
                evaluated = [self._eval(a, env) for a in arg_exprs]
                self._call(name, evaluated)

            case ReturnStmt(value=val_expr):
                if self._call_depth == 0:
                    raise IXXRuntimeError(
                        "'return' can only be used inside a function."
                    )
                value = self._eval(val_expr, env) if val_expr is not None else None
                raise _ReturnSignal(value)

            case FuncDef():
                pass  # already collected during the first pass in run()

            case _:
                raise IXXRuntimeError(
                    f"Unknown statement type: {type(stmt).__name__}"
                )

    # ── expression evaluation ──────────────────────────────────────────────────

    def _eval(self, expr: Expr, env: Environment) -> IXXValue:
        match expr:
            case IntLit(value=v):   return v
            case FloatLit(value=v): return v
            case BoolLit(value=v):  return v

            case StrLit(value=v):
                return self._interpolate(v, env)

            case ListLit(items=items):
                return [self._eval(item, env) for item in items]

            case VarRef(name=name):
                return env.get(name)

            case NegOp(operand=operand):
                v = self._eval(operand, env)
                if isinstance(v, bool):
                    raise IXXRuntimeError(
                        "Cannot negate a YES/NO value."
                    )
                if isinstance(v, (int, float)):
                    return -v
                raise IXXRuntimeError(
                    f"Cannot negate a {_ixx_type_name(v)} value."
                )

            case BinOp(op=op, left=left, right=right):
                return self._eval_binop(op, left, right, env)

            case Compare(op=op, left=left, right=right):
                return self._eval_compare(op, left, right, env)

            case AndOp(left=left, right=right):
                lv = self._eval(left, env)
                return lv if not _truthy(lv) else self._eval(right, env)

            case OrOp(left=left, right=right):
                lv = self._eval(left, env)
                return lv if _truthy(lv) else self._eval(right, env)

            case NotOp(operand=operand):
                return not _truthy(self._eval(operand, env))

            case CallExpr(name=name, args=arg_exprs):
                evaluated = [self._eval(a, env) for a in arg_exprs]
                return self._call(name, evaluated)

            case _:
                raise IXXRuntimeError(
                    f"Unknown expression type: {type(expr).__name__}"
                )

    # ── function dispatch ──────────────────────────────────────────────────────

    def _call(self, name: str, args: list[IXXValue]) -> IXXValue:
        """Call a built-in or user-defined function and return its value."""

        # Built-ins first
        if name in BUILT_INS:
            fn = BUILT_INS[name]
            try:
                return fn(*args)  # type: ignore[operator]
            except IXXRuntimeError:
                raise
            except TypeError as e:
                raise IXXRuntimeError(
                    f"Wrong number of arguments for '{name}': {e}"
                )

        # User-defined functions
        if name in self._func_table:
            func = self._func_table[name]
            if len(args) != len(func.params):
                raise IXXRuntimeError(
                    f"'{name}' expects {len(func.params)} argument(s), got {len(args)}."
                    + (f"  Parameters: {', '.join(func.params)}" if func.params else "")
                )

            self._call_depth += 1
            if self._call_depth > _CALL_DEPTH_LIMIT:
                self._call_depth -= 1
                raise IXXRuntimeError(
                    f"Recursion too deep ({_CALL_DEPTH_LIMIT}+ calls). "
                    "Check for infinite recursion."
                )

            local = FunctionEnvironment(parent=self._global_env)
            for param, value in zip(func.params, args):
                local._vars[param] = value

            try:
                self._exec_block(func.body, local)
                return None
            except _ReturnSignal as ret:
                return ret.value
            except RecursionError:
                raise IXXRuntimeError(
                    "Recursion too deep. Check for infinite recursion."
                )
            finally:
                self._call_depth -= 1

        raise IXXRuntimeError(
            f"'{name}' is not a function. "
            f"Tip: define it with: function {name} ..."
        )

    # ── string interpolation ───────────────────────────────────────────────────

    def _interpolate(self, text: str, env: Environment) -> str:
        """Replace {varname} with current variable values.

        Undefined variables print a warning to stderr and render as {?name}.
        """
        def replace(m: re.Match) -> str:
            name = m.group(1)
            try:
                return _display(env.get(name))
            except IXXRuntimeError:
                print(
                    f"Warning: '{name}' is not defined — showing {{?{name}}} instead",
                    file=sys.stderr,
                )
                return "{?" + name + "}"
        return _INTERP_RE.sub(replace, text)

    # ── arithmetic ─────────────────────────────────────────────────────────────

    def _eval_binop(
        self, op: str, left: Expr, right: Expr, env: Environment
    ) -> IXXValue:
        lv = self._eval(left, env)
        rv = self._eval(right, env)

        # Guard: booleans must not silently coerce to int in arithmetic
        if isinstance(lv, bool) or isinstance(rv, bool):
            raise IXXRuntimeError(
                "Cannot use YES/NO in arithmetic. "
                "Use a number instead."
            )

        match op:
            case "+":
                # String + anything = string concatenation
                if isinstance(lv, str) or isinstance(rv, str):
                    return _display(lv) + _display(rv)
                return lv + rv          # type: ignore[operator]
            case "-":
                return lv - rv          # type: ignore[operator]
            case "*":
                return lv * rv          # type: ignore[operator]
            case "/":
                if rv == 0:
                    raise IXXRuntimeError(
                        "You tried to divide by zero — that's not possible."
                    )
                result = lv / rv        # type: ignore[operator]
                # Return int when both inputs are integers and result is whole
                if (
                    isinstance(lv, int) and isinstance(rv, int)
                    and result == int(result)
                ):
                    return int(result)
                return result
            case _:
                raise IXXRuntimeError(f"Unknown operator: {op!r}")

    # ── comparisons ────────────────────────────────────────────────────────────

    def _eval_compare(
        self, op: str, left: Expr, right: Expr, env: Environment
    ) -> bool:
        a = self._eval(left, env)
        b = self._eval(right, env)
        match op:
            case "is":
                return a == b
            case "is not":
                return a != b
            case "less than" | "more than" | "at least" | "at most":
                if isinstance(a, bool) or isinstance(b, bool):
                    raise IXXRuntimeError(
                        "Cannot use YES/NO in numeric comparisons. "
                        "Use 'is' or 'is not' to compare booleans."
                    )
                match op:
                    case "less than": return a < b   # type: ignore[operator]
                    case "more than": return a > b   # type: ignore[operator]
                    case "at least":  return a >= b  # type: ignore[operator]
                    case "at most":   return a <= b  # type: ignore[operator]
            case "contains":
                if isinstance(a, list):
                    # Warn if element types don't match
                    if a and type(a[0]) != type(b):
                        print(
                            f"Warning: types don't match in 'contains' — "
                            f"looking for {_ixx_type_name(b)} in a list of "
                            f"{_ixx_type_name(a[0])}",
                            file=sys.stderr,
                        )
                    return b in a
                if isinstance(a, str):
                    return str(b) in a
                raise IXXRuntimeError(
                    f"'contains' only works on lists and text, not {_ixx_type_name(a)}."
                )
            case _:
                raise IXXRuntimeError(f"Unknown comparison: {op!r}")
        return False  # unreachable, satisfies type checker
