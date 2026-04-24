---
name: IXX v0.4 Implementation
overview: "Implement the full v0.3.8 + v0.4 scope: bug fixes, function system, built-ins, updated demo, interactive demo routing, and terminal color env-var support. v0.5+ roadmap items (records, try/error, modules) are preserved as pending todos but not implemented."
todos: []
isProject: false
---

# IXX v0.4 Implementation Plan

## State of play

- Grammar, AST, interpreter have NO function support yet — all pre-function
- `tests/test_functions.py` is already written with 40+ tests (all currently failing)
- `tests/test_functions.py` includes `TestRecords` and `TestTryError` — these are v0.5 and will be skipped with `@unittest.skip`
- `examples/try-it.ixx` still uses broken comma-string list pattern
- `ixx demo` now routes to walkthrough (fixed in 0.3.7) but the walkthrough has no function steps
- `renderer.py` has color codes but no `NO_COLOR`/`IXX_COLOR` env-var support

---

## Pass 1 — v0.3.8 bug fixes

All in [`ixx/preprocessor.py`](ixx/preprocessor.py) and [`ixx/interpreter.py`](ixx/interpreter.py).

**`preprocessor.py`** — strip blank/whitespace-only lines before Lark Indenter sees them:
```python
lines = [l for l in lines if l.strip() != '']
```

**`interpreter.py`** — five fixes:
- `_interpolate`: on undefined variable → `print(f"[warning: '{name}' is not defined]", file=sys.stderr)` then return original `{name}` token
- `Loop._exec`: add iteration counter; raise at 10,000: `"loop ran more than 10,000 times — did you forget to update the condition?"`
- `_eval_binop` and `_eval_compare`: guard both operands — if either is `bool`, raise `"Cannot use YES/NO in arithmetic"` / `"Cannot compare YES/NO with ordering operators"`
- `_eval_compare` `contains` on list: if `type(b) != type(a[0])`, write to stderr: `"[warning: types don't match in contains — comparing {type(b)} against list of {type(a[0])}]"`

---

## Pass 2 — v0.4 grammar (Earley + functions)

### [`ixx/grammar.lark`](ixx/grammar.lark)

Add three statement types and new expression form. Switch to Earley (in parser.py).

```lark
statement: assignment _NEWLINE
         | func_def
         | call_stmt _NEWLINE
         | return_stmt _NEWLINE
         | if_stmt
         | loop_stmt
         | say_stmt _NEWLINE

func_def: "function" IDENTIFIER params _NEWLINE block
params: (IDENTIFIER ("," IDENTIFIER)*)?

call_stmt: IDENTIFIER (expr ("," expr)*)?

return_stmt: "return" expr?

?primary: "(" expr ")"
        | MINUS primary          -> neg_op
        | INT                    -> int_lit
        | FLOAT                  -> float_lit
        | ESCAPED_STRING         -> str_lit
        | YES                    -> yes_lit
        | NO                     -> no_lit
        | IDENTIFIER "(" (expr ("," expr)*)? ")"  -> call_expr_paren
        | IDENTIFIER             -> var_ref
```

Call expressions in RHS use parentheses for clarity: `sum = add(5, 3)`. Call statements at top level use space-separated args: `greet "World"`. This avoids the `x = a, b` ambiguity entirely.

Test cases that use `sum = add 5, 3` (space-separated in RHS) will use the call_stmt form instead. Looking at the test file: `sum = add 5, 3` — this means the assignment RHS starts with a call_stmt expression. The call_stmt grammar handles `IDENTIFIER expr+` at statement level. For assignment RHS, call_expr_paren uses parens.

**Revised approach for test compatibility** — the test file uses both `sum = add 5, 3` (no parens) and `factorial (n - 1)` (with parens). To support both:
- Add `call_args: expr ("," expr)*` as a sub-rule
- `call_expr` in primary: `IDENTIFIER call_args -> call_expr` — only fires in Earley when IDENTIFIER is followed by a non-comma, non-newline expression. Earley with `ambiguity="resolve"` picks the longer match.
- Assignment RHS uses `expr ("," expr)*` — if the first expr resolves to a `call_expr`, the commas are consumed as call args; otherwise they form a list.

### [`ixx/parser.py`](ixx/parser.py)

```python
_parser = Lark(grammar, parser="earley", ambiguity="resolve",
               lexer="dynamic", propagate_positions=False)
```

---

## Pass 3 — v0.4 AST nodes

### [`ixx/ast_nodes.py`](ixx/ast_nodes.py)

```python
@dataclass
class FuncDef:
    name: str
    params: list[str]
    body: list["Stmt"]

@dataclass
class CallExpr:
    name: str
    args: list["Expr"]

@dataclass
class CallStmt:
    name: str
    args: list["Expr"]

@dataclass
class ReturnStmt:
    value: "Expr | None"
```

Update `Stmt` union to include `FuncDef | CallStmt | ReturnStmt`.
Update `Expr` union to include `CallExpr`.

### [`ixx/build_ast.py`](ixx/build_ast.py)

Add transformer methods: `func_def`, `params`, `call_stmt`, `call_expr`, `call_expr_paren`, `return_stmt`.

---

## Pass 4 — v0.4 interpreter

### [`ixx/interpreter.py`](ixx/interpreter.py)

**`_ReturnSignal`**:
```python
class _ReturnSignal(Exception):
    def __init__(self, value): self.value = value
```

**`BUILT_INS`** dict — registered at module level. v0.4 built-ins:
- `count(x)` — `len(x)` for list or str
- `text(x)` — `_display(x)`
- `number(x)` — `int` or `float` from str
- `type(x)`