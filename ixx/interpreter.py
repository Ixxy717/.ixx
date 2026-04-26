"""
IXX interpreter: walks an AST and produces side effects.

Supporting runtime pieces live in ixx/runtime/:
  errors.py       IXXRuntimeError
  values.py       display, truthy, ixx_type_name
  environment.py  Environment, FunctionEnvironment
  builtins/       all built-in function implementations + BUILT_INS registry
"""

from __future__ import annotations
import re
import sys
from .ast_nodes import (
    Program, Assign, If, Loop, LoopEach, Say,
    IntLit, FloatLit, StrLit, BoolLit, NothingLit, ListLit, VarRef,
    NegOp, BinOp, Compare, AndOp, OrOp, NotOp,
    CallExpr, CallStmt, ReturnStmt, FuncDef, TryCatch, UseStmt,
    IXXValue, Expr, Stmt,
)

# ── runtime imports ─────────────────────────────────────────────────────────────

from .runtime.errors      import IXXRuntimeError          # re-exported for compat
from .runtime.environment import Environment, FunctionEnvironment
from .runtime.values      import display as _display, truthy as _truthy, ixx_type_name as _ixx_type_name, ixx_err_type as _ixx_err_type
from .runtime.builtins    import BUILT_INS

_INTERP_RE = re.compile(r'\{([A-Za-z_][A-Za-z0-9_]*)\}')

_LOOP_LIMIT = 10_000


def _nargs(n: int) -> str:
    """Return a pluralised argument count string: '1 argument', '2 arguments'."""
    return f"{n} argument" if n == 1 else f"{n} arguments"
_CALL_DEPTH_LIMIT = 100


# ── return signal ──────────────────────────────────────────────────────────────

class _ReturnSignal(Exception):
    """Used to unwind the call stack on a `return` statement."""
    def __init__(self, value: IXXValue):
        self.value = value


# ── interpreter ────────────────────────────────────────────────────────────────

class Interpreter:
    """Evaluates an IXX Program."""

    def __init__(self) -> None:
        self._func_table: dict[str, FuncDef] = {}
        self._global_env: Environment = Environment()
        self._call_depth: int = 0
        self._exec_nesting: int = 0  # > 0 when inside any nested block

    def run(self, program: Program, extra_funcs: dict[str, FuncDef] | None = None) -> None:
        self._global_env = Environment()
        self._call_depth = 0
        self._exec_nesting = 0

        # Seed the function table with imported functions.
        self._func_table = dict(extra_funcs or {})

        # First pass: collect local FuncDef nodes; check for duplicates with imports.
        for stmt in program.body:
            if isinstance(stmt, FuncDef):
                if stmt.name in self._func_table:
                    raise IXXRuntimeError(
                        f"Duplicate function '{stmt.name}'. "
                        "Function names must be unique across imports."
                    )
                self._func_table[stmt.name] = stmt

        # Second pass: execute all statements.
        self._exec_block(program.body, self._global_env)

    def run_repl_input(
        self,
        program: Program,
        extra_funcs: dict[str, FuncDef] | None = None,
    ) -> None:
        """Execute *program* inside the current persistent session state.

        Unlike run(), this method does NOT reset the global environment or the
        function table.  Variables and functions defined in earlier REPL inputs
        remain visible.  New imported functions are merged (not replaced).

        Use this method exclusively for the interactive REPL.
        """
        # Merge new imports without discarding ones already accumulated.
        if extra_funcs:
            for name, func in extra_funcs.items():
                if name not in self._func_table:
                    self._func_table[name] = func

        # Register new top-level function definitions.
        for stmt in program.body:
            if isinstance(stmt, FuncDef):
                # Silently overwrite: redefining a function in the REPL is normal.
                self._func_table[stmt.name] = stmt

        # Execute against the persistent global environment.
        self._exec_block(program.body, self._global_env)

    # ── statement dispatch ─────────────────────────────────────────────────────

    def _exec_block(self, stmts: list[Stmt], env: Environment) -> None:
        for stmt in stmts:
            self._exec(stmt, env)

    def _exec_nested(self, stmts: list[Stmt], env: Environment) -> None:
        """Execute a block that is nested inside another statement (if/loop/try/function).

        Increments _exec_nesting so that FuncDef inside any block can be detected
        and rejected at runtime.
        """
        self._exec_nesting += 1
        try:
            self._exec_block(stmts, env)
        finally:
            self._exec_nesting -= 1

    def _exec(self, stmt: Stmt, env: Environment) -> None:
        match stmt:
            case Assign(name=name, value=expr):
                env.set(name, self._eval(expr, env))

            case If(condition=cond, then_body=then_body, else_body=else_body):
                if _truthy(self._eval(cond, env)):
                    self._exec_nested(then_body, env.child())
                elif else_body:
                    self._exec_nested(else_body, env.child())

            case Loop(condition=cond, body=body):
                iterations = 0
                while _truthy(self._eval(cond, env)):
                    iterations += 1
                    if iterations > _LOOP_LIMIT:
                        raise IXXRuntimeError(
                            f"Loop ran more than {_LOOP_LIMIT:,} times — did you mean to loop forever?\n"
                            "  Tip: Make sure your loop condition eventually becomes NO."
                        )
                    self._exec_nested(body, env.child())

            case LoopEach(var_name=var_name, iterable=iterable_expr, body=body):
                iterable = self._eval(iterable_expr, env)
                if not isinstance(iterable, list):
                    type_name = _ixx_err_type(iterable)
                    raise IXXRuntimeError(
                        f"'loop each' expects a list, got {type_name}."
                    )
                # Scoping: iter_env is a child of the outer env.  iter_env.set()
                # walks the parent chain — so if var_name already exists in an
                # ancestor scope it gets updated there (and survives the loop),
                # while a truly new name is created locally and discarded when
                # iter_env goes out of scope.  This mirrors how regular blocks work.
                for item in iterable:
                    iter_env = env.child()
                    iter_env.set(var_name, item)
                    self._exec_nested(body, iter_env)

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
                if self._exec_nesting > 0:
                    raise IXXRuntimeError(
                        "Function definitions must be at the top level, "
                        "not inside if/loop/try/other functions."
                    )
                # else: already registered during the first pass in run().

            case UseStmt():
                pass  # already resolved by modules.resolve_imports() before run()

            case TryCatch(try_body=try_body, catch_body=catch_body):
                try:
                    self._exec_nested(try_body, env.child())
                except (IXXRuntimeError, OSError, IOError, UnicodeDecodeError) as exc:
                    if catch_body:
                        catch_env = env.child()
                        if isinstance(exc, IXXRuntimeError):
                            err_msg = str(exc)
                        elif isinstance(exc, OSError):
                            err_msg = f"Something went wrong: {exc.strerror or 'could not access file'}"
                        elif isinstance(exc, UnicodeDecodeError):
                            err_msg = "Something went wrong: the file contains characters that could not be read."
                        else:
                            err_msg = "Something went wrong."
                        catch_env.set("error", err_msg)
                        self._exec_nested(catch_body, catch_env)

            case _:
                raise IXXRuntimeError(
                    "This statement cannot be run here."
                )

    # ── expression evaluation ──────────────────────────────────────────────────

    def _eval(self, expr: Expr, env: Environment) -> IXXValue:
        match expr:
            case IntLit(value=v):   return v
            case FloatLit(value=v): return v
            case BoolLit(value=v):  return v
            case NothingLit():      return None

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
                    f"Cannot negate a {_ixx_err_type(v)} value."
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
                    "This expression cannot be evaluated here."
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
                # Distinguish arity errors (wrong number of args) from type errors.
                # Python arity TypeErrors always contain "argument" in the message.
                if "argument" in str(e):
                    got = len(args)
                    raise IXXRuntimeError(
                        f"'{name}' was called with {_nargs(got)}, but that is not the right number."
                    )
                raise IXXRuntimeError(
                    f"'{name}' cannot be used with that type of value."
                )

        # User-defined functions
        if name in self._func_table:
            func = self._func_table[name]
            if len(args) != len(func.params):
                raise IXXRuntimeError(
                    f"'{name}' expects {_nargs(len(func.params))}, got {len(args)}."
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
                self._exec_nested(func.body, local)
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
            f"'{name}' is not defined."
        )

    # ── string interpolation ───────────────────────────────────────────────────

    # Keywords that are valid IXX literals but never live in the variable
    # environment.  {YES}, {NO}, and {nothing} substitute their display value
    # silently instead of printing a "not defined" warning.
    _INTERP_KEYWORDS: dict[str, str] = {
        "YES":     "YES",
        "NO":      "NO",
        "yes":     "YES",
        "no":      "NO",
        "nothing": "nothing",
    }

    def _interpolate(self, text: str, env: Environment) -> str:
        """Replace {varname} with current variable values.

        Undefined variables print a warning to stderr and render as {?name}.
        IXX literal keywords (YES, NO, nothing) substitute their display value.
        """
        def replace(m: re.Match) -> str:
            name = m.group(1)
            # Fast path: IXX literal keywords substitute directly.
            if name in self._INTERP_KEYWORDS:
                return self._INTERP_KEYWORDS[name]
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

        # Guard: lists are not valid arithmetic operands
        if isinstance(lv, list) or isinstance(rv, list):
            raise IXXRuntimeError(
                f"Cannot use '{op}' with a list."
            )

        match op:
            case "+":
                # String + anything = string concatenation
                if isinstance(lv, str) or isinstance(rv, str):
                    if lv is None or rv is None:
                        raise IXXRuntimeError(
                            "Cannot concatenate text with nothing. "
                            "Use an if check or provide a default value."
                        )
                    return _display(lv) + _display(rv)
                try:
                    return lv + rv          # type: ignore[operator]
                except TypeError:
                    raise IXXRuntimeError(
                        f"Cannot use '+' with {_ixx_err_type(lv)} and {_ixx_err_type(rv)}."
                    )
            case "-":
                try:
                    return lv - rv          # type: ignore[operator]
                except TypeError:
                    raise IXXRuntimeError(
                        f"Cannot use '-' with {_ixx_err_type(lv)} and {_ixx_err_type(rv)}."
                    )
            case "*":
                try:
                    return lv * rv          # type: ignore[operator]
                except TypeError:
                    raise IXXRuntimeError(
                        f"Cannot use '*' with {_ixx_err_type(lv)} and {_ixx_err_type(rv)}."
                    )
            case "/":
                if rv == 0:
                    raise IXXRuntimeError(
                        "You tried to divide by zero — that's not possible."
                    )
                try:
                    result = lv / rv        # type: ignore[operator]
                except TypeError:
                    raise IXXRuntimeError(
                        f"Cannot use '/' with {_ixx_err_type(lv)} and {_ixx_err_type(rv)}."
                    )
                # Return int when both inputs are integers and result is whole
                if (
                    isinstance(lv, int) and isinstance(rv, int)
                    and result == int(result)
                ):
                    return int(result)
                return result
            case _:
                raise IXXRuntimeError("That arithmetic operation is not supported.")

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
                    # If the LEFT operand is bool it means a previous comparison
                    # produced YES/NO — the user is chaining comparisons.
                    if isinstance(a, bool):
                        raise IXXRuntimeError(
                            "Comparisons cannot be chained. "
                            f"Use 'and': if a {op} b and b {op} c"
                        )
                    raise IXXRuntimeError(
                        "Cannot use YES/NO in numeric comparisons. "
                        "Use 'is' or 'is not' to compare yes-or-no values (YES / NO)."
                    )
                try:
                    match op:
                        case "less than": return a < b   # type: ignore[operator]
                        case "more than": return a > b   # type: ignore[operator]
                        case "at least":  return a >= b  # type: ignore[operator]
                        case "at most":   return a <= b  # type: ignore[operator]
                except TypeError:
                    raise IXXRuntimeError(
                        f"Cannot compare {_ixx_err_type(a)} and {_ixx_err_type(b)} "
                        f"using '{op}'. Both values must be numbers or both must be text."
                    )
            case "contains":
                if isinstance(a, list):
                    # Warn if element types don't match
                    if a and type(a[0]) != type(b):
                        print(
                            f"Warning: types don't match in 'contains' — "
                            f"looking for {_ixx_err_type(b)} in a list of "
                            f"{_ixx_err_type(a[0])}",
                            file=sys.stderr,
                        )
                    return b in a
                if isinstance(a, str):
                    return _display(b) in a
                raise IXXRuntimeError(
                    f"'contains' only works on lists and text, not {_ixx_err_type(a)}."
                )
            case _:
                raise IXXRuntimeError("That comparison is not supported.")
        return False  # unreachable, satisfies type checker
