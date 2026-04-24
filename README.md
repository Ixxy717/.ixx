# IXX

IXX is executable checklist-style code. It uses plain English comparisons and visible dash blocks instead of braces, indentation, and symbolic clutter.

```
age = 19

if age less than 18
- say "Not adult"
else
- say "Adult"
```

---

## Quick start

```
pip install lark
pip install -e .
```

Then `ixx` is a command in your terminal.

---

## Hello World

```
say "Hello World"
```

```
ixx hello.ixx
```

---

## Variables and string interpolation

```
name = "Ixxy"
say "Hello, {name}"
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

The `-` at the start of a line means it belongs to the block directly above. No indentation rules. No invisible whitespace.

---

## Lists and contains

```
items = "apple", "banana", "grape"

if items contains "banana"
- say "Found it"
else
- say "No banana"
```

---

## Loops

```
count = 3

loop count more than 0
- say "Countdown: {count}"
- count = count - 1

say "Done"
```

---

## All comparisons

```
if x is 10           # equal
if x is not 10       # not equal
if x less than 10    # strictly less
if x more than 10    # strictly greater
if x at least 10     # greater or equal
if x at most 10      # less or equal
if list contains x   # membership
if text contains x   # substring check
```

---

## Logic

```
if ready and logged_in
- say "Go"

if tired or bored
- say "Take a break"

if not active
- say "Inactive"
```

---

## Booleans

```
active = YES
done = NO
```

---

## Nested blocks

```
if user is "Ixxy"
- say "Hello Ixxy"
- if age at least 18
-- say "Adult account"
- else
-- say "Limited account"
```

---

## CLI

| Command | What it does |
|---|---|
| `ixx file.ixx` | run a script |
| `ixx run file.ixx` | run a script (explicit) |
| `ixx check file.ixx` | check syntax without running |
| `ixx version` | print the IXX version |
| `ixx help` | show help and quick-reference |
| `ixx shell` | interactive shell (planned) |

---

## Current limitations

- Requires Python 3.11+ and the `lark` library.
- No interactive shell or REPL yet.
- No built-in system commands yet (`cpu`, `ram`, `ip`, etc. are planned).
- No functions, file I/O, or imports yet.
- Variable names must be single words (no spaces).
- Reserved words cannot be used as variable names: `if`, `else`, `loop`, `say`, `and`, `or`, `not`, `is`, `less`, `more`, `than`, `at`, `least`, `most`, `contains`, `YES`, `NO`.

---

## This is prototype v0

The current implementation uses Python and the Lark parser library. This is a proof of concept to validate the grammar and interpreter design.

Python is the implementation language for this phase only. It is not the long-term identity of IXX.

The long-term goal is a standalone IXX binary that requires nothing else to be installed — likely written in Go, Rust, or a similar compiled language. See [`spec/roadmap.md`](spec/roadmap.md) for the full plan.

---

## Tests

The prototype ships with a full automated test suite.

```
python -m unittest discover -s tests -p "test*.py"
```

**98 tests passing** across: basics, strings, numbers, booleans, conditions, dash blocks, loops, lists, comparisons, `contains`, logic, error handling, and CLI commands.

---

## Project layout

```
ixx/            prototype interpreter (Python)
examples/       example .ixx scripts
spec/           language spec, shell design, roadmap
docs/           getting started guide
tests/          automated tests
CHANGELOG.md    version history
```

---

## More

- [`spec/language.md`](spec/language.md) — full language reference
- [`spec/shell.md`](spec/shell.md) — planned interactive shell design
- [`spec/roadmap.md`](spec/roadmap.md) — where IXX is going
- [`docs/getting-started.md`](docs/getting-started.md) — step by step setup
