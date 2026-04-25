"""
Lark -> IXX AST transformer.

Each method name matches a grammar rule alias (-> name) or rule name.
Lark calls them bottom-up, so every child is already an AST node when
the parent method runs.
"""

from __future__ import annotations
from lark import Transformer
from .ast_nodes import (
    Program, Assign, If, Loop, Say,
    IntLit, FloatLit, StrLit, BoolLit, NothingLit, ListLit, VarRef,
    NegOp, BinOp, Compare, AndOp, OrOp, NotOp,
    CallExpr, CallStmt, ReturnStmt, FuncDef, TryCatch,
)


class IXXTransformer(Transformer):

    # ── program ────────────────────────────────────────────────────────────────

    def start(self, items):
        return Program(body=[s for s in items if s is not None])

    # ── statements ─────────────────────────────────────────────────────────────

    def statement(self, items):
        return items[0]

    def assignment(self, items):
        name = str(items[0])
        line = getattr(items[0], "line", None)
        exprs = list(items[1:])
        value = ListLit(items=exprs) if len(exprs) > 1 else exprs[0]
        return Assign(name=name, value=value, line=line)

    def if_stmt(self, items):
        cond       = items[0]
        then_block = items[1]
        else_block = items[2] if len(items) > 2 else []
        return If(condition=cond, then_body=then_block, else_body=else_block)

    def loop_stmt(self, items):
        cond, body = items
        return Loop(condition=cond, body=body)

    def say_stmt(self, items):
        return Say(args=list(items))

    def call_stmt(self, items):
        name = str(items[0])
        line = getattr(items[0], "line", None)
        args = list(items[1:])
        return CallStmt(name=name, args=args, line=line)

    def return_stmt(self, items):
        value = items[0] if items else None
        return ReturnStmt(value=value)

    def func_def(self, items):
        name = str(items[0])
        line = getattr(items[0], "line", None)
        # items[1] is either func_params (list[str]) or a block (list[Stmt])
        # items[-1] is always the block
        if len(items) == 3:
            params = list(items[1])
            body   = items[2]
        else:
            params = []
            body   = items[1]
        return FuncDef(name=name, params=params, body=body, line=line)

    def func_params(self, items):
        return [str(t) for t in items]

    def try_stmt(self, items):
        try_body   = items[0]
        catch_body = items[1] if len(items) > 1 else []
        return TryCatch(try_body=try_body, catch_body=catch_body)

    def block(self, items):
        return [s for s in items if s is not None]

    # ── function call expression ────────────────────────────────────────────────

    def call_expr(self, items):
        name = str(items[0])
        line = getattr(items[0], "line", None)
        args = list(items[1:])
        return CallExpr(name=name, args=args, line=line)

    # ── literals ───────────────────────────────────────────────────────────────

    def int_lit(self, items):
        return IntLit(value=int(items[0]))

    def float_lit(self, items):
        return FloatLit(value=float(items[0]))

    def str_lit(self, items):
        raw = str(items[0])
        return StrLit(value=raw[1:-1])      # strip surrounding quotes

    def yes_lit(self, _):
        return BoolLit(value=True)

    def no_lit(self, _):
        return BoolLit(value=False)

    def nothing_lit(self, _):
        return NothingLit()

    def var_ref(self, items):
        line = getattr(items[0], "line", None)
        return VarRef(name=str(items[0]), line=line)

    # ── arithmetic ─────────────────────────────────────────────────────────────

    def neg_op(self, items):
        # items[0] is the MINUS token; items[1] is the operand
        return NegOp(operand=items[-1])

    def add_expr(self, items):
        return self._fold_binop(items)

    def mul_expr(self, items):
        return self._fold_binop(items)

    def _fold_binop(self, items):
        result = items[0]
        i = 1
        while i < len(items):
            result = BinOp(op=str(items[i]), left=result, right=items[i + 1])
            i += 2
        return result

    # ── comparisons ────────────────────────────────────────────────────────────
    # Each compare rule alias produces exactly (left, right) children.

    def op_is(self, items):
        return Compare(op="is", left=items[0], right=items[1])

    def op_is_not(self, items):
        return Compare(op="is not", left=items[0], right=items[1])

    def op_less_than(self, items):
        return Compare(op="less than", left=items[0], right=items[1])

    def op_more_than(self, items):
        return Compare(op="more than", left=items[0], right=items[1])

    def op_at_least(self, items):
        return Compare(op="at least", left=items[0], right=items[1])

    def op_at_most(self, items):
        return Compare(op="at most", left=items[0], right=items[1])

    def op_contains(self, items):
        return Compare(op="contains", left=items[0], right=items[1])

    # ── logic ──────────────────────────────────────────────────────────────────

    def or_op(self, items):
        return OrOp(left=items[0], right=items[1])

    def and_op(self, items):
        return AndOp(left=items[0], right=items[1])

    def not_op(self, items):
        return NotOp(operand=items[0])
