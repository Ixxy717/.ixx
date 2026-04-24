# Changelog

All notable changes to IXX are documented here.

---

## [0.3.0-dev] — in progress (branch: v0.3.0-system-commands)

First real-usefulness release. Shell commands now actually work on Windows.

### Added

- **14 live command entries** — real implementations replacing stubs:
  `ip`, `ip all`, `ip wifi`, `ip ethernet`, `ip local`, `network`,
  `cpu`, `cpu core-count`, `ram`, `disk`, `disk space`,
  `folder size`, `open`, `list`
- **`shell/platform/`** — cross-platform adapter layer (`windows.py` real,
  `linux.py` / `macos.py` stubs for later)
- **`shell/paths.py`** — path alias system (`desktop`, `downloads`, `documents`,
  `pictures`, `music`, `videos`, `home`, `temp`, `appdata`, `here`, `.`)
- **`shell/safety.py`** — `format_bytes()` helper and `render_table()` renderer
- **`shell/commands/hardware.py`** — `cpu`, `ram` handlers
- **`shell/commands/network.py`** — `ip`, `network` handlers
- **`shell/commands/system.py`** — `disk` handlers
- **`shell/commands/files.py`** — `folder size`, `open`, `list` handlers
- **`ixx do "command"`** — run one shell command and exit (`ixx do "ip wifi"`)
- **`executable_with_children`** field on `CommandNode` — parent commands
  (`ip`, `cpu`, `ram`, `disk`, `network`) now execute standalone AND keep
  subcommands available
- **SSH/server stubs** — `ssh`, `servers`, `server add`, `server list` registered
  in the command tree; stub-only, no credentials or remote execution

### Changed

- `VERSION` bumped to `0.3.0-dev`
- Stub messages updated from "coming in v0.3.0" to "planned for a future release"
- `show_not_implemented()` accepts an optional `note` argument
- `repl.py` gains `run_command_once()` for single-dispatch use
- Windows console now configured for UTF-8 output on shell start

### Tests

- **`tests/test_v030.py`** — 66 new tests covering path aliases, format helpers,
  guidance model, command handlers (mocked platform), and `ixx do`
- **Total: 218 tests passing** (98 language + 54 shell + 66 v0.3.0)

---

---

## [0.2.0-dev] — in progress (branch: v0.2.0-shell-planning)

Interactive shell skeleton. The REPL is live and the guidance engine is
fully working. No real OS commands yet — those come in v0.3.0.

### Added

- **`ixx shell`** — opens the IXX interactive shell (was a placeholder; now a real REPL)
- **`ixx`** (no arguments) — also opens the shell, per spec
- **`shell/registry.py`** — `CommandNode` dataclass and `CommandRegistry`; the entire command grammar lives here as pure data, with no hardcoded string matching
- **`shell/guidance.py`** — `get_guidance()` engine; walks the command tree and returns valid next options, executability, examples, and safety flags
- **`shell/renderer.py`** — all REPL output formatting: hints, help, warnings, fuzzy-correction messages
- **`shell/repl.py`** — main interactive loop with tokenizer, dispatch, `help` / `?` support, fuzzy correction, and clean Ctrl-C / Ctrl-D / EOF exit
- **`shell/commands/stubs.py`** — 18 commands seeded with full metadata and stub handlers: `cpu`, `ram`, `gpu`, `disk`, `network`, `ip`, `wifi`, `ports`, `processes`, `kill`, `folder`, `find`, `open`, `list`, `copy`, `move`, `delete`, `native`

### Tests

- **`tests/test_shell.py`** — 54 new tests covering registry, guidance engine, tokenizer, fuzzy correction, stub handlers, and full-registry smoke tests
- **Total: 152 tests passing** (98 language + 54 shell)

### Shell behavior

Typing an incomplete command shows guidance:
```
ixx> delete
  file        Delete a single file
  folder      Delete a folder [recursive] [force] [dry-run]
  temp        Clean temporary files
  empty-trash Empty the recycle bin / trash
```

Typing a complete command runs the stub:
```
ixx> cpu usage
  [cpu usage  -  not yet implemented, coming in v0.3.0]
```

Typing something wrong fuzzy-corrects:
```
ixx> cpoy
  Unknown command: cpoy
  Did you mean: copy  |  cpu?
```

### Known limitations

- All system commands are stubs (no real OS integration yet)
- No inline autocomplete while typing (keystroke-level guidance is v0.3.0)
- No `ixx do "command"` yet

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
