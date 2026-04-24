# IXX — Project Overview

A language you can actually read without having studied programming.

---

## What IXX is

IXX is a small programming language that looks and feels like a checklist or a set of plain instructions.
The goal is to make it easy to tell the computer what to do without memorizing a dictionary of symbols and special rules.

It is not trying to replace Python or Rust for complex software.
It is trying to be the easiest way to write simple logic, automate everyday tasks, and eventually run system commands — without the garbage that comes with PowerShell, CMD, and Bash.

---

## What it looks like

```
say "Hello World"
```

```
name = "Ixxy"
say "Hello, {name}"
```

```
age = 19

if age less than 18
- say "Not adult"
else
- say "Adult"
```

```
items = "apple", "banana", "grape"

if items contains "banana"
- say "Found it"
```

```
count = 3

loop count more than 0
- say "Countdown: {count}"
- count = count - 1

say "Done"
```

---

## Design rules

- No indentation. Use `-` lines to mark what belongs to a block.
- No braces. No semicolons. No colons.
- No symbolic soup like `===`, `&&`, `||`, `{}`, `()` for basic logic.
- Word-based comparisons: `is`, `is not`, `less than`, `more than`, `at least`, `at most`, `contains`.
- `YES` and `NO` instead of `true` and `false`.
- `say` instead of `print`.
- `loop` instead of `while`.
- `else` instead of `otherwise` or `elif`.
- `{varname}` inside strings for interpolation.
- `=` is fine. Commas are fine. Quotes are fine.
- The point is not to remove all symbols. The point is to remove annoying programming clutter.

---

## The dash block system

A line with a `-` at the start belongs to the statement directly above it.

```
no dash    = top level
-          = one level deep
--         = two levels deep
---        = three levels deep
```

Example:

```
if user is "Ixxy"
- say "Hello Ixxy"
- if age at least 18
-- say "Adult account"
- else
-- say "Limited account"
```

The spaces after dashes are optional but recommended.

---

## The language so far

### Values

| Type    | Example                         |
|---------|---------------------------------|
| Text    | `"Hello"`, `"Ixxy"`             |
| Number  | `42`, `3.14`, `-10`             |
| Boolean | `YES`, `NO` (case-insensitive)  |
| List    | `"apple", "banana", "grape"`    |

### Comparisons

| Operator   | Meaning           |
|------------|-------------------|
| `is`       | equal             |
| `is not`   | not equal         |
| `less than`| strictly less     |
| `more than`| strictly greater  |
| `at least` | greater or equal  |
| `at most`  | less or equal     |
| `contains` | list or text      |

### Logic

```
and   or   not
```

### Arithmetic

```
+   -   *   /
```

String concatenation also uses `+`:

```
greeting = "Hello, " + name
```

### String interpolation

```
name = "Ixxy"
say "Hello, {name}"
# prints: Hello, Ixxy
```

### Lists

```
fruits = "apple", "banana", "grape"
if fruits contains "banana"
- say "Found it"
```

### Reserved words

`if`, `else`, `loop`, `say`, `and`, `or`, `not`, `is`, `less`, `more`, `than`, `at`, `least`, `most`, `contains`, `YES`, `NO`

---

## The CLI

```
ixx file.ixx              run a script
ixx run file.ixx          run a script (explicit)
ixx check file.ixx        check syntax, do not run
ixx version               print the IXX version
ixx help                  show help and quick-reference
ixx shell                 interactive shell (planned)
```

---

## How it works under the hood

IXX currently runs as a Python package. Python is just the engine for the prototype — it is not the long-term identity of the language.

```
your .ixx file
     |
     v
preprocessor        converts  -  --  ---  into spaces
     |
     v
Lark LALR parser    reads the grammar, produces a parse tree
     |
     v
AST transformer     converts the parse tree into clean data structures
     |
     v
interpreter         walks the AST and runs your program
```

The grammar is defined in `ixx/grammar.lark`. The whole language spec lives there in about 70 lines.

---

## Project files

```
ixx/
  grammar.lark        the IXX language grammar rules
  preprocessor.py     converts dash lines to spaces before parsing
  parser.py           loads the grammar, runs the parser
  ast_nodes.py        data structures for the parsed program
  build_ast.py        transforms the parse tree into those structures
  interpreter.py      runs the program
  __main__.py         the ixx CLI command

examples/
  hello.ixx           say "Hello World"
  condition.ixx       age / adult example
  lists.ixx           items contains banana
  advanced.ixx        full showcase of language features
  system-info.ixx     placeholder for future built-in system commands
  files.ixx           placeholder for future file commands

spec/
  language.md         full language reference
  shell.md            the IXX console/shell design (not yet built)
  roadmap.md          phases: prototype -> standalone -> shell -> stdlib

docs/
  getting-started.md  install and first steps

tests/
  language/           (empty, structure ready)
  commands/
  paths/
  safety/

pyproject.toml        Python project config and dependencies
```

---

## The long-term plan

### Phase 0 — now
Python prototype. Proves the grammar and interpreter. Requires Python + Lark installed.

### Phase 1 — standalone binary
Ship `ixx` as a single executable with no Python dependency. Either bundle with PyInstaller or rewrite the interpreter in Go or Rust.

### Phase 2 — interactive shell
`ixx shell` opens a console. Type commands, get results. Live grammar-aware guidance shows what arguments are valid as you type. History, fuzzy correction, help system.

### Phase 3 — built-in system commands
Replace the most annoying PowerShell / CMD / Bash commands with readable IXX equivalents.

```
cpu              ram              disk             ip wifi
folder size downloads            find file "resume"
delete folder temp recursive     open desktop
```

### Phase 4 — scripting power
Functions, file I/O, HTTP, date/time, importing other `.ixx` files, standard library.

---

## What the shell will eventually feel like

Instead of:

```powershell
(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi').IPAddress
```

You write:

```
ip wifi
```

Instead of:

```powershell
Get-ChildItem -Path ".\TargetFolder" -Recurse -Force | Remove-Item -Force -Recurse
```

You write:

```
delete folder TargetFolder recursive
```

The shell will ask you to confirm before deleting anything. It will show you what it is about to do. It will explain errors in plain language.

---

## The one-sentence version

IXX is a language that feels like executable notes — readable, obvious, and actually usable for real things without needing to be a programmer.
