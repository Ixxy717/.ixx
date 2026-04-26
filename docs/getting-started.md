# Getting Started with IXX

IXX is executable checklist-style code. It uses plain English comparisons and visible dash blocks instead of braces and indentation. It should feel like writing a checklist or a set of instructions, not programming.

---

## Install

```
pip install ixx
```

After that, `ixx` is a command in your terminal.

To upgrade:

```
pip install --upgrade ixx
```

---

## Running scripts

```
ixx hello.ixx           run a script
ixx run hello.ixx       run a script (explicit)
ixx check hello.ixx     check syntax without running
ixx                     open the interactive shell
ixx shell               open the interactive shell (explicit)
```

---

## Your first script

Create a file called `hello.ixx`:

```
say "Hello World"
```

Run it:

```
ixx hello.ixx
```

Output:

```
Hello World
```

---

## Variables

```
name = "Ixxy"
age = 19
score = 3.14
active = YES
```

Variable names are single words (letters, numbers, underscores, starting with a letter).

---

## Saying things

```
say "Hello World"
say name
say "Hello, {name}"
```

Put `{varname}` inside a string to insert a variable's value.

`say` accepts multiple comma-separated values:

```
say "Hello,", name, "!"
```

---

## Comments

```
# This is a comment
name = "Ixxy"   # inline comment is fine too
```

Lines starting with `#` are ignored. `//` and `--` are **not** comment syntax — `--` is the two-level dash block prefix.

---

## String escape sequences

IXX processes three escape sequences inside string literals:

| Sequence | Meaning |
|---|---|
| `\n` | Newline |
| `\t` | Tab |
| `\\` | Single backslash |

```
say "Line 1\nLine 2"        # two lines
say "col1\tcol2"            # tab-separated
say "C:\\Temp\\file.txt"    # prints C:\Temp\file.txt
```

On Windows, you can also use forward slashes in paths:

```
say read("C:/Temp/file.txt")   # same as C:\Temp\file.txt
```

---

## Conditions

```
age = 19

if age less than 18
- say "Not adult"
else
- say "Adult"
```

The `-` before a line means it belongs to the block above it. No indentation counting. No invisible whitespace.

### All comparisons

```
if x is 10          # equal
if x is not 10      # not equal
if x less than 10   # strictly less
if x more than 10   # strictly greater
if x at least 10    # greater or equal
if x at most 10     # less or equal
if list contains x  # membership or substring check
```

### Bare conditions

A condition can be a single variable — no comparison operator required:

```
active = YES
if active
- say "Account is active"

name = ""
if not name
- say "No name set"
```

`YES`, non-zero numbers, non-empty text, and non-empty lists are **true**.
`NO`, `0`, `""`, `nothing`, and empty lists are **false**.

### and / or

```
if ready and logged_in
- say "Go"

if tired or bored
- say "Take a break"
```

`and` and `or` use short-circuit evaluation — the right side is only evaluated when necessary.

---

## Loops

**While-style loop:**

```
count = 3

loop count more than 0
- say "Countdown: {count}"
- count = count - 1
```

**List iteration:**

```
names = "Ixxy", "Lune", "Zach"

loop each name in names
- say "Hello, {name}"
```

`loop each` iterates over every item in the list. The loop variable is local by default — it does not survive past the loop unless you declared it before the loop.

---

## Lists

```
fruits = "apple", "banana", "grape"

if fruits contains "banana"
- say "Found it"

say count(fruits)    # 3
say first(fruits)    # apple
say last(fruits)     # grape
```

---

## Functions

Define a function with `function`. Call it with space-separated arguments (statement position) or with parentheses (expression position):

```
function greet name
- say "Hello, {name}"

greet "World"               # statement — no parens

function add a, b
- return a + b

result = add(3, 4)          # expression — parens required
say result                  # 7
```

### Return list literals

Functions can return a list directly:

```
function items
- return "a", "b", "c"

say count(items())          # 3
```

### try / catch

Run code that might fail:

```
result = nothing
try
- result = read("config.txt")
catch
- say "Could not read config: {error}"
```

`error` is only available inside the `catch` block. A bare `try` without `catch` silently continues.

---

## File I/O

```
write "log.txt", "Hello"
append "log.txt", "\nWorld"

content = read("log.txt")
say content

lines = readlines("log.txt")
say count(lines)

if exists("log.txt")
- say "File exists"
```

File paths in `read()` and `readlines()` are resolved **relative to the script's own directory**, not the terminal's current folder. Absolute paths and forward slashes work on all platforms.

---

## Imports

Reuse code from another file:

```
use "helpers.ixx"
```

Functions defined in `helpers.ixx` are available in the current script. Top-level statements in the imported file do not run — only function definitions are imported.

Standard library modules:

```
use std "time"
use std "date"
```

---

## IXX shell (interactive)

Open the shell with `ixx` (or `ixx shell`):

```
ixx> name = "Ixxy"
ixx> say name
Ixxy

ixx> function double x
...  - return x * 2
ixx> say double(21)
42

ixx> ip wifi
Wi-Fi: 192.168.1.42

ixx> ram used
  Used: 15.5 GB  (50%)
```

The shell remembers variables and functions for the duration of the session. Import files work in the shell too.

Command history is saved to `~/.ixx_history` and is available between sessions on systems that support readline.

---

## ixx check

Run a static analysis pass without executing the script:

```
ixx check script.ixx
```

Reports syntax errors and common semantic issues (undefined variables, wrong argument counts, unknown function calls, etc.).

Machine-readable JSON output for editor integration:

```
ixx check script.ixx --json
```

JSON output includes `"ok"` (true/false) and an `"errors"` array. Warnings appear with `"severity": "warning"` — a file with only warnings still gets `"ok": true`.

```
# Common checker warnings
count = 5   # warning: 'count' shadows the built-in 'count'
```

Top-level `return` is a static error:

```
return 42   # error: 'return' can only be used inside a function
```

---

## Number display

IXX displays numbers cleanly — no trailing `.0`, no excessive decimal places:

```
say 10 / 2      # 5  (not 5.0)
say 0.1 + 0.2   # 0.3
say 3.14        # 3.14
```

`number("inf")` and `number("nan")` raise a runtime error — these are not valid IXX numbers.

---

## Keyword interpolation

IXX literal keywords can be used inside string interpolation:

```
active = YES
say "Active: {YES}"     # Active: YES
say "Done: {NO}"        # Done: NO
say "Value: {nothing}"  # Value: nothing
```

---

## Examples in this repo

- `examples/` — main working example scripts
- `examples/errors/` — intentional failure examples (these are expected to raise errors)
- `examples/archive/` — historical syntax examples from earlier versions

---

## Running the tests

Python unit tests:

```
python -m unittest discover -s tests -p "test*.py"
```

End-to-end StressTest suite:

```
StressTest\run-all.cmd           normal suite
StressTest\Hard\run-hard.cmd     hard tests
StressTest\Scenario\run-scenario.cmd  scenario tests
```

Expected-failure tests inside `StressTest\ExpectedFailures\` are intentional — they pass the gate when they fail correctly.

---

## What's next

- See `spec/language.md` for the full language reference.
- See `spec/dictionary.md` for the complete IXX language dictionary.
- See `spec/shell.md` for the interactive shell design.
- See `spec/roadmap.md` for where IXX is headed.

---

## Current limitations

- Requires Python 3.11+ and the `lark` library.
- Variable names must be single words (no spaces).
- Shell system commands are Windows-first; Linux/macOS adapters are planned.
- Destructive file commands (`delete`, `copy`, `move`) are registered in the guidance tree but do not execute yet.
- Expressions must fit on one line — multi-line expressions are not supported.
