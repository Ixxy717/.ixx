---
name: IXX v0.4 Functions
overview: Implement v0.3.8 bug fixes, v0.4 function system with LALR grammar, built-ins, updated demo, interactive demo routing, and terminal color env-var support. v0.5+ items (records, try/error, modules) stay as pending todos.
todos:
  - id: v038-bugs
    content: "preprocessor blank lines + interpreter: loop limit, bool-int guard, interpolation {?name} warning, contains type warning"
    status: completed
  - id: v040-grammar
    content: "grammar.lark: func_def, call_stmt (space-style), call_expr (parens-required), return_stmt, params — LALR stays"
    status: completed
  - id: v040-ast
    content: "ast_nodes.py + build_ast.py: FuncDef, CallExpr, CallStmt, ReturnStmt + transformer methods"
    status: completed
  - id: v040-tests-update
    content: "test_functions.py: update expression-position calls to parens, skip TestRecords + TestTryError"
    status: completed
  - id: v040-interpreter
    content: "interpreter.py: BUILT_INS dict, function table, two-pass, _ReturnSignal, clean scope, call depth 500, type() returns IXX words, number() friendly errors"
    status: completed
  - id: v040-colors
    content: "renderer.py: NO_COLOR / IXX_COLOR env vars, _GREEN, show_error/show_success; __main__.py uses show_error; add color env-var tests"
    status: completed
  - id: v040-demo-script
    content: Rewrite examples/try-it.ixx + ixx/assets/try-it.ixx with correct v0.4 syntax
    status: completed
  - id: v040-demo-walk
    content: "demo_walk.py: 10 updated steps (functions+built-ins), _input_fn param for testability; __main__.py demo routing (demo = script, demo interactive = walkthrough)"
    status: completed
  - id: v040-docs
    content: spec/language.md functions section, roadmap update, examples/functions.ixx
    status: completed
  - id: v040-version
    content: Bump to 0.4.0-dev / 0.4.0.dev0; mark stable only after manual verification
    status: completed
isProject: false
---

# IXX v0.4 Functions

## Definitive call syntax (v0.4 rule — no ambiguity)

**Statement position** (standalone line at any block depth) — space-separated args:
```
greet "World"
countdown 3
greet("World")   # parens also accepted here
```

**Expression position** (RHS of `=`, inside `say`, inside `if`/`loop`, inside another call) — REQUIRES parentheses:
```
total = add(5, 3)
result = factorial(n - 1)
say check(15)
r = dowork()
```

This keeps the parser LALR(1) with zero ambiguity. No Earley switch needed.
`test_functions.py` will be updated to use this rule throughout (see Pass 3).

---

## Pass 1 — v0.3.8 bug fixes

Files: [`ixx/preprocessor.py`](ixx/preprocessor.py), [`ixx/interpreter.py`](ixx/interpreter.py)

**`preprocessor.py`** — strip blank/whitespace-only lines before Lark Indenter:
```python
lines = [l for l in lines if l.strip() != '']
```
Known side effect: source line numbers in syntax errors will be offset. Document as known limitation for v0.4; a source line map can be added later.

**`interpreter.py`** — five targeted fixes:

- `_interpolate`: undefined variable → write `[warning: '{name}' is not defined]` to `sys.stderr` and replace with `{?name}` in output (visibly wrong, testable):
  ```python
  print(f"[warning: '{name}' is not defined]", file=sys.stderr)
  return f"{{?{name}}}"
  ```
- `Loop._exec`: add iteration counter, raise at 10,000:
  `"loop ran more than 10,000 times — did you forget to update the condition?"`
- `_eval_binop` + `_eval_compare`: if either operand is `bool`, raise before operating:
  `"Cannot use YES/NO in arithmetic"` / `"Cannot compare YES/NO with ordering operators"`
- `_eval_compare` `contains` on list: if `type(b) != type(a[0])`, write to `sys.stderr`:
  `"[warning: types don't match in contains — ...]"` (does not raise, returns result)

---

## Pass 2 — v0.4 grammar (LALR stays)

File: [`ixx/grammar.lark`](ixx/grammar.lark)

Add three statement types. Add `call_expr` to primary using explicit parens (LALR-safe):

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

// Statement-level call: space-separated args, no parens required
call_stmt: IDENTIFIER (expr ("," expr)*)?

return_stmt: "return" expr?

// Expression-level call: parentheses required — unambiguous in LALR
?primary: "(" expr ")"
        | MINUS primary                              -> neg_op
        | INT                                        -> int_lit
        | FLOAT                                      -> float_lit
        | ESCAPED_STRING                             -> str_lit
        | YES                                        -> yes_lit
        | NO                                         -> no_lit
        | IDENTIFIER "(" (expr ("," expr)*)? ")"     -> call_expr
        | IDENTIFIER                                 -> var_ref
```

Disambiguation for `call_stmt` at statement level: LALR(1) uses one-token lookahead after `IDENTIFIER`:
- `IDENTIFIER "="` → `assignment` fires
- `IDENTIFIER "("`... wait, `IDENTIFIER "(" ...` could be `call_stmt` with a paren-expr as first arg OR `call_expr` inside assignment. Since `call_stmt` is at the statement rule level and `call_expr` is in primary, there is no conflict: a statement starting `IDENTIFIER` without `"="` is always a `call_stmt`; the `"("` case would appear inside the call_stmt's args as a paren-grouped expression.

**Unknown bare words**: `foo` alone on a line parses as `call_stmt("foo", [])`. At runtime, if `foo` is not in the function table or built-ins, the interpreter raises: `"'foo' is not a function. Tip: define it with: function foo ..."`. This replaces the old "unknown variable" path for top-level bare words. Current behavior is preserved because bare top-level words were previously syntax errors anyway.

No changes needed to [`ixx/parser.py`](ixx/parser.py) — LALR stays.

---

## Pass 3 — v0.4 AST + build_ast

File: [`ixx/ast_nodes.py`](ixx/ast_nodes.py) — add four node types:

```python
@dataclass
class FuncDef:
    name: str
    params: list[str]
    body: list["Stmt"]

@dataclass
class CallExpr:       # expression position — parens in source
    name: str
    args: list["Expr"]

@dataclass
class CallStmt:       # statement position — space-separated in source
    name: str
    args: list["Expr"]

@dataclass
class ReturnStmt:
    value: "Expr | None"
```

Update `Stmt` and `Expr` type aliases.

File: [`ixx/build_ast.py`](ixx/build_ast.py) — add transformer methods:
`func_def`, `params`, `call_stmt`, `call_expr`, `return_stmt`.

File: [`tests/test_functions.py`](tests/test_functions.py) — update tests to match parens-in-expression rule:

| Original | Updated |
|---|---|
| `sum = add 5, 3` | `sum = add(5, 3)` |
| `msg = greet "Ixxy"` | `msg = greet("Ixxy")` |
| `say check 15` | `say check(15)` |
| `say check 21` | `say check(21)` |
| `sub = factorial (n - 1)` | `sub = factorial(n - 1)` |
| `say factorial 5` | `say factorial(5)` |
| `result = noop` | `result = noop()` |
| `r = dowork` | `r = dowork()` |
| `result = min 3, 1, 4` | `result = min(3, 1, 4)` |
| `result = max 3, 1, 4` | `result = max(3, 1, 4)` |
| `parts = split "a,b,c", ","` | `parts = split("a,b,c", ",")` |
| `result = join items, "-"` | `result = join(items, "-")` |
| `result = replace "hello world", "world", "IXX"` | `result = replace("hello world", "world", "IXX")` |

Call statements without return values stay space-separated: `greet "World"`, `countdown 3`, `divider`.

Add `@unittest.skip` to `TestRecords` and `TestTryError` (v0.5, not implemented).

In `TestBuiltins`, skip the v0.5 built-in tests (upper, lower, trim, length, round, floor, ceil, abs, min, max, sqrt, power, first, last, sort, reverse, unique, split, join, replace) with a class-level `@unittest.skip` or individual decorators. Only the five v0.4 built-in tests (count, text, number, type, and any ask tests) should remain active.

---

## Pass 4 — v0.4 interpreter

File: [`ixx/interpreter.py`](ixx/interpreter.py)

**`_ReturnSignal`** exception class.

**`BUILT_INS`** dict — v0.4 only (five essential built-ins):

| Name | Behavior |
|---|---|
| `count(x)` | `len(x)` for list or str |
| `text(x)` | `_display(x)` — converts any value to its IXX text representation |
| `number(x)` | `int` or `float` from str — wraps `ValueError` in `IXXRuntimeError`: `"Cannot convert '{x}' to a number"` |
| `type(x)` | returns IXX words: `"text"` / `"number"` / `"bool"` / `"list"` / `"nothing"` — never exposes Python type names (`str`, `int`, `NoneType`, etc.) |
| `ask(prompt)` | `input(str(prompt))` |

**v0.5 built-ins (NOT in this run):** `upper`, `lower`, `trim`, `length`, `round`, `floor`, `ceil`, `abs`, `min`, `max`, `sqrt`, `power`, `first`, `last`, `sort`, `reverse`, `unique`, `split`, `join`, `replace` — these belong to the v0.5 full text/number/list library and are preserved as pending roadmap items.

**`Interpreter`** changes:

- `__init__`: add `self._func_table: dict[str, FuncDef] = {}` and `self._call_depth = 0`
- `run(program)`: two-pass — collect all `FuncDef`s into `_func_table` first, then execute. Store `global_env` reference on `self`.
- `_exec`: add cases for `FuncDef` (skip — already collected), `CallStmt` (dispatch), `ReturnStmt` (raise `_ReturnSignal` or raise `IXXRuntimeError("'return' can only be used inside a function")` if not in call)
- `_eval`: add case for `CallExpr` (same dispatch as `CallStmt` but returns value)
- `_call(func, arg_values)`: clean local scope, `_parent = global_env` (reads globals, writes local), call depth limit 500, catch `_ReturnSignal`

Error messages:
- Wrong arg count: `"'add' expects 2 argument(s), got 1. Parameters: a, b"`
- Unknown function/built-in: `"'foo' is not a function. Tip: define it with: function foo ..."`
- Return outside function: caught by `_ReturnSignal` escaping `run()` (add a top-level catch)

---

## Pass 5 — terminal color env-var support

File: [`ixx/shell/renderer.py`](ixx/shell/renderer.py)

Update `_enable_ansi()` to check env vars before TTY check:
```python
def _enable_ansi() -> bool:
    import os
    if os.environ.get("NO_COLOR"):      # https://no-color.org/
        return False
    ixx = os.environ.get("IXX_COLOR")
    if ixx == "0":
        return False
    if ixx == "1":
        return True                     # force-on
    # ... existing TTY + Windows VTP logic ...
```

Add `_GREEN = "\033[32m"`.

Add `show_error(msg: str) -> None` using `_RED`.
Add `show_success(msg: str) -> None` using `_GREEN`.

Use `show_error` in [`ixx/__main__.py`](ixx/__main__.py) for `IXXRuntimeError` and file-not-found output.

Add tests in [`tests/test_shell.py`](tests/test_shell.py):
```python
def test_no_color_env_disables_ansi(self):
    with patch.dict(os.environ, {"NO_COLOR": "1"}):
        import importlib; importlib.reload(renderer)
        self.assertFalse(renderer._ANSI)

def test_ixx_color_0_disables_ansi(self):
    with patch.dict(os.environ, {"IXX_COLOR": "0"}, clear_existing=False):
        ...

def test_ixx_color_1_forces_ansi(self):
    with patch.dict(os.environ, {"IXX_COLOR": "1"}, clear_existing=False):
        ...
```

Note: `_ANSI` is a module-level constant set at import. Tests will need to reload the module or patch `renderer._ANSI` directly to avoid import-order issues.

---

## Pass 6 — updated demo script

Files: [`examples/try-it.ixx`](examples/try-it.ixx) and [`ixx/assets/try-it.ixx`](ixx/assets/try-it.ixx)

Rewrite using correct v0.4 syntax. Key constraints:
- No `{expr}` interpolation — compute into a variable first
- No comma-string fake lists — use `"a", "b", "c"`
- Include functions, return values, built-ins

Skeleton:
```
say "Hello, World!"

name = "Ixxy"
say "Hello, {name}"

x = 10
y = 5
total = x + y
say "Sum: {total}"

if total at least 10
- say "Total is large"
else
- say "Total is small"

n = 1
loop n at most 3
- say "Count: {n}"
- n = n + 1

langs = "python", "rust", "ixx", "go"
if langs contains "ixx"
- say "ixx found in list"
n_langs = count(langs)
say "Languages: {n_langs}"

function greet who
- say "Hello from function: {who}"

greet "Ixxy"

function add a, b
- return a + b

result = add(10, 5)
say "10 + 5 = {result}"

t = type(result)
say "Type of result: {t}"
```

---

## Pass 7 — interactive demo update

File: [`ixx/shell/commands/demo_walk.py`](ixx/shell/commands/demo_walk.py)

Add `_input_fn` parameter for testability:
```python
def handle_demo_walk(args: list[str], _input_fn=None) -> None:
    if _input_fn is None:
        _input_fn = input
```

Update `_STEPS` to 10 steps covering full v0.4 language. All code snippets must follow the v0.4 call syntax (parens in expression position). Suggested steps:

1. Hello World
2. Variables and interpolation (with explicit intermediate var for computed values)
3. If / else
4. Loops
5. Lists and contains
6. Functions (define and call as statement)
7. Return values (call in expression position with parens)
8. Built-ins (`count`, `type`, `text`, `number`)
9. Nested functions + recursion teaser
10. Shell preview — hint about `ixx shell`, `ip wifi`, `cpu`, etc.

File: [`ixx/__main__.py`](ixx/__main__.py) — demo routing:
```python
if cmd == "demo":
    sub = args[0] if args else None
    if sub in ("interactive", "walkthrough"):
        from .shell.commands.demo_walk import handle_demo_walk
        handle_demo_walk([])
    else:
        import importlib.resources
        ref = importlib.resources.files("ixx.assets").joinpath("try-it.ixx")
        with importlib.resources.as_file(ref) as p:
            _run_file(str(p))
    return
```

Add tests for interactive demo in [`tests/test_shell.py`](tests/test_shell.py):
```python
def test_demo_walk_steps_with_mocked_input(self):
    """All steps complete when Enter is pressed each time."""
    ...mock _input_fn returning "" for each step...

def test_demo_walk_q_exits_early(self):
    """Typing q at any step exits the walkthrough."""
    ...mock _input_fn returning "q"...
```

---

## Pass 8 — docs and examples

- [`spec/language.md`](spec/language.md) — add section: Functions (syntax, params, return, clean scope, built-ins table). Show call syntax rule explicitly.
- [`spec/roadmap.md`](spec/roadmap.md) — mark v0.3.8 and v0.4 complete, keep v0.5-v0.7 pending.
- [`examples/functions.ixx`](examples/functions.ixx) — new file with greet, add, check_age, factorial (showing both call styles).

---

## Pass 9 — version bump

- [`ixx/_version.py`](ixx/_version.py): `VERSION = "0.4.0-dev"`
- [`pyproject.toml`](pyproject.toml): `version = "0.4.0.dev0"` (PEP 440 dev format for PyPI compatibility)
- Mark stable (`0.4.0`) only after all tests pass and manual verification is done.

---

## Preserved roadmap — NOT implemented in this run

- `v050-builtins`: full text/number/list built-in library
- `v050-modules`: `use` / `from use` module system
- `v050-records`: `record` keyword, dot access
- `v050-errors`: `try` / `if error` error handling
- `v060-command`: `command` keyword, IXX-defined shell commands
- `v070-native`: native bridge, self-hosting stdlib
