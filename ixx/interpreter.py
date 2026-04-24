"""
IXX interpreter: walks an AST and produces side effects.

The Environment maps variable names to values.
Child environments are created for if/loop blocks.
"""

from __future__ import annotations
import re
from .ast_nodes import (
    Program, Assign, If, Loop, Say,
    IntLit, FloatLit, StrLit, BoolLit, ListLit, VarRef,
    NegOp, BinOp, Compare, AndOp, OrOp, NotOp,
    IXXValue, Expr, Stmt,
)

_INTERP_RE = re.compile(r'\{([A-Za-z_][A-Za-z0-9_]*)\}')


# ── runtime errors ─────────────────────────────────────────────────────────────

class IXXRuntimeError(Exception):
    pass


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

    def run(self, program: Program) -> None:
        self._exec_block(program.body, Environment())

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
                while _truthy(self._eval(cond, env)):
                    self._exec_block(body, env.child())

            case Say(args=args):
                parts = [_display(self._eval(a, env)) for a in args]
                print(" ".join(parts))

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
                if isinstance(v, (int, float)):
                    return -v
                raise IXXRuntimeError(
                    f"Cannot negate a {type(v).__name__} value."
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

            case _:
                raise IXXRuntimeError(
                    f"Unknown expression type: {type(expr).__name__}"
                )

    # ── string interpolation ───────────────────────────────────────────────────

    def _interpolate(self, text: str, env: Environment) -> str:
        """Replace {varname} placeholders with the current variable values."""
        def replace(m: re.Match) -> str:
            name = m.group(1)
            try:
                return _display(env.get(name))
            except IXXRuntimeError:
                return m.group(0)   # leave {name} as-is if not defined
        return _INTERP_RE.sub(replace, text)

    # ── arithmetic ─────────────────────────────────────────────────────────────

    def _eval_binop(
        self, op: str, left: Expr, right: Expr, env: Environment
    ) -> IXXValue:
        lv = self._eval(left, env)
        rv = self._eval(right, env)
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
            case "less than":
                return a < b            # type: ignore[operator]
            case "more than":
                return a > b            # type: ignore[operator]
            case "at least":
                return a >= b           # type: ignore[operator]
            case "at most":
                return a <= b           # type: ignore[operator]
            case "contains":
                if isinstance(a, list):
                    return b in a
                if isinstance(a, str):
                    return str(b) in a
                raise IXXRuntimeError(
                    f"'contains' only works on lists and text, not {type(a).__name__}."
                )
            case _:
                raise IXXRuntimeError(f"Unknown comparison: {op!r}")
