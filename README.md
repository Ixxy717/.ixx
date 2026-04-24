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
| `ixx` | open the interactive shell |
| `ixx shell` | open the interactive shell |
| `ixx do "ip wifi"` | run one shell command and exit |

---

## IXX Shell

Open the shell with `ixx`, then use everyday commands without memorising native syntax.

```
ixx> ip
Adapter      IPv4
-----------  ---------------
Wi-Fi        192.168.1.42

ixx> ip wifi
Wi-Fi: 192.168.1.42

ixx> cpu
  CPU:     AMD Ryzen 9 5950X
  Cores:   16
  Threads: 32
  Usage:   12%

ixx> cpu core-count
  AMD Ryzen 9 5950X
  Cores:   16
  Threads: 32

ixx> ram
  RAM
  Total: 64.0 GB
  Used:  21.0 GB
  Free:  43.0 GB

ixx> disk
Drive  Label   Total    Free
-----  ------  -------  -------
C:     System  2.0 TB   870 GB

ixx> disk space
ixx> folder size downloads
  downloads: 14.2 GB

ixx> open desktop
  Opened: C:\Users\you\Desktop

ixx> list downloads
```

Single-command mode (useful for scripts and automation):

```
ixx do "ip"
ixx do "cpu core-count"
ixx do "folder size downloads"
```

Notes:
- v0.3.0 is Windows-first for real system commands.
- Cross-platform adapters (Linux, macOS) are planned for a future release.
- Destructive commands (`delete`, `kill process`, `copy`, `move`) are still stubbed for safety.
- The Python implementation is prototype v0 — not the final runtime.

---

## Current limitations

- Requires Python 3.11+ and the `lark` library.
- No functions, file I/O, or imports yet.
- Variable names must be single words (no spaces).
- Reserved words cannot be used as variable names: `if`, `else`, `loop`, `say`, `and`, `or`, `not`, `is`, `less`, `more`, `than`, `at`, `least`, `most`, `contains`, `YES`, `NO`.
- Shell system commands are Windows-first in v0.3.0; Linux/macOS adapters are planned.
- Destructive commands (`delete`, `kill process`, `copy`, `move`) exist in the guidance tree but do not execute yet.

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
