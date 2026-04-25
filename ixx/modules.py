"""
IXX module resolver — handles `use "file.ixx"` and `use std "module"` imports.

Only FuncDef nodes from imported files are collected; top-level statements
(say, assignment, etc.) in imported files are silently ignored.

Public API:
    resolve_imports(program, base_dir) -> dict[str, FuncDef]
    IXXImportError   — raised for missing file / cycle / duplicate function
"""

from __future__ import annotations
import os
import importlib.resources
from .ast_nodes import Program, FuncDef, UseStmt


class IXXImportError(Exception):
    """Raised when an import fails: missing file, circular import, or duplicate function name."""

    def __init__(self, message: str, line: int | None = None):
        super().__init__(message)
        self.line = line


def _short(path: str) -> str:
    """Return a short display name for a path (basename only)."""
    return os.path.basename(path)


def _resolve_std_path(module_name: str) -> str:
    """Return the absolute filesystem path for a stdlib module.

    Uses importlib.resources so it works both from source and from a wheel.
    """
    try:
        ref = importlib.resources.files("ixx.stdlib").joinpath(f"{module_name}.ixx")
        with importlib.resources.as_file(ref) as p:
            return str(p)
    except (FileNotFoundError, TypeError, AttributeError):
        raise IXXImportError(
            f"Standard library module not found: '{module_name}'. "
            f"Run 'ixx help' for available modules."
        )


def _collect_funcs(
    program: Program,
    source_label: str,
    accumulator: dict[str, FuncDef],
) -> None:
    """Add FuncDef nodes from *program* into *accumulator*, checking for duplicates."""
    for stmt in program.body:
        if isinstance(stmt, FuncDef):
            if stmt.name in accumulator:
                raise IXXImportError(
                    f"Duplicate function '{stmt.name}' from {source_label}. "
                    "Function names must be unique across imports."
                )
            accumulator[stmt.name] = stmt


def resolve_imports(
    program: Program,
    base_dir: str,
    _stack: list[str] | None = None,
) -> dict[str, FuncDef]:
    """Walk all UseStmt nodes in *program* and return all imported FuncDef nodes.

    Arguments:
        program   — already-parsed Program AST for the importing file.
        base_dir  — directory of the importing file, used to resolve relative paths.
        _stack    — internal: list of canonical absolute paths currently being loaded
                    (used for cycle detection — do not pass from outside).

    Returns:
        dict mapping function name → FuncDef for every function imported (directly
        or transitively).  Only FuncDef nodes are collected; top-level statements
        in imported files are silently skipped.

    Raises:
        IXXImportError  on missing file, circular import, or duplicate function name.
    """
    from .parser import parse  # local import to avoid module-level circularity

    if _stack is None:
        _stack = []

    result: dict[str, FuncDef] = {}

    for stmt in program.body:
        if not isinstance(stmt, UseStmt):
            continue

        # ── resolve the physical path ─────────────────────────────────────
        if stmt.kind == "file":
            abs_path = os.path.realpath(
                os.path.join(base_dir, stmt.path)
            )
            if not os.path.isfile(abs_path):
                raise IXXImportError(
                    f"Import file not found: {stmt.path}",
                    line=stmt.line,
                )
        else:  # "std"
            try:
                abs_path = _resolve_std_path(stmt.path)
            except IXXImportError as exc:
                # Re-raise with line info attached
                raise IXXImportError(str(exc), line=stmt.line) from exc

        # ── cycle detection ───────────────────────────────────────────────
        if abs_path in _stack:
            chain = " -> ".join(_short(p) for p in _stack) + " -> " + _short(abs_path)
            raise IXXImportError(
                f"Circular import detected: {chain}",
                line=stmt.line,
            )

        # ── parse the imported file ───────────────────────────────────────
        try:
            with open(abs_path, encoding="utf-8") as f:
                source = f.read()
        except OSError as e:
            raise IXXImportError(
                f"Cannot read import file '{stmt.path}': {e}",
                line=stmt.line,
            ) from e

        from lark.exceptions import UnexpectedInput
        try:
            child_program = parse(source)
        except UnexpectedInput as e:
            raise IXXImportError(
                f"Syntax error in import '{stmt.path}': {e}",
                line=stmt.line,
            ) from e

        # ── recurse into transitive imports ───────────────────────────────
        child_dir = os.path.dirname(abs_path)
        child_imports = resolve_imports(
            child_program, child_dir, _stack + [abs_path]
        )

        # Merge transitive imports first, then this file's own functions
        for name, func in child_imports.items():
            if name in result:
                raise IXXImportError(
                    f"Duplicate function '{name}' introduced by '{stmt.path}'. "
                    "Function names must be unique across imports.",
                    line=stmt.line,
                )
            result[name] = func

        _collect_funcs(child_program, _short(abs_path), result)

    return result
