# Getting Started with IXX

IXX is executable checklist-style code. It uses plain English comparisons and visible dash blocks instead of braces and indentation.

---

## Install

IXX currently requires Python 3.11 or newer.

```
pip install lark
pip install -e .
```

After that, `ixx` is a command in your terminal.

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
score = 0
active = YES
```

Use `{name}` inside a string to insert a variable's value:

```
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

The `-` before a line means it belongs to the block above it.

---

## Loops

```
count = 3

loop count more than 0
- say "Tick: {count}"
- count = count - 1
```

---

## Lists

```
fruits = "apple", "banana", "grape"

if fruits contains "banana"
- say "Found it"
```

---

## All comparisons

```
if x is 10          # equal
if x is not 10      # not equal
if x less than 10   # strictly less
if x more than 10   # strictly greater
if x at least 10    # greater or equal
if x at most 10     # less or equal
if list contains x  # membership
if text contains x  # substring check
```

---

## CLI commands

```
ixx file.ixx              run a script
ixx run file.ixx          run a script (explicit)
ixx check file.ixx        check syntax without running
ixx version               print the IXX version
ixx help                  show help
ixx shell                 interactive shell (planned)
```

---

## What's next

- See `spec/language.md` for the full language reference.
- See `spec/shell.md` for the planned interactive shell design.
- See `spec/roadmap.md` for where IXX is headed.
- See `examples/` for working scripts.

---

## Running the tests

The prototype ships with a full automated test suite.

```
python -m unittest discover -s tests -p "test*.py"
```

98 tests passing across: basics, strings, numbers, booleans, conditions, dash blocks, loops, lists, comparisons, `contains`, logic, error handling, and CLI commands.

---

## Current limitations

- Requires Python 3.11+ and the `lark` library.
- No interactive shell or REPL yet.
- No built-in system commands yet (`cpu`, `ram`, `ip`, etc. are planned — see `spec/shell.md`).
- No functions, file I/O, or imports yet.
- Variable names must be single words (letters, numbers, underscores).
- Reserved words cannot be used as variable names: `if`, `else`, `loop`, `say`, `and`, `or`, `not`, `is`, `less`, `more`, `than`, `at`, `least`, `most`, `contains`, `YES`, `NO`.

---

## Note on this implementation

The current IXX interpreter is written in Python using the Lark parser library.
This is prototype v0 — it proves the grammar and syntax design without the overhead of building a compiler from scratch.

Python is the implementation language for this phase only.
It is not the long-term identity of IXX.

The long-term goal is a standalone `ixx` binary that requires nothing else to be installed.
See `spec/roadmap.md` for the full plan.
