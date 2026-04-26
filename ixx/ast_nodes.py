"""
AST node dataclasses for IXX.

Each node type maps directly to one concept in the language.
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ── value types ────────────────────────────────────────────────────────────────

IXXValue = int | float | str | bool | list | None


# ── expression nodes ───────────────────────────────────────────────────────────

@dataclass
class IntLit:
    value: int

@dataclass
class FloatLit:
    value: float

@dataclass
class StrLit:
    value: str
    line: int | None = None

@dataclass
class BoolLit:
    value: bool

@dataclass
class NothingLit:
    """The literal `nothing` — IXX null value."""
    pass

@dataclass
class ListLit:
    items: list["Expr"]

@dataclass
class VarRef:
    name: str
    line: int | None = None

@dataclass
class NegOp:
    operand: "Expr"

@dataclass
class BinOp:
    op: str    # "+", "-", "*", "/"
    left: "Expr"
    right: "Expr"

@dataclass
class Compare:
    op: str    # "is", "is not", "less than", "more than", "at least", "at most", "contains"
    left: "Expr"
    right: "Expr"

@dataclass
class AndOp:
    left: "Expr"
    right: "Expr"

@dataclass
class OrOp:
    left: "Expr"
    right: "Expr"

@dataclass
class NotOp:
    operand: "Expr"

@dataclass
class CallExpr:
    """Expression-position function call: must use parentheses, e.g. add(5, 3)."""
    name: str
    args: list["Expr"]
    line: int | None = None

Expr = (
    IntLit | FloatLit | StrLit | BoolLit | NothingLit | ListLit | VarRef |
    NegOp | BinOp | Compare | AndOp | OrOp | NotOp | CallExpr
)


# ── statement nodes ────────────────────────────────────────────────────────────

@dataclass
class Assign:
    name: str
    value: Expr
    line: int | None = None

@dataclass
class If:
    condition: Expr
    then_body: list["Stmt"]
    else_body: list["Stmt"] = field(default_factory=list)

@dataclass
class Loop:
    condition: Expr
    body: list["Stmt"]

@dataclass
class LoopEach:
    """loop each <var_name> in <iterable> — list iteration."""
    var_name: str
    iterable: Expr
    body: list["Stmt"]
    line: int | None = None

@dataclass
class Say:
    args: list[Expr]

@dataclass
class CallStmt:
    """Statement-position function call: space-separated args, e.g. greet "World"."""
    name: str
    args: list[Expr]
    line: int | None = None

@dataclass
class ReturnStmt:
    """Return from a function.  value is None for bare `return`."""
    value: "Expr | None"

@dataclass
class FuncDef:
    """User-defined function definition."""
    name: str
    params: list[str]
    body: list["Stmt"]
    line: int | None = None

@dataclass
class TryCatch:
    """try / catch error handling block."""
    try_body:   list["Stmt"]
    catch_body: list["Stmt"] = field(default_factory=list)

@dataclass
class UseStmt:
    """use "file.ixx"  or  use std "module" import statement."""
    kind: str          # "file" | "std"
    path: str          # e.g. "helpers.ixx" or "time"
    line: int | None = None

Stmt = Assign | If | Loop | LoopEach | Say | CallStmt | ReturnStmt | FuncDef | TryCatch | UseStmt

@dataclass
class Program:
    body: list[Stmt]
