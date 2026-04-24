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

@dataclass
class BoolLit:
    value: bool

@dataclass
class ListLit:
    items: list["Expr"]

@dataclass
class VarRef:
    name: str

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

Expr = (
    IntLit | FloatLit | StrLit | BoolLit | ListLit | VarRef |
    NegOp | BinOp | Compare | AndOp | OrOp | NotOp | CallExpr
)


# ── statement nodes ────────────────────────────────────────────────────────────

@dataclass
class Assign:
    name: str
    value: Expr

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
class Say:
    args: list[Expr]

@dataclass
class CallStmt:
    """Statement-position function call: space-separated args, e.g. greet "World"."""
    name: str
    args: list[Expr]

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

Stmt = Assign | If | Loop | Say | CallStmt | ReturnStmt | FuncDef

@dataclass
class Program:
    body: list[Stmt]
