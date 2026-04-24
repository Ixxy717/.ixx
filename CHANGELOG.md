# Changelog

All notable changes to IXX are documented here.

---

## [0.1.0] — 2026-04-23

First stable language prototype. The grammar, interpreter, and CLI are all in place and covered by an automated test suite.

### Language features

- **`say`** — print a value or string to the terminal
- **Variables** — simple assignment with `=`
- **String interpolation** — `"{varname}"` inserts a variable's value into a string
- **Booleans** — `YES` and `NO`
- **Arithmetic** — `+`, `-`, `*`, `/` with standard precedence; unary minus
- **Conditions** — `if` / `else` with full comparison and logic support
- **Loops** — `loop` (while-style, runs as long as condition is true)
- **Lists** — comma-separated literal syntax: `items = "a", "b", "c"`
- **Comparisons** — `is`, `is not`, `less than`, `more than`, `at least`, `at most`, `contains`
- **Logic** — `and`, `or`, `not`
- **Nested blocks** — `--`, `---`, etc. for deeper nesting
- **Comments** — `# this is a comment`

### Dash blocks

Lines starting with `-` belong to the block directly above.  
No indentation rules. No invisible whitespace. No colons.

```
if age less than 18
- say "Not adult"
else
- say "Adult"
```

Two dashes = one level deeper:

```
if user is "Ixxy"
- say "Hello"
- if age at least 18
-- say "Adult account"
- else
-- say "Limited account"
```

### CLI

| Command | What it does |
|---|---|
| `ixx file.ixx` | run a script |
| `ixx run file.ixx` | run a script (explicit) |
| `ixx check file.ixx` | parse and check syntax without running |
| `ixx version` | print the IXX version |
| `ixx help` | show help and quick-reference |
| `ixx shell` | placeholder — interactive shell is planned |

### Error messages

Syntax errors show the source line, a caret at the problem position, and a plain-English explanation.  
Incomplete comparison phrases produce targeted hints:

```
ixx: syntax error in script.ixx line 5

  if age less than
                  ^

Expected a value after "less than".
  Example:  if age less than 18
```

Unknown CLI commands suggest the closest match using fuzzy matching.

### Tests

98 automated tests passing via `python -m unittest discover -s tests -p "test*.py"`.

Coverage: basics, strings, numbers, booleans, conditions, dash blocks, loops, lists, comparisons, `contains`, logic, error handling, CLI commands.

### Project structure

```
ixx/            prototype interpreter (Python + Lark)
  grammar.lark  IXX grammar
  preprocessor  dash-block → indent conversion
  parser        source → AST
  interpreter   AST execution
  __main__      CLI entry point
examples/       hello.ixx, condition.ixx, lists.ixx, advanced.ixx
spec/           language.md, shell.md, roadmap.md
docs/           getting-started.md
tests/          test_ixx.py (98 tests)
CHANGELOG.md    this file
README.md       project overview
OVERVIEW.md     full design overview and rationale
```

### Known limitations

- Requires Python 3.11+ and the `lark` library (prototype dependency)
- No interactive shell or REPL
- No built-in system commands (`cpu`, `ram`, `ip`, etc. — planned)
- No functions, file I/O, or imports
- Variable names must be single words
- Reserved words cannot be used as variable names

---

## Planned — [0.2.0]

To be decided. Leading candidates:

- **v0.2.0-shell-planning** — design the interactive shell architecture in earnest; skeleton REPL with live command guidance
- **v0.2.0-system-commands** — implement first wave of built-in system commands (`cpu`, `ram`, `disk`, `ip`, `wifi`, etc.)
