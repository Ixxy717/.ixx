# Changelog

All notable changes to IXX are documented here.

---

## [0.4.3] — gpu temp, disk health, disk smart, update check

### Added

- **`gpu temp`** — GPU temperature command. Queries `nvidia-smi` for NVIDIA cards; falls back to LibreHardwareMonitor/OpenHardwareMonitor WMI for other vendors. Alias: `gpu temperature`.
- **`disk health`** — Physical disk health status via `Get-PhysicalDisk` (no admin required). Shows health, operational status, media type, and size per drive.
- **`disk smart`** — Basic SMART predictive-failure flag per physical disk (no admin required). Shows SMART status, health, media type, and spindle speed for HDDs.
- **`disk smart full`** — Stub with a clear "requires administrator" message; full attribute table deferred to a future release.
- **Background update check** — On interactive shell startup, a daemon thread checks PyPI once per 24 hours and prints a single update notice below the banner if a newer version is available. Set `IXX_NO_UPDATE_CHECK=1` to opt out entirely.

### Fixed

- `disk health` promoted from admin-only stub to a live no-admin command.
- `get_disk_smart` spindle speed parsing no longer crashes when `SpindleSpeed` returns the string `"Unknown"` instead of an integer.

---

## [0.4.0.2] — GPU VRAM fix

### Fixed

- **GPU VRAM capped at 4 GB** — `Win32_VideoController.AdapterRAM` is a 32-bit field and cannot represent more than 4 GB regardless of actual hardware. `get_gpu_info()` now calls `nvidia-smi --query-gpu=name,memory.total` (bundled with all NVIDIA drivers) and cross-references the result by GPU name. The correct value (e.g. 12 GB for RTX 4070 SUPER) replaces the capped WMI value when available. Non-NVIDIA adapters continue using `AdapterRAM` unchanged.

---

## [0.4.0.1] — CPU temperature fallback

### Fixed

- **`cpu temp` showed "Temperature data not available" on AMD Ryzen and many desktop systems** — Windows does not expose CPU temperatures through ACPI thermal zones on these platforms without a kernel driver. `get_cpu_temperature()` now queries three sources in order: ACPI (`MSAcpi_ThermalZoneTemperature`), OpenHardwareMonitor WMI (`root/OpenHardwareMonitor`), LibreHardwareMonitor WMI (`root/LibreHardwareMonitor`). The first source that returns data wins.
- When no source returns data, the fallback message now explains the AMD Ryzen limitation and links to LibreHardwareMonitor as a free no-install workaround.

---

## [0.4.0] — Release v0.4.0

### Added

**Function system**
- `function name [params]` — define user functions with optional comma-separated parameters
- `return [expr]` — return a value from a function; returns `nothing` if omitted
- Expression-position calls require parentheses: `total = add(5, 3)`
- Statement-position calls use space-style: `greet "World"` / `divider`
- Two-pass collection: functions can be called before they are defined in the file
- Clean local scoping via `FunctionEnvironment` — local writes never leak to global scope
- Call depth limit of 100 with a friendly error (catches Python `RecursionError` too)

**Built-ins (v0.4 set)**
- `count(x)` — length of a list or string
- `text(x)` — convert any value to its text representation
- `number(x)` — convert text/number to number; friendly error on invalid input
- `ask(prompt)` — read a line of user input
- `type(x)` — returns IXX words: `text`, `number`, `yes/no`, `list`, `nothing`

**Terminal color support**
- `NO_COLOR` and `IXX_COLOR=0/1` env-var support
- `show_error()` in red, `show_success()` in green
- Windows Virtual Terminal Processing enabled for both stdout and stderr
- `examples/colors.ixx` — visual color test with PowerShell and CMD instructions

**Demo improvements**
- `ixx demo interactive` — step-by-step guided walkthrough with live code execution
- `try-it.ixx` rewritten to demonstrate v0.4 language features

**New examples**
- `examples/functions.ixx` — function basics, parameters, return, recursion, built-ins
- `examples/colors.ixx` — terminal color env-var test
- `examples/FunctionStressReal.ixx` — comprehensive function stress test

**Documentation**
- `spec/language.md` — full Functions section, built-ins table, updated reserved words
- `spec/roadmap.md` — v0.4 marked complete; v0.5–v0.7 sections written and deferred

### Fixed

- **UTF-8 BOM** (`\ufeff`) at start of `.ixx` files now stripped in preprocessor
- **Keyword-prefix identifier bug** — function names like `return_list`, `is_valid`, `not_empty`, `contains_check` previously caused a lexer error; all 11 priority keyword terminals now carry negative lookahead `(?![A-Za-z0-9_])`
- Preprocessor strips blank lines to prevent spurious `_DEDENT` tokens in blocks
- Loop iteration limit of 10,000 with friendly error
- `YES`/`NO` blocked from arithmetic and relational comparisons
- Undefined string interpolation → `{?name}` with stderr warning
- `contains` type-mismatch warns on stderr

### Packaging

- `pyproject.toml`: excluded root `assets/` dev scripts and `tests/` from wheel
- Wheel contents: only `ixx/` package files + `ixx/assets/` runtime data
- 400 tests passing, 29 skipped (v0.5 placeholders)

---

## [0.3.0] — v0.3.0-system-commands

First real-usefulness release. Shell commands now actually work on Windows.

### Added

**New live command entries (this pass adds to the original 14):**
- `cpu info` — full CPU summary (name, cores, threads, speed, usage)
- `cpu speed` — CPU clock speed in GHz
- `cpu temperature` — ACPI thermal zone temperatures; graceful "not available" if hardware doesn't expose them
- `ram free` — free RAM
- `ram usage` — used RAM with percentage
- `ram speed` — RAM speed in MHz
- `gpu` — GPU name, VRAM, and driver version
- `gpu vram` — VRAM only
- `gpu driver` — driver version only
- `wifi` — standalone Wi-Fi: SSID, signal, IP
- `ip public` — public-facing IP via external lookup (api.ipify.org); offline-safe
- `ports` — listening TCP ports with owning process names
- `processes` — top 30 running processes by RAM
- `disk partitions` — partition table
- `find file <pattern> [in <path>]` — recursive file search with path alias support

**Shell improvements:**
- **Branded startup banner** — Unicode box banner with "The language for the user." slogan; ASCII fallback for terminals that can't render box characters; not shown for `ixx do`
- **`command ?` / `help command` / `command help`** — all three help forms supported
- **Unknown subcommand guard** — `cpu temp` now shows "Unknown option for 'cpu': temp / Did you mean: cpu temperature?" instead of silently running the `cpu` handler
- **Prefix matching** — abbreviations like `temp` match `temperature` even when difflib cutoff doesn't
- **Case-insensitive commands** — `CPU`, `Ip`, `DISK` all work

**Platform adapter:**
- `windows.py` now has: `get_cpu_speed`, `get_cpu_temperature`, `get_ram_speed`, `get_gpu_info`, `get_wifi_info`, `get_public_ip`, `get_ports`, `get_processes`, `get_disk_partitions`
- `linux.py` and `macos.py` updated with `_not_yet()` stubs for all new functions

**Original 14 live entries from earlier in v0.3.0:**
- `ip`, `ip all`, `ip wifi`, `ip ethernet`, `ip local`, `network`
- `cpu`, `cpu core-count`
- `ram`, `disk`, `disk space`
- `folder size`, `open`, `list`

**Infrastructure:**
- `shell/platform/` — cross-platform adapter layer
- `shell/paths.py` — path alias system
- `shell/safety.py` — `format_bytes()` and `render_table()`
- `ixx do "command"` — single-dispatch CLI mode

### Fixed

- 172.16.x.x–172.31.x.x (RFC 1918 range) no longer mis-classified as "virtual" adapters
- Subprocess test encoding fixed for Unicode banner output
- `gpu` moved from stub to live

### Still stubbed (deferred, all planned)

- `disk health` — requires admin SMART access
- `kill process`, `copy`, `move`, `delete` — destructive; safety flow not designed yet
- `native` — shell passthrough
- `ssh`, `server`, `servers` — remote access feature category

### Tests

- **`tests/test_v030.py`** — 46 new tests added this pass: `TestBannerOutput`, `TestNewHardwareCommands`, `TestNewNetworkCommands`, `TestNewSystemCommands`, `TestFindFile`, `TestUnknownSubcommand`, `TestCaseInsensitive`, `TestNetworkClassification`
- **Total: 282 tests passing**

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
