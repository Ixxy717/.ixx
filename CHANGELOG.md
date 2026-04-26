# Changelog

All notable changes to IXX are documented here.

---

## [0.6.8] — 2026-04-26: Deep Audit Fixes (Letters A–V + Final Docs Batch)

### Crash hardening / raw-exception elimination

- **Write/append to missing folder** — `write` and `append` now catch `OSError` and raise a friendly `IXXRuntimeError` instead of leaking a Python traceback.
- **`open` shell command** — `subprocess.run` in non-Windows path now catches `FileNotFoundError` gracefully.
- **Network adapter classifier** — `int(parts[1])` in `_classify_adapter` is now guarded against `ValueError`.
- **Catch block `error` variable** — `OSError` and `UnicodeDecodeError` now produce readable human messages; Python exception class names no longer appear in `error`.
- **Unknown statement/expression/operator fallbacks** — Python class names (`Unknown statement type: Assign`) replaced with calm human messages ("This statement cannot be run here.").

### Display consistency / vocabulary cleanup

- **`ixx_err_type()`** — a new display helper returns `"a yes-or-no value (YES/NO)"` for booleans in error messages; `ixx_type_name()` still returns `"bool"` for `type()` compatibility.
- **All user-facing error messages** — type names in 17 built-in error messages updated to use `ixx_err_type` instead of raw Python class names.
- **Import error messages** — `"Import file not found"` → `"Couldn't find '…'. Check that the file exists."` and similar plain-English rewrites.
- **Circular import message** — `"Circular import detected: chain"` → `"These files load each other in a loop, which causes a problem: chain"`.
- **`ixx check` success** — output changed from `"syntax OK"` to `"check passed"`.
- **Stub commands** — `"not yet implemented, planned for a future release"` → `"not available yet, coming in a future release"`.
- **Comparison chaining hint** — `if a less than b less than c` now raises `"Comparisons cannot be chained. Use 'and': if a less than b and b less than c"` instead of a confusing type error.
- **YES/NO comparison wording** — `"Use 'is' or 'is not' to compare booleans."` → `"Use 'is' or 'is not' to compare yes-or-no values (YES / NO)."`.
- **Help text** — OVERVIEW examples use forward slashes, admin note no longer mentions `run as admin via native`.

### String escapes (Letter C)

- `\n`, `\t`, `\\` are now processed inside all IXX string literals. Previously they were literal characters.
- Unknown `\x` sequences pass through as-is (e.g. `\q` → `\q`).
- Windows paths work as `"C:\\Temp\\file.txt"` or `"C:/Temp/file.txt"`.

### REPL imports and persistence (Letters D, U)

- `use "file.ixx"` now works inside the interactive shell.
- **REPL state persistence** — variables and functions survive across input lines in the same session. A single `Interpreter` instance is reused per session via `run_repl_input()`.
- **IXX call-statement recognition** — `write`, `read`, `readlines`, `append`, `exists`, `do`, `ask`, `color` added to `_IXX_STARTERS` so they are correctly parsed as IXX rather than misrouted as unknown shell commands.
- **Blank continuation line errors** — errors inside multi-line inputs are now surfaced as friendly messages instead of being silently swallowed.
- **Quoted path casing** — `_normalize` now preserves casing of quoted path tokens on case-sensitive systems.
- **readline history** — `~/.ixx_history` is loaded on startup and saved on exit via `atexit`.

### Checker scoping and line accuracy (Letters E, V)

- **`error` variable scope** — the checker no longer incorrectly flags `error` as undefined when used outside catch; it now only considers it defined inside a catch body.
- **Top-level `return` is a static error** — `return` outside a function now correctly produces an error diagnostic.
- **`StrLit` line metadata** — `StrLit` AST nodes now carry a `line` attribute from the Lark token, enabling accurate interpolation-warning line numbers.
- **`read`/`readlines` path resolution** — static path checks in the checker now resolve relative paths from the script's directory rather than CWD.
- **Checker line number correction** — `preprocess_with_map()` returns a line map; `_apply_line_map()` translates preprocessed line numbers back to original source lines in both human and `--json` output.

### Float display and finite-number validation (Letter O)

- Numbers display without trailing `.0` — `10 / 2` → `5` not `5.0`.
- No excess IEEE 754 precision — `0.1 + 0.2` → `0.3`.
- `number("inf")` and `number("nan")` now raise a runtime error — these are not valid IXX numbers.

### Keyword interpolation (Letter P)

- `{YES}`, `{NO}`, and `{nothing}` inside string literals now substitute their display value directly, without triggering an "undefined variable" warning.

### Return list literals (Letter Q)

- Functions can return multiple comma-separated values directly: `return 1, 2, 3` produces a list.
- Grammar, AST transformer, and checker all updated. Existing single-value and bare returns are unchanged.
- Top-level `return 1, 2, 3` (outside a function) is a static checker error.

### Checker warnings (Letter T)

- **Builtin shadowing** — assigning to a top-level variable whose name matches a built-in (`count`, `text`, `type`, etc.) now produces a checker warning with a rename suggestion.

### StressTest coverage expansion (Letters H, I, N, O, P, Q, T, V)

- 83 positive test files, 50 expected-failure files, 34 CheckJson tests in the normal suite.
- Hard suite: 104 total pass.
- Scenario suite: 20 scenario pass, 144 assert pass.

### Documentation overhaul (Final Docs Batch — Letters F, R, S, T docs, + collected notes)

- **`docs/getting-started.md`** — full rewrite covering all current language features, REPL, imports, file I/O, escape sequences, Windows paths, multi-value say, bare conditions, and StressTest suites.
- **`README.md`** — removed stale "no escape sequences" limitation; updated test section with all three StressTest suites; removed hardcoded test counts.
- **`spec/language.md`** — new sections: Imports/use, Number display, ixx check (JSON/warnings/builtin-shadow/no-multiline), REPL persistence, `{YES}/{NO}/{nothing}` interpolation, multi-value say, return list literals, file I/O path behavior note.
- **`spec/dictionary.md`** — new entries: keyword interpolation, return list literal, builtin shadowing, clean float display, `number()` inf/nan rejection, `ask()` EOF behavior, file I/O path resolution, imports section, REPL section, `ixx check --json` entry.
- **`IXX_ROADMAP_0.6.6_to_0.7.md`** — corrected version label collision: v0.6.7 and v0.6.8 relabeled to their actual content; future features renumbered.
- **`OVERVIEW.md`** — removed stale `0.3.0-dev` shell version string; updated version history; updated language evolution section.
- **`spec/shell.md`** — removed stale `v0.3.0` section labels and SSH roadmap version numbers.
- **`ixx/preprocessor.py`** — updated docstring: known-limitation note now documents the solution (`preprocess_with_map` + `_apply_line_map`).

---

## [0.6.7] — 2026-04-25: Bug & Edge Case Audit

### Fixed

- **`color()` with bool value** — `color("red", YES)` now renders `"YES"` instead of Python `"True"`. The `display()` helper from `values.py` is now used instead of `str()`.
- **`_eval_binop` unhandled `TypeError`** — operations like `list - 1`, `nothing + 1` now raise a friendly `IXXRuntimeError` instead of a raw Python traceback. The `-`, `*`, `/`, and `+` (non-string) branches are all wrapped.
- **`"text" + nothing` silent coercion** — `"hello" + nothing` previously produced `"hellonothing"`. It now raises `IXXRuntimeError: Cannot concatenate text with nothing.`
- **`_eval_compare` unhandled `TypeError`** — `"abc" more than 1` now raises a friendly `IXXRuntimeError` and is catchable by `try/catch`. Previously it leaked a raw Python `TypeError` traceback.
- **`try/catch` misses `UnicodeDecodeError`** — reading a binary file inside `try/catch` now correctly catches the error. `UnicodeDecodeError` was added to the caught-exceptions tuple.
- **`ask()` EOFError on piped stdin** — `ask()` on closed/piped stdin now raises a friendly `IXXRuntimeError("No input available (stdin is closed).")` instead of crashing.
- **Checker: `LoopEach` missing from `_collect_written_paths`** — a `write()` call inside `loop each` now correctly registers the path, preventing a false "File not found" error for a subsequent top-level `read()`.
- **Checker: dead `_has_catch` field removed** — `self._has_catch` was assigned but never read; the field and both assignments are removed.
- **REPL IXX-detection heuristic** — `function`, `try`, `use`, `return`, `catch` added to the set of keywords that trigger IXX syntax-error reporting in the REPL instead of "unknown command".

### Added

- **Checker: interpolation expression warning** — string literals containing `{expr(...)}` or `{a + b}` patterns (expressions that cannot be interpolated) now produce a `"warning"` severity `CheckError`. `ok: true` is preserved in `--json` output — only hard errors cause `ok: false`. A `_warn()` helper was added to `SemanticChecker`.
- **LoopEach scoping comment** — an explanatory comment in `interpreter.py` documents the `iter_env.set()` parent-chain walk that implements the "predeclared variable survives / new variable does not leak" scoping rule.
- **StressTest positive tests** — `69-edge-arith.ixx`, `70-edge-compare.ixx`, `71-edge-builtins-type-coerce.ixx`, `72-edge-list-ops.ixx`, `73-edge-try-catch-coverage.ixx`.
- **StressTest ExpectedFailures** — `bad-arith-list-minus.ixx`, `bad-arith-nothing-plus.ixx`, `bad-arith-text-plus-nothing.ixx`, `bad-compare-text-number.ixx`, `bad-min-mixed.ixx`.
- **Unit tests** — `TestEdgeCases` class in `tests/test_ixx.py` (30+ tests covering all fixed bugs, edge cases, and documented behaviours).
- **Docs** — `spec/language.md` updated with: `\n` is literal, expression interpolation warning, bool-in-string-concat requires `text()`, `call_stmt` parentheses trap, and list round-trip via `join`/`split`.
- **StressTest/RealWorld/** — 53 real-world scenario and torture test files; 52 pass, 1 intentional bug probe (`53-bug-compare-mismatch.ixx`, now fixed).

### Notes

- `min`/`max` mixed-type `TypeError` was previously listed as a bug; confirmed it was already wrapped by `_call()` in the interpreter. No change needed.
- `StressTest/RealWorld/53-bug-compare-mismatch.ixx` (the one previously failing intentionally) now passes after the `_eval_compare` TypeError fix.

---

## [0.6.6.1] — 2026-04-25: REPL Empty-Enter Fix

### Fixed
- Pressing Enter on an empty line in the IXX terminal no longer dumps the full help menu. It now behaves like PowerShell and CMD — the prompt simply advances to the next line.

---

## [0.6.6] — 2026-04-25: IXX-native List Iteration

### Added
- **`loop each` construct** — `loop each <name> in <expr>` iterates over every item in a list.
- **`LoopEach` AST node** — `var_name: str`, `iterable: Expr`, `body: list[Stmt]`, `line: int | None`.
- **Grammar** — `loop_each` rule alongside `loop_while`; new `_EACH_KW` and `_IN_KW` terminals at priority 2 with negative lookaheads to avoid clashing with identifiers like `each_item`, `inside`, `input`.
- **Transformer** — renamed existing `loop_stmt` method to `loop_while`; added `loop_each` method in `build_ast.py`.
- **Interpreter** — `LoopEach` case in `_exec`: evaluates the iterable once, raises a friendly `IXXRuntimeError` if it is not a list, then runs the body once per item.
- **Checker** — `loop each` is understood by `SemanticChecker`.  Conservative literal validation flags obvious non-list literals (`"text"`, numbers) at the top level only (not inside functions, try/catch, or other control-flow blocks).  Loop-variable scoping matches runtime: defined inside the body for all iterations; survives after the loop only if it was declared before the loop.
- **Examples** — `examples/loop-each.ixx` demonstrates names, sums, text building, nested loops, early return from inside a loop, and try/catch inside a loop.
- **StressTest positive tests** — `59-loop-each-basic.ixx`, `60-loop-each-nested.ixx`, `61-loop-each-in-function.ixx`, `62-loop-each-try-catch.ixx`, `63-loop-each-mixed.ixx`.
- **StressTest ExpectedFailures** — `bad-loop-each-text.ixx`, `bad-loop-each-number.ixx`, `bad-loop-each-undefined-list.ixx`.
- **StressTest CheckJson** — `good-loop-each.ixx`, `bad-loop-each-text-literal.ixx`, `bad-loop-each-number-literal.ixx`.
- **Unit tests** — `TestLoopEach` class in `tests/test_ixx.py` (18 tests covering parse, AST, interpreter, scoping, runtime errors, checker, and JSON).
- **Docs** — `spec/language.md` and `spec/dictionary.md` updated with `loop each` syntax, scoping rules, and examples.  Keywords list extended with `each` and `in`.

### Notes
- Existing while-style `loop <condition>` behavior is unchanged.
- `loop each` does **not** add indexing, maps, filters, or dictionaries — those are future scope.
- No new built-ins were added; iterating over a non-list still raises a descriptive runtime error.

---

## [0.6.5] — 2026-04-25: Local Module Imports and Standard Library

### Added
- **Local module imports** — `use "path/to/file.ixx"` loads function definitions from another IXX file, resolved relative to the importing file's directory.
- **Standard library imports** — `use std "time"` and `use std "date"` load built-in IXX helper modules from `ixx/stdlib/`.
- **Standard library foundation** — `ixx/stdlib/time.ixx` provides `time_greeting`, `minutes_to_hours`, `seconds_to_minutes`; `ixx/stdlib/date.ixx` provides `is_leap_year`, `days_in_february`, `is_valid_month`. All pure IXX — no new built-ins required.
- **Import resolver** (`ixx/modules.py`) — handles file loading, recursive/transitive imports, cycle detection, and duplicate function name detection. Only `function` definitions are collected from imports; top-level statements in imported files never execute.
- **`UseStmt` AST node** — `kind: "file" | "std"`, `path: str`, `line: int | None`.
- **Grammar** — `use_stmt` rule with `_USE_KW` and `_STD_KW` terminals at priority 2.
- **`IXXImportError`** — raised on missing file, circular import, or duplicate function name (with line info where available).
- **Interpreter** — `run(program, extra_funcs)` accepts a dict of pre-resolved imported functions; duplicate local/imported names raise `IXXRuntimeError`.
- **Checker** — `check(program, file, imported_funcs)` validates imported function arity and detects local/imported name collisions; `UseStmt` nodes are silently skipped.
- **CLI** — `ixx run` and `ixx check` (both human-readable and `--json`) resolve imports before execution/checking; import errors are reported consistently in both modes.
- **StressTest** — 6 new positive tests (41–46), 5 new expected-failure files, 5 new `CheckJson` cases. Final counts: FILE PASS 46, JSON PASS 16, EXPECTED FAIL PASS 21.
- **Unit tests** — `TestImports` class with 19 tests covering grammar, resolver, interpreter, stdlib, and checker.

---

## [0.6.4.2] — Fix: literal diagnostics no longer fire inside blocks

### Fixed
- `ixx check` literal built-in validation is now strictly top-level only.
  Checks are suppressed inside function bodies, if/else blocks, loop bodies,
  try blocks, and catch blocks — fixing false positives on all 40 positive
  StressTest files (every test uses `number("ASSERT_FAIL")` inside a helper
  function that only runs on assertion failure).
- `read()` / `readlines()` literal path checks are also suppressed when any
  `write()` or `append()` to the same literal path appears anywhere in the
  program (the file may be created at runtime before the read).
- JSON literal diagnostics continue to work correctly for all ExpectedFailures
  files (`bad-color-name`, `bad-file-read`, `bad-number-conversion`,
  `bad-do-empty`, `bad-do-nontext`).

---

## [0.6.4.1] — Enhanced `ixx check` literal diagnostics for built-ins

### Added
- **`ixx check` now catches obvious built-in misuse statically** when arguments are literals:
  - `color("purple", ...)` → unknown color name flagged (valid: bold, cyan, dim, green, red, yellow)
  - `read("missing.txt")` / `readlines("missing.txt")` → non-existent literal file path flagged
  - `first("abc")`, `last(123)`, `sort("abc")`, `reverse(123)` → scalar literals flagged (must be list)
  - `count(42)` → number/bool/nothing literal flagged (must be list or text)
  - `number("abc")` → un-convertible string literal flagged
  - `do("")` → empty command flagged; `do(42)` → non-text literal flagged
- All checks are conservative — only fire on literal arguments, never on variables or expressions.
- The VS Code/Cursor extension automatically benefits (already consumes `ixx check --json`).
- 28 new unit tests for literal validation across all checked built-ins.

---

## [0.6.4.0] — `do()` built-in: script-to-shell command bridge

### Added
- **`do(command)` built-in** — run any IXX shell command from inside an `.ixx` script and get the output back as text:
  ```
  ram = do("ram used")
  say ram

  ip = do("wifi ip")
  say "Wi-Fi IP: {ip}"

  cpu = do("cpu info")
  write "cpu-report.txt", cpu
  ```
- `do()` raises `IXXRuntimeError` on unknown commands, incomplete commands, not-yet-implemented commands, or commands that fail at runtime — so `try`/`catch` works:
  ```
  try
  - info = do("bad command")
  catch
  - say "Command failed: {error}"
  ```
- `do()` added to `_BUILTIN_ARITY` in `checker.py` — `ixx check` flags wrong-arity calls statically
- `do` added to VS Code extension syntax-highlighting keyword list; VSIX rebuilt (`0.6.0`)
- `do(command)` documented in `spec/dictionary.md` (Shell bridge section)
- `ixx/runtime/builtins/shell.py` — new module for shell-bridge built-ins

### Technical
- `run_command_capture(line)` added to `ixx/shell/repl.py`: runs the same tokenize → normalize → alias → guidance → dispatch pipeline as `run_command_once`, but captures handler `print()` output via `contextlib.redirect_stdout` and returns it as a string
- No handler files modified; all existing `ixx do "..."` CLI behavior unchanged

---

## [0.6.3.0] — interpreter refactored into `ixx/runtime/` package

### Changed
- **`ixx/interpreter.py`** slimmed from 755 lines to ~250 lines — now contains only `_ReturnSignal`, `Interpreter`, and the four runtime import lines
- **`ixx/runtime/`** package extracted from the interpreter:
  - `errors.py` — `IXXRuntimeError`
  - `values.py` — `ixx_type_name`, `display`, `truthy`
  - `environment.py` — `Environment`, `FunctionEnvironment`
  - `builtins/core.py` — `count`, `text`, `number`, `type`, `ask`
  - `builtins/text.py` — `upper`, `lower`, `trim`, `replace`, `split`, `join`
  - `builtins/math.py` — `round`, `abs`, `min`, `max`
  - `builtins/lists.py` — `first`, `last`, `sort`, `reverse`
  - `builtins/files.py` — `read`, `readlines`, `write`, `append`, `exists`
  - `builtins/color.py` — `color`
  - `builtins/__init__.py` — `BUILT_INS` combined registry
- **Zero behavior change** — all 507 tests pass, StressTest FILE/ASSERT/EXPECTED FAIL: 0
- **Backward-compatible** — `IXXRuntimeError` re-exported from `interpreter.py`; no external import sites changed

---

## [0.6.2.7] — showoff: dot-loading boot, yellow headers, dim purpose tags, native note polish

### Changed
- **Boot sequence** — status lines now animate as `runtime   .  ..  ...   ready`:
  - Label types out at 0.015s/char
  - Each dot group (`.`, `..`, `...`) types in yellow with 0.48s pause between groups
  - `ready` types in green after the dots — the yellow-to-green transition feels like a real init sequence
- **Section headers** (`_hr()`) — changed from bold white to **bold yellow**; creates a clear visual layer: yellow = structure, cyan = IXX content, green = output, dim = old/labels
- **Purpose tags** in comparisons — changed from plain white to **dim text**; reads as a subtitle, not competing with the code
- **`_section_native_note`** — `KNOWN COMMAND:` now dim (old-way treatment), `PLANNED:` now bold+cyan (IXX-way treatment), matching the visual language of the comparison blocks

### Fixed
- Removed unused `uni`/`hdr` variables left over in `_section_boot`
- Added blank line between purpose tag and `OLD WAY:` label for breathing room

---

## [0.6.2.6] — showoff: new boot/final/slogan text, purpose tags, [enter] on comparisons

### Changed
- **Boot section** completely rewritten: was `> booting IXX...` loading messages + taglines; now shows `══ IXX SHOWOFF ══` header followed by animated status readouts (`runtime  ready`, `syntax  ready`, `shell  ready`, `examples  ready`) in green, then `IXX {version}` + `"Readable scripting for real terminal work."`
- **Slogan block** (full mode): was "No braces. No semicolons..." — now `"Readable when you write it."` / `"Readable when you come back later."` / `"Useful from the first command."`
- **Native commands intro**: was "IXX does not replace what you already know. / It gives you a home base." — now `"IXX is not trying to hide the system."` / `"It gives common work a cleaner front door."`
- **Final screen**: removed "The computer, translated." and slogan list; now `IXX` / `The language for the user.` / `Readable scripts.` / `Practical commands.` / `Built to stay understandable.` / `pip install ixx`

### Added
- **Purpose tag** above each OLD WAY block: one short line (≤10 words) describing the goal of the comparison, e.g. `"Get your wifi IP address."`, `"Read a text file into a variable."`
- **`[enter]` prompt after every comparison block** (`_comparison()`) — same treatment as code blocks; no-op when piped/quick/plain

### Fixed
- Removed orphaned dead-code block that had somehow been placed after `if __name__ == "__main__":` in `tests/test_ixx.py`
- `_code_reveal` loop body was missing its `for` statement after the `CODE` label edit — restored

---

## [0.6.2.5] — showoff: native/timeline animated, press-enter pacing, slower code

### Fixed
- **`_section_native_note`** was using bare `print()` on every line — now uses `type_line()` at 0.020s/char with 0.22s inter-line pause; no longer pops in
- **`_section_timeline`** milestone lines were bare `print()` — now types the description char-by-char (0.018s/char) after printing the colored version tag
- **Code typing delay** in `_code_reveal` increased 0.022 → 0.030s/char so code is actually readable during the reveal
- **`_section_real_script`** code delay increased 0.016 → 0.028s/char for same reason

### Added
- **`_wait()` — lightweight press-enter prompt** after each code block in `default` and `full` modes: a dim `[enter]` appears at the left margin; pressing enter erases it and continues. Completely silent (no-op) when piped, in `plain` mode, or in `quick` mode — tests unaffected

---

## [0.6.2.4] — showoff: all animations now consistent, less color fatigue

### Fixed
- **`ixx showoff` outputs no longer jump in instantly** — OUTPUT lines in both `_code_reveal` and `_comparison` now type out character by character (green, 0.015–0.016s/char)
- **Horizontal dividers no longer slam in** — `_divider()` now draws character by character at 0.003s/char (fast scribble feel, ~0.19s total)
- **"All blue code" resolved** — `_code_reveal` code lines changed from cyan to the terminal's default text color; cyan is now reserved only for IXX WAY comparison lines where the contrast with dim OLD WAY matters
- **`_section_real_script` inline code** updated with the same plain-color + animated-output fix
- **Pacing breathing** — added 0.60s pause after OLD WAY block (was 0.45s) and 0.30s post-divider (was 0.22s) so each comparison has room to breathe

---

## [0.6.2.3] — showoff: OLD WAY -> IXX WAY comparisons, readable pacing

### Changed
- **`ixx showoff` completely rewritten** with OLD WAY → IXX WAY comparison panels:
  - PowerShell wifi IP / RAM / CPU vs `ixx do "wifi ip"` / `"ram used"` / `"cpu info"`
  - Python file I/O vs `read("notes.txt")`
  - C-like if/else vs IXX readable conditionals
  - Python try/except vs IXX try/catch
- **Pacing fixed**: inter-line pauses 0.45s, code-to-output pause 0.80s (actually followable now)
- **New sections**: VARIABLES+INTERPOLATION, FILES+ERRORS, BUILT-INS code/output reveals
- **Full mode** adds: BUILT-INS, NATIVE COMMANDS note, A REAL SCRIPT, TIMELINE, slogans
- **Quick mode** shows one shell comparison, one function reveal, validation, final (~8s)
- **Plain mode** includes all default sections instantly, ASCII-only
- **`ixx> showoff`** works inside the shell (added in 0.6.2.2, documented here)
- Tests expanded to 29 showoff tests; suite total: 507 passing.

---

## [0.6.2.2] — showoff upgrade: cinematic terminal trailer

### Changed
- **`ixx showoff` completely rewritten** — animated boot sequence, before/after comparisons, code reveals, fill-bar validation matrix, section headers, TIMELINE in full mode.
- **`showoff` now works inside the IXX shell** (`ixx>` prompt).
- 5 new tests; TestShowoff total: 21 passing.

---

## [0.6.2.1] — showoff command, version release date

### Added
- **`ixx showoff`** — polished terminal presentation of IXX. Supports `quick`, `full`, and `plain` sub-modes.
- **Release date in version output** — `ixx version` now shows `ixx 0.6.2.1  (released 2026-04-24)`.
- 16 new tests in `TestShowoff` covering exit codes, content, and NO_COLOR.

---

## [0.6.2] — Shell polish: colored banner, update command, always-on update notice

### Changed
- **Shell banner**: the word `IXX` is now bold cyan when the terminal supports color.
- **Update check**: removed the 24-hour cache — IXX now checks PyPI for a newer version every time it starts (background thread, silent on failure, 2-second timeout).
- **Update notice hint**: now reads `run: update` instead of the full pip command.

### Added
- **`update` command** inside the IXX shell: type `update` to run `pip install --upgrade ixx` live. Streams pip output, then prints a success or error message.

### Fixed
- Output ordering in `update` handler: "Checking for the latest IXX version..." now reliably appears before pip output (added `flush=True`).

---

## [0.6.0] — File I/O and error handling

### Added

**File I/O built-ins**
- `read(path)` — read the full contents of a file as text
- `readlines(path)` — read a file and return its lines as a list
- `write(path, content)` — write (overwrite) text to a file
- `append(path, content)` — append text to an existing or new file
- `exists(path)` — check whether a file or folder exists (returns `YES`/`NO`)
- All five raise a friendly `IXXRuntimeError` on OS failure (file not found, permission denied, etc.)
- `write` and `append` are statement-level calls using space-separated arguments

**try / catch error handling**
- `try` / `catch` statement — runs a block and catches any `IXXRuntimeError` or OS/IO error
- `catch` block is optional; without it, errors are swallowed silently and execution continues
- Inside `catch`, the variable `error` is automatically set to the error message text
- Variables pre-declared before `try` can be updated inside the block and read after it

**`nothing` literal**
- `nothing` is now a grammar keyword and can be written directly: `result = nothing`
- Previously only producible via bare `return`; now usable as an explicit null default

**Examples**
- `examples/files.ixx` — full working demo of all five file I/O built-ins and `try`/`catch`

### Documentation
- `spec/language.md` — new `nothing`, File I/O, and try/catch sections; reserved words updated
- `spec/roadmap.md` — v0.6 marked complete

---

## [0.5.2] — color() ANSI fix on Windows CMD

### Fixed

- **`color()` showing raw escape codes on Windows CMD** — the built-in's ANSI check now calls `SetConsoleMode` to enable Virtual Terminal Processing before emitting escape codes, the same way the shell renderer does. Running `ixx script.ixx` from CMD will now show actual colors instead of `←[32m...←[0m`.

---

## [0.5.1] — Error message cleanup

### Fixed

- **Shell runtime error format** — IXX errors typed in the interactive shell (e.g. `say color(...)`) now display as `  Error: message` with consistent indentation and optional red colouring, instead of the raw `runtime error: ...` line.
- **Unknown function error** — "X is not a function. Tip: define it with: function X ..." replaced with the simpler `'X' is not defined.` — the old tip was confusing when the name was a known built-in or a valid word.

---

## [0.5.0] — Extended built-in library

### Added

**Text built-ins**
- `upper(x)` — convert to uppercase
- `lower(x)` — convert to lowercase
- `trim(x)` — strip spaces from both ends
- `replace(x, find, with)` — replace all occurrences
- `split(x)` — split on whitespace; `split(x, sep)` splits on a separator
- `join(items)` — join a list with `", "`; `join(items, sep)` uses a custom separator

**Math built-ins**
- `round(x)` — round to nearest whole number; `round(x, digits)` for decimal places
- `abs(x)` — absolute value
- `min(a, b)` / `min(list)` — smallest value
- `max(a, b)` / `max(list)` — largest value

**List built-ins**
- `first(items)` — first item; returns `nothing` if empty
- `last(items)` — last item; returns `nothing` if empty
- `sort(items)` — sorted copy
- `reverse(items)` — reversed copy (does not modify the original)

**Color output**
- `color(name, text)` — wrap text in a terminal color for use with `say`
- Available colors: `red`, `green`, `yellow`, `cyan`, `bold`, `dim`
- Respects `NO_COLOR` and `IXX_COLOR=0`; falls back to plain text when color is off

**Examples**
- `examples/stdlib.ixx` — a natural-language demo of all new built-ins

### Documentation
- `spec/language.md` — new v0.5 built-ins tables added
- `spec/roadmap.md` — v0.5 extended built-in library marked complete
- Editor grammar files updated: all new built-in names highlighted in VS Code and Notepad++

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
