"""
IXX static semantic checker.

Runs after a successful syntax parse and before execution.
All checks are conservative — if a check is uncertain, it is skipped.
Never executes any user code.

Checks performed:
  1. Wrong argument count for user-defined function calls.
  2. Unknown function/built-in calls.
  3. Wrong argument count for built-in calls (where arg count is fixed).
  4. Simple undefined variable references (top-level only, conservative).
  5. Literal value validation for specific built-ins (see _check_builtin_literals).
"""

from __future__ import annotations
import os
from dataclasses import dataclass

from .ast_nodes import (
    Program, Assign, If, Loop, Say,
    CallExpr, CallStmt, FuncDef, ReturnStmt, TryCatch,
    VarRef, BinOp, NegOp, Compare, AndOp, OrOp, NotOp,
    ListLit, StrLit, IntLit, FloatLit, BoolLit, NothingLit,
)


# ── built-in arity table ────────────────────────────────────────────────────
# (min_args, max_args)  — max_args=None means no upper limit

_BUILTIN_ARITY: dict[str, tuple[int, int | None]] = {
    "count":     (1, 1),
    "text":      (1, 1),
    "number":    (1, 1),
    "type":      (1, 1),
    "ask":       (0, 1),
    "upper":     (1, 1),
    "lower":     (1, 1),
    "trim":      (1, 1),
    "replace":   (3, 3),
    "split":     (1, 2),
    "join":      (1, 2),
    "round":     (1, 2),
    "abs":       (1, 1),
    "min":       (1, None),
    "max":       (1, None),
    "first":     (1, 1),
    "last":      (1, 1),
    "sort":      (1, 1),
    "reverse":   (1, 1),
    "read":      (1, 1),
    "readlines": (1, 1),
    "write":     (2, 2),
    "append":    (2, 2),
    "exists":    (1, 1),
    "color":     (2, 2),
    "do":        (1, 1),
}

_ALL_BUILTINS: frozenset[str] = frozenset(_BUILTIN_ARITY)

# Valid IXX color names (must stay in sync with runtime/builtins/color.py)
_VALID_COLORS: frozenset[str] = frozenset(
    {"red", "green", "yellow", "cyan", "bold", "dim"}
)


# ── literal helpers ───────────────────────────────────────────────────────────

def _lit_str(expr) -> str | None:
    """Return the string value if *expr* is a StrLit, else None."""
    return expr.value if isinstance(expr, StrLit) else None


def _lit_type_name(expr) -> str | None:
    """Return the IXX type name if *expr* is any scalar literal, else None.

    Returns None for ListLit (we do not flag lists as wrong here).
    """
    if isinstance(expr, StrLit):             return "text"
    if isinstance(expr, (IntLit, FloatLit)): return "number"
    if isinstance(expr, BoolLit):            return "bool"
    if isinstance(expr, NothingLit):         return "nothing"
    return None


# ── result types ─────────────────────────────────────────────────────────────

@dataclass
class CheckError:
    file: str
    line: int | None
    column: int | None
    severity: str
    message: str

    def as_dict(self) -> dict:
        return {
            "file":     self.file,
            "line":     self.line,
            "column":   self.column,
            "severity": self.severity,
            "message":  self.message,
        }


# ── checker ───────────────────────────────────────────────────────────────────

class SemanticChecker:
    """Walk a Program AST and return a list of semantic errors."""

    def check(self, program: Program, file_path: str) -> list[CheckError]:
        self._file = file_path
        self._errors: list[CheckError] = []

        # First pass: collect user-defined function signatures.
        self._func_table: dict[str, FuncDef] = {
            stmt.name: stmt
            for stmt in program.body
            if isinstance(stmt, FuncDef)
        }

        # Second pass: collect every name ever assigned anywhere in the file
        # (used for conservative undefined-variable detection at top level).
        self._all_assigned: set[str] = set()
        self._has_catch = False
        self._collect_names(program.body)

        # Third pass: check all statements.
        self._check_stmts(program.body, in_function=False)

        return self._errors

    # ── name collection pass ─────────────────────────────────────────────────

    def _collect_names(self, stmts: list) -> None:
        for stmt in stmts:
            if isinstance(stmt, Assign):
                self._all_assigned.add(stmt.name)
            elif isinstance(stmt, FuncDef):
                self._all_assigned.add(stmt.name)
                for p in stmt.params:
                    self._all_assigned.add(p)
                self._collect_names(stmt.body)
            elif isinstance(stmt, If):
                self._collect_names(stmt.then_body)
                self._collect_names(stmt.else_body)
            elif isinstance(stmt, Loop):
                self._collect_names(stmt.body)
            elif isinstance(stmt, TryCatch):
                self._collect_names(stmt.try_body)
                if stmt.catch_body:
                    self._has_catch = True
                    self._all_assigned.add("error")
                    self._collect_names(stmt.catch_body)

    # ── statement walk ───────────────────────────────────────────────────────

    def _check_stmts(self, stmts: list, in_function: bool) -> None:
        for stmt in stmts:
            if isinstance(stmt, Assign):
                self._check_expr(stmt.value, in_function)
            elif isinstance(stmt, Say):
                for arg in stmt.args:
                    self._check_expr(arg, in_function)
            elif isinstance(stmt, CallStmt):
                self._check_call(stmt.name, stmt.args, stmt.line, in_function)
            elif isinstance(stmt, If):
                self._check_expr(stmt.condition, in_function)
                self._check_stmts(stmt.then_body, in_function)
                self._check_stmts(stmt.else_body, in_function)
            elif isinstance(stmt, Loop):
                self._check_expr(stmt.condition, in_function)
                self._check_stmts(stmt.body, in_function)
            elif isinstance(stmt, FuncDef):
                self._check_stmts(stmt.body, in_function=True)
            elif isinstance(stmt, ReturnStmt):
                if stmt.value is not None:
                    self._check_expr(stmt.value, in_function)
            elif isinstance(stmt, TryCatch):
                self._check_stmts(stmt.try_body, in_function)
                self._check_stmts(stmt.catch_body, in_function)

    # ── expression walk ──────────────────────────────────────────────────────

    def _check_expr(self, expr, in_function: bool) -> None:
        if isinstance(expr, VarRef):
            if not in_function:
                name = expr.name
                if (
                    name not in self._all_assigned
                    and name not in self._func_table
                    and name not in _ALL_BUILTINS
                ):
                    self._err(
                        expr.line, None,
                        f"'{name}' is not defined. Did you mean to set it first?"
                    )
        elif isinstance(expr, CallExpr):
            self._check_call(expr.name, expr.args, expr.line, in_function)
        elif isinstance(expr, (BinOp, Compare, AndOp, OrOp)):
            self._check_expr(expr.left, in_function)
            self._check_expr(expr.right, in_function)
        elif isinstance(expr, (NegOp, NotOp)):
            self._check_expr(expr.operand, in_function)
        elif isinstance(expr, ListLit):
            for item in expr.items:
                self._check_expr(item, in_function)

    # ── call checking ────────────────────────────────────────────────────────

    def _check_call(
        self,
        name: str,
        args: list,
        line: int | None,
        in_function: bool,
    ) -> None:
        n = len(args)

        # Recurse into argument expressions first.
        for arg in args:
            self._check_expr(arg, in_function)

        # User-defined function?
        if name in self._func_table:
            func = self._func_table[name]
            expected = len(func.params)
            if n != expected:
                param_hint = (
                    f". Parameters: {', '.join(func.params)}"
                    if func.params
                    else ""
                )
                self._err(
                    line, None,
                    f"'{name}' expects {expected} argument(s), got {n}{param_hint}"
                )
            return

        # Built-in?
        if name in _BUILTIN_ARITY:
            lo, hi = _BUILTIN_ARITY[name]
            if n < lo or (hi is not None and n > hi):
                if hi is None:
                    expected_str = f"at least {lo}"
                elif lo == hi:
                    expected_str = str(lo)
                else:
                    expected_str = f"{lo}-{hi}"
                self._err(
                    line, None,
                    f"'{name}' expects {expected_str} argument(s), got {n}"
                )
            else:
                # Arity OK — run conservative literal-value checks.
                self._check_builtin_literals(name, args, line)
            return

        # Unknown name entirely.
        self._err(
            line, None,
            f"'{name}' is not defined."
        )

    # ── literal value checks for built-ins ───────────────────────────────────

    def _check_builtin_literals(
        self, name: str, args: list, line: int | None
    ) -> None:
        """Conservative validation of literal arguments for specific built-ins.

        Only fires when the argument is a known literal (string, number, bool,
        nothing).  If the argument is a variable or expression, skips silently.
        """
        if not args:
            return

        arg0 = args[0]

        # ── color(name, text) ─────────────────────────────────────────────
        if name == "color":
            s = _lit_str(arg0)
            if s is not None:
                if s.lower().strip() not in _VALID_COLORS:
                    valid_list = ", ".join(sorted(_VALID_COLORS))
                    self._err(
                        line, None,
                        f"Unknown color '{s}'.  Valid colors: {valid_list}."
                    )

        # ── read(path) / readlines(path) ──────────────────────────────────
        elif name in ("read", "readlines"):
            s = _lit_str(arg0)
            if s is not None and not os.path.exists(s):
                self._err(line, None, f"File not found: {s}")

        # ── first/last/sort/reverse — must be list ────────────────────────
        elif name in ("first", "last", "sort", "reverse"):
            t = _lit_type_name(arg0)
            if t is not None:
                self._err(
                    line, None,
                    f"'{name}' works on lists, not {t}."
                )

        # ── count — works on text and lists, not numbers/bools/nothing ────
        elif name == "count":
            t = _lit_type_name(arg0)
            if t in ("number", "bool", "nothing"):
                self._err(
                    line, None,
                    f"'count' works on lists and text, not {t}."
                )

        # ── number(x) — catch obviously un-convertible string literals ────
        elif name == "number":
            s = _lit_str(arg0)
            if s is not None:
                try:
                    int(s)
                except ValueError:
                    try:
                        float(s)
                    except ValueError:
                        self._err(
                            line, None,
                            f"Cannot convert '{s}' to a number."
                        )

        # ── do(command) — empty string or non-text literal ────────────────
        elif name == "do":
            s = _lit_str(arg0)
            if s is not None:
                if not s.strip():
                    self._err(line, None, "do() received an empty command.")
            else:
                t = _lit_type_name(arg0)
                if t is not None:
                    self._err(
                        line, None,
                        f"'do' expects a shell command as text, not {t}."
                    )

    # ── error helper ─────────────────────────────────────────────────────────

    def _err(self, line: int | None, column: int | None, message: str) -> None:
        self._errors.append(CheckError(
            file=self._file,
            line=line,
            column=column,
            severity="error",
            message=message,
        ))
