---
name: IXX Function System Design
overview: A complete design for all IXX callable behavior — from user-defined functions through built-ins, standard library, shell commands, native bridge, and remote/database functions — covering syntax, grammar approach, scoping, return values, and a staged release plan through v1.0.
todos:
  - id: v038-bugfixes
    content: "v0.3.8: blank lines, silent interpolation, loop depth, bool-int guard, else error message, contains warning"
    status: completed
  - id: v040-grammar
    content: "v0.4: switch to Earley, add func_def / call_stmt / call_expr / return_stmt to grammar.lark"
    status: completed
  - id: v040-ast
    content: "v0.4: add FuncDef, CallExpr, CallStmt, ReturnStmt to ast_nodes.py and build_ast.py"
    status: completed
  - id: v040-interpreter
    content: "v0.4: function table, local scope, _ReturnSignal, call depth limit, two-pass execution"
    status: completed
  - id: v040-builtins
    content: "v0.4: count, text, number, ask, type built-ins"
    status: completed
  - id: v040-errors
    content: "v0.4: wrong-arg-count, unknown-function, return-outside-function error messages"
    status: completed
  - id: v040-tests
    content: "v0.4: function call, return, scope isolation, recursion, error cases"
    status: completed
  - id: v040-docs
    content: "v0.4: update language.md, roadmap, add examples/functions.ixx"
    status: in_progress
  - id: v050-builtins
    content: "v0.5: full text/number/list built-in library"
    status: pending
  - id: v050-modules
    content: "v0.5: use / from use module system, FunctionTable namespacing"
    status: pending
  - id: v050-records
    content: "v0.5: record objects with dot access"
    status: pending
  - id: v050-errors
    content: "v0.5: try / if error error handling"
    status: pending
  - id: v060-command
    content: "v0.6: command keyword, metadata, registration from .ixx files"
    status: pending
  - id: v070-native
    content: "v0.7: native.* bridge, self-hosting stdlib"
    status: pending
isProject: false
---

# IXX Function System — Complete Design

## Part 0 — Pre-function cleanup (v0.3.8)

Seven confirmed bugs should be fixed before the function system lands. They affect scoping, error messages, and parser stability — all of which functions depend on.

**Blank lines inside blocks kill the parser**
The Lark Indenter sees an empty `\n` as indentation level 0, emitting DEDENT mid-block. Fix in [`ixx/preprocessor.py`](ixx/preprocessor.py): strip blank lines before the Indenter sees them.

```python
def preprocess(source: str) -> str:
    lines = source.split('\n')
    # strip blank/whitespace-only lines before Lark's Indenter sees them
    lines = [l for l in lines if l.strip() != '']
    ...
```

**Silent interpolation failure**
[`ixx/interpreter.py`](ixx/interpreter.py) `_interpolate()` silently leaves `{undefined}` as literal text. This should warn, or in strict mode, error. Minimum fix: print a warning line like `[warning: {name} not defined]` to stderr, or replace with `{?name}` so the output is obviously wrong. Functions will need this fixed because local-scope variables in function bodies are a common source of scoping mistakes.

**YES/bool-int overlap**
Python's `bool` is a subclass of `int`, so `YES more than 0` evaluates to `True > 0 = True`. Guard comparison operators: if either operand is a `bool`, raise a friendly type error rather than silently proceeding.

**else-if indentation**
The error message when `-- else` appears (wrong depth) gives no hint. The grammar error should specifically check whether `else` is indented and suggest: `else must match the dash-depth of its if`.

**contains type-strict on lists**
`ids contains "2"` where `ids = 1, 2, 3` silently returns False. For lists: coerce the search value to the type of each element before comparing, OR document clearly. The safe fix is to show a warning: `[warning: comparing "2" (text) against list of numbers — use number 2 instead]`.

**Variables in if blocks / silent placeholder**
This is the interpolation bug again: `if cond / - result = "x" / say {result}` silently prints `{result}`. Fix is same as interpolation fix above.

**No break/continue/exit**
Document as a known limitation. Add a recursion/loop depth limit (e.g. 10,000 iterations) with a clear error: `loop ran more than 10000 times — did you forget to update the condition?`

---

## Part 1 — The IXX callable model

IXX needs a single unified concept of "a thing you can call." Every callable in IXX is one of these five tiers:

```
Tier 1 — User-defined functions      (v0.4)
         function greet name

Tier 2 — Built-in language functions  (v0.4-v0.5)
         count, upper, lower, round, ask, type, text, number

Tier 3 — Standard library             (v0.5)
         math, files, text, system (written partly in IXX)

Tier 4 — Shell commands               (today as Python handlers)
         ip, cpu, ram, disk, folder size ...
         Later: backed by IXX command definitions (v0.6)

Tier 5 — Native/runtime bridge        (v0.7)
         native primitives the stdlib calls internally
```

The user never sees the tier number. They just call things. The tiers describe implementation.

---

## Part 2 — User-defined functions (v0.4 core target)

### 2.1 Syntax

```
function divider
- say "----------------"

function greet name
- say "Hello, {name}"

function add a, b
- return a + b

function check_age age
- if age less than 18
-- return "Not adult"
- return "Adult"
```

Rules:
- `function` keyword followed by the function name (one identifier)
- Zero or more comma-separated parameter names on the same line
- Body is a dash-block (same `-` / `--` / `---` system as `if`/`loop`)
- `return expr` exits with a value; `return` with no expression exits with `nothing`
- `nothing` is the IXX null — printed as `nothing`, falsy in conditions
- No nested function definitions in v0.4

### 2.2 Grammar changes

Three new statement types added to [`ixx/grammar.lark`](ixx/grammar.lark):

```lark
statement: assignment _NEWLINE
         | func_def
         | call_stmt _NEWLINE       // NEW
         | return_stmt _NEWLINE     // NEW
         | if_stmt
         | loop_stmt
         | say_stmt _NEWLINE

func_def: "function" IDENTIFIER params _NEWLINE block  -> func_def
params: (IDENTIFIER ("," IDENTIFIER)*)?

call_stmt: IDENTIFIER (expr ("," expr)*)?              -> call_stmt

return_stmt: "return" expr?                            -> return_stmt
```

**Call expression (assignment RHS):**

The hard case. `sum = add 5, 3` requires a function call in expression position. The current grammar is LALR(1). Adding `IDENTIFIER expr+` as a primary introduces a shift-reduce conflict.

**Recommended approach: switch parser to Earley.**

Lark supports `parser="earley"` with `ambiguity="resolve"`. For typical IXX script sizes (< 500 lines), Earley is fast enough. The grammar gain is significant: natural syntax with no parens required.

Change in [`ixx/parser.py`](ixx/parser.py):
```python
_parser = Lark(grammar, parser="earley", ambiguity="resolve", ...)
```

Then add to the grammar:
```lark
?primary: "(" expr ")"
        | MINUS primary                      -> neg_op
        | INT                                -> int_lit
        | FLOAT                              -> float_lit
        | ESCAPED_STRING                     -> str_lit
        | YES                                -> yes_lit
        | NO                                 -> no_lit
        | IDENTIFIER call_args               -> call_expr   // function call
        | IDENTIFIER                         -> var_ref

call_args: expr ("," expr)*
```

**Disambiguation rule:** When `IDENTIFIER expr+` is ambiguous with `var_ref` in a list literal context (`a, b, c`), function calls win if the identifier resolves to a known function at runtime. If not a known function, the interpreter raises a clear error: `'add' is not a function and 'add 5' is not valid syntax — did you mean to assign a list?`

This preserves all current syntax (list literals still work: `fruits = "apple", "banana"` because `"apple"` starts with `"` which is unambiguous as an expression, not a call).

**Edge case — no-arg call in expression position:**

`result = divider` is ambiguous: is it calling `divider` (no args) or assigning the value of variable `divider`? Resolution: at runtime, check if the identifier is a function. If yes, call it. If it's a variable, use its value. If neither, error. This is a runtime disambiguation, not grammar-level.

### 2.3 AST nodes

New nodes in [`ixx/ast_nodes.py`](ixx/ast_nodes.py):

```python
@dataclass
class FuncDef:
    name: str
    params: list[str]
    body: list["Stmt"]

@dataclass
class CallExpr:
    name: str
    args: list[Expr]

@dataclass
class CallStmt:
    name: str
    args: list[Expr]

@dataclass
class ReturnStmt:
    value: Expr | None
```

Update `Stmt = Assign | If | Loop | Say | FuncDef | CallStmt | ReturnStmt`
Update `Expr = ... | CallExpr`

### 2.4 Interpreter changes

[`ixx/interpreter.py`](ixx/interpreter.py) changes:

**Function storage:** The `Environment` (or a new `FunctionTable` passed alongside it) stores `FuncDef` objects by name. Functions are global by default in v0.4 — defined once at the top of a script, available everywhere. A two-pass approach can be used: first pass collects all `FuncDef` names, second pass executes. This avoids "function used before definition" errors.

**Return signal:** Use a dedicated exception class (not `IXXRuntimeError`):
```python
class _ReturnSignal(Exception):
    def __init__(self, value): self.value = value
```
`return_stmt` raises `_ReturnSignal(value)`. The function call handler catches it and returns the value. Any `_ReturnSignal` that escapes a function body is a bug — caught at the call site.

**Function call execution:**
```python
case CallExpr(name=name, args=args):
    func = func_table.get(name) or built_ins.get(name)
    if func is None:
        raise IXXRuntimeError(f"'{name}' is not a function. ...")
    arg_values = [self._eval(a, env) for a in args]
    return self._call(func, arg_values, env)

def _call(self, func, arg_values, caller_env):
    if len(arg_values) != len(func.params):
        raise IXXRuntimeError(
            f"'{func.name}' expects {len(func.params)} argument(s), "
            f"got {len(arg_values)}. Parameters: {', '.join(func.params)}"
        )
    local_env = Environment()   # NOT a child of caller_env — functions have clean scope
    for param, val in zip(func.params, arg_values):
        local_env.set(param, val)
    try:
        self._exec_block(func.body, local_env)
    except _ReturnSignal as ret:
        return ret.value
    return None   # IXX nothing
```

### 2.5 Scoping

Functions have **clean lexical scope**. Not a child of the caller's environment.

```
x = 10

function test
- x = 99        # local x — does NOT affect outer x
- say x         # → 99

test
say x           # → 10
```

Functions CAN read global variables (by walking up to a global env):

Design decision: in v0.4, pass a "global env" reference alongside the local env, and use it for `VarRef` lookups if the local scope doesn't have the name. Write always goes to local scope. This matches the user's expectation that functions can reference script-level constants.

```
name = "Ixxy"

function greet
- say "Hello, {name}"    # reads global name

greet                    # → Hello, Ixxy
```

### 2.6 Error messages

- Wrong arg count: `'add' expects 2 arguments, got 1. Parameters: a, b`
- Unknown function: `'foo' is not a function. Tip: check the spelling or define it with: function foo ...`
- Return outside function: `'return' can only be used inside a function`
- Infinite recursion: detect with a call depth counter, raise at depth 500: `Recursion too deep in '{name}' (500 calls deep). Check for a missing base case.`

---

## Part 3 — Built-in language functions (v0.4-v0.5)

Built-ins are callable by name but not defined in any IXX file. They are registered in the interpreter as a `BUILT_INS` dict.

### 3.1 v0.4 built-ins (essential)

```
count items         → number of items in a list or characters in text
text value          → convert number/bool to text
number value        → convert text to number
ask "prompt"        → read user input (interactive)
type value          → "text", "number", "bool", "list", "nothing"
```

### 3.2 v0.5 built-ins

**Text:**
```
upper "hello"               → "HELLO"
lower "HELLO"               → "hello"
trim "  hello  "            → "hello"
split "a,b,c" by ","        → "a", "b", "c"
join items with ", "        → "a, b, c"
replace "hello" "l" with "r" → "herro"
starts "hello" with "he"    → YES
ends "hello" with "lo"      → YES
length "hello"              → 5
```

**Numbers:**
```
round 3.7          → 4
floor 3.7          → 3
ceil 3.2           → 4
abs -5             → 5
min 3, 7, 1        → 1
max 3, 7, 1        → 7
random 1, 10       → number between 1 and 10
```

**Lists:**
```
count items        → 3
first items        → first element
last items         → last element
sort items         → sorted list
reverse items      → reversed list
unique items       → deduplicated list
```

**I/O:**
```
ask "Name?"        → user's input
wait 2             → sleep 2 seconds
clear              → clear screen
```

**Note on syntax:** Multi-arg built-ins use commas: `split "a,b" by ","`. The `by`, `with`, `between` words are part of the call syntax for specific built-ins — not general keyword args. This is a small set of named forms, not a general keyword-argument system.

---

## Part 4 — Standard library (v0.5)

The stdlib is a set of IXX-native modules backed by native bridge calls where needed. Where possible, stdlib functions are written in `.ixx` files that ship with the package.

The `use` keyword loads a stdlib module:

```
use math
use files
use text
use system
```

Modules expose functions into the current scope with a namespace prefix:

```
use math
result = math.round 3.7
```

Or with import-into-scope (v0.5+):

```
from math use round, floor
result = round 3.7
```

### Planned standard library domains

```
math         round, floor, ceil, abs, min, max, random, sqrt, power
text         upper, lower, trim, split, join, replace, starts, ends, length, pad
files        read, write, append, exists, size, list, copy, move, delete
system       cpu, ram, disk, network, processes, env
network      get, post, ping, resolve
date         now, format, diff, parse
json         parse, stringify
```

The `system` module is the bridge between the stdlib and the shell command system. When you write `cpu` in the shell, it eventually calls `system.cpu` under the hood.

---

## Part 5 — Shell commands as functions (v0.6)

Today, shell commands are Python `CommandNode` handlers. Eventually they should be writable in IXX itself.

### 5.1 The `command` keyword

```ixx
command cpu
- info = system cpu
- say "CPU: {info.name}"
- say "Cores: {info.cores}"
- say "Threads: {info.threads}"
- say "Usage: {info.usage}%"
```

```ixx
command ip wifi
- wifi = system.network wifi
- if wifi.connected
-- say "Wi-Fi: {wifi.ip}"
- else
-- say "No connected Wi-Fi adapter found."
```

`command` definitions carry metadata:

```ixx
command delete folder path
- description "Delete a folder"
- destructive YES
- requires_admin NO
- alias "rm folder", "remove folder"
- confirm "Delete {path} and all its contents?"
- filesystem.delete path
```

**Design rule:** `command` definitions go in `.ixx` files (shell command library), not in user scripts. User scripts use `function`. Commands are registered into the `CommandRegistry` at shell startup.

### 5.2 Migration path

```
Today:    CommandNode with Python handler
v0.6:     CommandNode can point to a FuncDef loaded from an .ixx file
v0.7:     Most built-in shell commands migrated to IXX command files
v1.0:     Core command library ships as IXX files, native bridge is the only Python
```

---

## Part 6 — Native/runtime bridge (v0.7)

The native bridge is the layer between IXX and the OS. It is never user-facing.

```
native.windows.cpu_info()       → {name, cores, threads, usage, speed}
native.windows.network_adapters() → list of adapter objects
native.filesystem.list(path)    → list of file objects
native.process.list()           → list of process objects
```

Users never call `native.*` directly. The stdlib and command definitions call them. If a user somehow accesses a native function directly, they get: `native functions are internal — use the system module instead`.

Platform implementations live in [`ixx/shell/platform/`](ixx/shell/platform/). The existing `windows.py`, `linux.py`, `macos.py` structure IS the native bridge. The plan for v0.7 is to expose these as callable functions from within IXX scripts via the `native` namespace (internal/private).

---

## Part 7 — Platform-specific functions

The common interface rule: every function exposed to IXX users has one name. The platform adapter picks the right implementation.

```
system cpu          → works on Windows, Linux, macOS
folder size path    → works everywhere
```

On Windows: uses `Get-CimInstance Win32_Processor`
On Linux: reads `/proc/cpuinfo`, `/proc/stat`
On macOS: uses `sysctl -n`

The user sees none of this. If a platform doesn't support a function: `'cpu temperature' is not available on this system.`

The existing `platform/__init__.py` `current()` selector is already the right architecture. This just extends it.

---

## Part 8 — Remote/server functions (v0.5+)

```
server cer-server
- host "192.168.1.50"
- user "admin"

run on cer-server "disk space"
run on cer-server "cpu"
copy report.pdf to cer-server:/home/admin/
```

The shell's REPL shows the target in the prompt:
```
ixx>                  ← local
ixx cer-server>       ← remote context
```

The function system must be designed so that every command handler can operate in one of three execution contexts: `local`, `remote(server)`, `dry-run`. Context is passed through the call chain, not injected as a global.

This is a v0.5 design concern, v0.6+ implementation concern.

---

## Part 9 — Database functions (v0.6+)

```
connect "postgresql://localhost/inventory"

from assets
- get name, status, location
- where status is "Ready"
- sort by name

in assets
- find id is "LAP-123"
- set status = "Sold"
- save
```

Database writes require safety:
- Always preview affected rows before destructive operations
- Confirm before `delete` or bulk `update`
- Wrap in transactions with rollback on error

These are FUTURE design items. The function system must not prevent them by being too restrictive, but they do not need to be designed in detail for v0.4.

---

## Part 10 — Web/API functions (v0.6+)

```
response = get "https://api.example.com/status"
say response.status
say response.body

post "https://api.example.com/items"
- body = json item
- headers = {"Authorization": "Bearer {token}"}
```

HTTP methods are lowercase to avoid collision with IXX keywords (`delete` as HTTP DELETE will need namespacing: `http delete url`).

---

## Part 11 — Functions vs commands

The distinction IXX will maintain:

| | Function | Command |
|---|---|---|
| Defined with | `function` | `command` |
| Body | dash-block | dash-block |
| Return value | yes | print to screen |
| Help metadata | no (v0.4) | yes |
| Aliases | no | yes |
| Safety flags | no | yes (destructive, admin) |
| Callable from shell | no (v0.4) | yes |
| Callable from scripts | yes | planned (v0.6) |
| Registered in | script scope | CommandRegistry |

In v0.6, the line blurs: `command` definitions can call `function`s, and scripts can call registered commands. But until then, functions are for scripts and commands are for the shell.

---

## Part 12 — Objects/maps/records

Functions become much more useful when they can return structured data. The standard library (`system.cpu`, `network.wifi`) will need to return objects with named fields.

**Planned map/record syntax (v0.5 design, v0.6 implementation):**

```
person = record
- name = "Ixxy"
- age = 19

say person.name
say person.age
```

Or inline:
```
point = record name = "Home", x = 0, y = 0
```

Access: `person.name` — dot notation.
Assignment to field: `person.age = 20`

This is required for the stdlib to return meaningful data from `system.cpu`, `network.wifi`, etc.

---

## Part 13 — Modules/imports (v0.5)

```
use math
use files
use "my-helpers.ixx"

x = math.round 3.7
```

Local function files:
```
use "./helpers.ixx"
helpers.greet "Ixxy"
```

Or import directly into scope:
```
from "./helpers.ixx" use greet, format_name
greet "Ixxy"
```

The module system requires:
- A module loader in [`ixx/interpreter.py`](ixx/interpreter.py)
- A `FunctionTable` that supports namespaced functions (`math.round`)
- Resolution order: local scope → global scope → loaded modules

---

## Part 14 — Error handling (v0.5)

```
try
- content = read file "missing.txt"

if error
- say "Could not read: {error.message}"
- say "File: missing.txt"
```

Or with named error:
```
try
- result = http.get "https://api.example.com"
if error as e
- say "Request failed: {e.message}"
```

The `try` block is a statement that captures runtime errors. The `if error` block only runs if an error occurred. This is minimal and readable.

---

## Part 15 — Closures, lambdas, higher-order functions

Not in v0.4 or v0.5. Not planned for v0.6. These are deferred indefinitely. IXX is not a functional programming language. If the need arises for v1.0, they can be considered. Until then: out of scope.

---

## Part 16 — Async/background functions

Not in v0.4. Needed eventually for:
- Long-running shell commands with progress
- Background update checks (already implemented with Python threads)
- Watching files

`wait` (blocking sleep) is in v0.4 built-ins. True async is v0.6+.

---

## Part 17 — Full staged release plan

### v0.3.8 — Bug fixes (before functions)
- Preprocessor: strip blank lines before Lark Indenter
- Interpolation: warn/error on `{undefined}` in strings
- Loop depth limit (10,000 iterations)
- YES/bool-int guard in comparisons
- Better `else`-indentation error message
- `contains` type mismatch warning

### v0.4.0 — Core user-defined functions
- Grammar: switch to Earley parser, add `func_def`, `call_stmt`, `call_expr`, `return_stmt`
- AST: add `FuncDef`, `CallExpr`, `CallStmt`, `ReturnStmt`
- Interpreter: function table, local scope, return signal, call depth limit
- Built-ins: `count`, `text`, `number`, `ask`, `type`
- Error messages: wrong arg count, unknown function, return-outside-function
- Two-pass script execution (collect function defs first)
- `nothing` value in IXX (null/None)
- Tests: function call, return, scope isolation, recursion, wrong-arg-count errors
- Docs: update language.md, spec/roadmap.md, examples/functions.ixx

### v0.5.0 — Built-ins + stdlib + richer expressions
- Full text/number/list built-in library
- `use module` and `use "file.ixx"` import system
- Map/record objects with dot access
- Function return values usable in more expression contexts
- `try / if error` error handling
- Module: `math`, `text`, `files` (basic)

### v0.6.0 — Commands written in IXX
- `command` keyword with metadata (description, aliases, destructive, requires_admin)
- Commands registered into `CommandRegistry` from `.ixx` files
- Shell command handlers migrated to IXX command definitions where practical
- Remote context object threaded through command calls
- Module: `system`, `network` (IXX-facing wrappers over existing Python platform adapters)

### v0.7.0 — Native bridge / self-hosting
- `native.*` functions exposed to IXX stdlib (not user scripts)
- Majority of shell commands backed by IXX command definitions
- `use system` gives scripts access to system functions
- Platform adapters formalized as native bridge interface

### v0.8.0 — Remote, database, API
- `server` definitions and remote execution context
- `connect database` and basic query/update syntax
- `get`, `post` HTTP functions

### v1.0 — Standalone binary
- Compiled binary (Go or Rust) replacing Python prototype
- Standard library ships as IXX files + native bridge
- Core shell commands ship as `.ixx` command definitions
- Identical user-facing syntax on Windows, Linux, macOS

---

## Part 18 — What NOT to build

Things that will never be in IXX:
- Anonymous functions / lambdas
- Closures
- Decorators
- Type annotations
- Class / object definitions (records cover the use case)
- Generators / iterators
- Exceptions you throw and catch with named types
- Operator overloading
- Macros

IXX stays readable. Every feature must be expressible in plain English without punctuation noise.
