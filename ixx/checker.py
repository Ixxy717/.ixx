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
  5. Literal value validation for specific built-ins — TOP LEVEL ONLY.
     Literal checks are suppressed inside function bodies, if/else blocks,
     loop bodies, try blocks, and catch blocks.
     For read()/readlines() the check is also suppressed when any write() or
     append() to the same literal path appears anywhere in the program.
  6. Import errors (missing file, circular import, duplicate function) reported
     as CheckErrors when imported_funcs has already been resolved outside.
"""

from __future__ import annotations
import os
import re
from dataclasses import dataclass

from .ast_nodes import (
    Program, Assign, If, Loop, LoopEach, Say,
    CallExpr, CallStmt, FuncDef, ReturnStmt, TryCatch, UseStmt,
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

    def check(
        self,
        program: Program,
        file_path: str,
        imported_funcs: dict[str, FuncDef] | None = None,
    ) -> list[CheckError]:
        self._file = file_path
        self._errors: list[CheckError] = []

        # _literal_depth tracks how deep inside any block we are.
        # Literal built-in checks only fire when this is 0 (true top level).
        self._literal_depth: int = 0

        # Seed func_table with imported functions.
        self._func_table: dict[str, FuncDef] = dict(imported_funcs or {})

        # First pass: collect local FuncDef, reporting duplicates with imports.
        for stmt in program.body:
            if isinstance(stmt, FuncDef):
                if stmt.name in self._func_table:
                    self._err(
                        stmt.line, None,
                        f"Duplicate function '{stmt.name}'. "
                        "Function names must be unique across imports."
                    )
                else:
                    self._func_table[stmt.name] = stmt

        # Second pass: collect every name ever assigned anywhere in the file.
        self._all_assigned: set[str] = set()
        self._collect_names(program.body)

        # Third pass: collect all literal file paths written/appended anywhere.
        self._written_paths: set[str] = set()
        self._collect_written_paths(program.body)

        # Fourth pass: check all statements.
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
            elif isinstance(stmt, LoopEach):
                # Do NOT add var_name here — it only survives if predeclared before loop.
                # Collect any names assigned inside the body (they may escape via scoping).
                self._collect_names(stmt.body)
            elif isinstance(stmt, TryCatch):
                self._collect_names(stmt.try_body)
                if stmt.catch_body:
                    self._all_assigned.add("error")
                    self._collect_names(stmt.catch_body)
            # UseStmt: no names to collect

    # ── written-paths collection pass ────────────────────────────────────────

    def _collect_written_paths(self, stmts: list) -> None:
        """Recursively gather all literal file paths passed to write/append."""
        for stmt in stmts:
            if isinstance(stmt, CallStmt):
                if stmt.name in ("write", "append") and stmt.args:
                    s = _lit_str(stmt.args[0])
                    if s is not None:
                        self._written_paths.add(s)
            elif isinstance(stmt, Assign):
                self._scan_expr_for_writes(stmt.value)
            elif isinstance(stmt, FuncDef):
                self._collect_written_paths(stmt.body)
            elif isinstance(stmt, If):
                self._collect_written_paths(stmt.then_body)
                self._collect_written_paths(stmt.else_body)
            elif isinstance(stmt, Loop):
                self._collect_written_paths(stmt.body)
            elif isinstance(stmt, LoopEach):
                self._collect_written_paths(stmt.body)
            elif isinstance(stmt, TryCatch):
                self._collect_written_paths(stmt.try_body)
                self._collect_written_paths(stmt.catch_body)
            # UseStmt: no writes to track

    def _scan_expr_for_writes(self, expr) -> None:
        if isinstance(expr, CallExpr) and expr.name in ("write", "append"):
            if expr.args:
                s = _lit_str(expr.args[0])
                if s is not None:
                    self._written_paths.add(s)

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
                self._literal_depth += 1
                self._check_stmts(stmt.then_body, in_function)
                self._check_stmts(stmt.else_body, in_function)
                self._literal_depth -= 1
            elif isinstance(stmt, Loop):
                self._check_expr(stmt.condition, in_function)
                self._literal_depth += 1
                self._check_stmts(stmt.body, in_function)
                self._literal_depth -= 1
            elif isinstance(stmt, LoopEach):
                self._check_expr(stmt.iterable, in_function)
                # Conservative literal check: only flag obvious non-list at top level.
                if self._literal_depth == 0:
                    t = _lit_type_name(stmt.iterable)
                    if t is not None:
                        self._err(stmt.line, None, f"'loop each' expects a list, got {t}.")
                # Track whether the loop var was declared before this loop.
                was_predeclared = stmt.var_name in self._all_assigned
                # Temporarily add var_name so body checks treat it as defined.
                self._all_assigned.add(stmt.var_name)
                self._literal_depth += 1
                self._check_stmts(stmt.body, in_function)
                self._literal_depth -= 1
                # If not predeclared, remove it — it doesn't leak past the loop.
                if not was_predeclared:
                    self._all_assigned.discard(stmt.var_name)
            elif isinstance(stmt, FuncDef):
                self._literal_depth += 1
                self._check_stmts(stmt.body, in_function=True)
                self._literal_depth -= 1
            elif isinstance(stmt, ReturnStmt):
                if stmt.value is not None:
                    self._check_expr(stmt.value, in_function)
            elif isinstance(stmt, TryCatch):
                self._literal_depth += 1
                self._check_stmts(stmt.try_body, in_function)
                self._check_stmts(stmt.catch_body, in_function)
                self._literal_depth -= 1
            # UseStmt: nothing to check here (resolved before check() is called)

    # ── expression walk ──────────────────────────────────────────────────────

    # Matches {content} blocks — used to find non-identifier interpolation attempts.
    _INTERP_BLOCK = re.compile(r'\{([^}]*)\}')
    # A bare identifier looks exactly like this.
    _BARE_IDENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
    # Content that signals an expression was attempted (not just a typo).
    _EXPR_CHARS = re.compile(r'[()+ \-*/]')

    def _check_expr(self, expr, in_function: bool) -> None:
        if isinstance(expr, StrLit):
            # Warn about {expr(...)} or {a + b} patterns that will not be interpolated.
            # This warning fires at all depths — it's equally likely inside functions.
            for m in self._INTERP_BLOCK.finditer(expr.value):
                content = m.group(1)
                if not self._BARE_IDENT.match(content) and self._EXPR_CHARS.search(content):
                    self._warn(
                        getattr(expr, "line", None), None,
                        f"'{{{{ {content} }}}}' in string will not be interpolated — "
                        "only bare variable names like {name} are supported."
                    )
        elif isinstance(expr, VarRef):
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

        # User-defined function (local or imported)?
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
                # Arity OK — run conservative literal-value checks (top level only).
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
        """Conservative literal-argument validation for specific built-ins.

        Only fires when _literal_depth == 0 (true top-level, not inside any block).
        """
        if self._literal_depth > 0:
            return

        if not args:
            return

        arg0 = args[0]

        if name == "color":
            s = _lit_str(arg0)
            if s is not None:
                if s.lower().strip() not in _VALID_COLORS:
                    valid_list = ", ".join(sorted(_VALID_COLORS))
                    self._err(
                        line, None,
                        f"Unknown color '{s}'.  Valid colors: {valid_list}."
                    )

        elif name in ("read", "readlines"):
            s = _lit_str(arg0)
            if (
                s is not None
                and s not in self._written_paths
                and not os.path.exists(s)
            ):
                self._err(line, None, f"File not found: {s}")

        elif name in ("first", "last", "sort", "reverse"):
            t = _lit_type_name(arg0)
            if t is not None:
                self._err(
                    line, None,
                    f"'{name}' works on lists, not {t}."
                )

        elif name == "count":
            t = _lit_type_name(arg0)
            if t in ("number", "bool", "nothing"):
                self._err(
                    line, None,
                    f"'count' works on lists and text, not {t}."
                )

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

    def _err(self, line: int | None, column: int | None, message: str, severity: str = "error") -> None:
        self._errors.append(CheckError(
            file=self._file,
            line=line,
            column=column,
            severity=severity,
            message=message,
        ))

    def _warn(self, line: int | None, column: int | None, message: str) -> None:
        self._err(line, column, message, severity="warning")
