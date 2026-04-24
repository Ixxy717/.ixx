---
name: IXX v0.1.0 polish
overview: "A stability and polish pass: better error messages, automated tests for all current language features, an updated README, an Examples section in help, and verification that all examples still run. No new language features."
todos:
  - id: help-errors
    content: Add Examples section to HELP_TEXT and improve error formatting in __main__.py
    status: completed
  - id: interp-tip
    content: Add Tip line to undefined-variable error in interpreter.py
    status: completed
  - id: readme
    content: Create README.md with identity, examples, CLI table, limitations, prototype note
    status: completed
  - id: docs-update
    content: Update docs/getting-started.md with limitations and prototype note
    status: completed
  - id: tests
    content: Create tests/test_ixx.py with all 35+ test cases
    status: completed
isProject: false
---

# IXX v0.1.0 Polish Plan

## 1. Help text — add Examples section

In [`ixx/__main__.py`](ixx/__main__.py), append to `HELP_TEXT`:

```
Examples:
  ixx examples\hello.ixx
  ixx run examples\condition.ixx
  ixx check examples\advanced.ixx
  ixx version
  ixx help
```

## 2. README.md at project root

Create [`README.md`](README.md) covering:
- One-line identity ("IXX is executable checklist-style code")
- Hello world
- Condition example
- List / contains example
- CLI command table
- Current limitations (Python 3.11+ required, no REPL, no built-in system commands)
- Prototype note: Python is prototype v0 only, not the long-term identity

`docs/getting-started.md` gets a small update: add a **Current limitations** section and a **Note on this implementation** paragraph at the bottom.

## 3. Automated tests

Single test file: [`tests/test_ixx.py`](tests/test_ixx.py) using `unittest` (no extra dependencies).

Tests capture `stdout` with `io.StringIO` + `contextlib.redirect_stdout`. CLI commands tested via `subprocess`.

Coverage:

| Category | What is tested |
|---|---|
| Basics | hello world, `say`, variables, assignment |
| Strings | plain strings, string `+` concat, `{interp}` |
| Numbers | integers, floats, negative numbers, math `+ - * /` |
| Booleans | `YES`, `NO`, truthiness |
| Conditions | `if` alone, `if/else`, condition false, condition true |
| Dash blocks | single `-`, double `--` nesting |
| Loop | basic loop, loop that runs zero times |
| Lists | list literal, `say` a list, list display |
| Comparisons | `is`, `is not`, `less than`, `more than`, `at least`, `at most` |
| Contains | `contains` on list (true), `contains` on list (false), `contains` on string |
| Logic | `and`, `or`, `not` |
| Errors | undefined variable raises `IXXRuntimeError`, division by zero |
| CLI | `ixx version` output, `ixx help` output, `ixx check` on valid file, `ixx check` on bad file exits non-zero |

## 4. Friendlier error messages

### Syntax errors — [`ixx/__main__.py`](ixx/__main__.py)

Currently dumps `str(e)` which contains raw Lark parser state.

Replace with `e.get_context(source)`, which Lark already provides — it returns the relevant source line with a caret:

```
ixx: syntax error in examples\bad.ixx (line 4)

  if age less
            ^
Unexpected token. Check the syntax around this point.
```

Implementation in `_run_file`:

```python
except UnexpectedInput as e:
    loc = f"line {getattr(e, 'line', '?')}"
    print(f"ixx: syntax error in {path} ({loc})\n", file=sys.stderr)
    # get_context formats the source line + caret for us
    ctx = e.get_context(source).rstrip()
    print(ctx, file=sys.stderr)
    print("\nCheck the syntax around the marked position.", file=sys.stderr)
    sys.exit(1)
```

### Runtime errors — [`ixx/__main__.py`](ixx/__main__.py) + [`ixx/interpreter.py`](ixx/interpreter.py)

Add the filename to runtime error output:

```python
except IXXRuntimeError as e:
    print(f"ixx: runtime error in {path}", file=sys.stderr)
    print(f"  {e}", file=sys.stderr)
    sys.exit(1)
```

Add a tip for the most common runtime error — undefined variable — already in `interpreter.py`:

```
I don't know what 'name' is. Did you set it yet?
Tip: name = "your value"
```

The tip line is appended inside `Environment.get()` when raising, making the message self-contained regardless of how the error is caught.

### Bad command — [`ixx/__main__.py`](ixx/__main__.py)

When the user types an unknown command, suggest `ixx help` more clearly:

```
ixx: unknown command 'cpoy'
     Did you mean: copy?  Run 'ixx help' for available commands.
```

For now, a simple close-match suggestion using Python's `difflib.get_close_matches` against the known command list (`run`, `check`, `version`, `help`, `shell`).

## 5. Verify all examples run

Covered by tests and by a final manual check in implementation. No code change needed unless a bug is found.

## File changes summary

| File | Change |
|---|---|
| `ixx/__main__.py` | add Examples to HELP_TEXT, better syntax error format, better runtime error format, fuzzy suggestion for unknown commands |
| `ixx/interpreter.py` | add Tip line to undefined-variable error |
| `README.md` | create (new file) |
| `docs/getting-started.md` | add limitations + prototype note |
| `tests/test_ixx.py` | create (new file), ~35 test cases |
