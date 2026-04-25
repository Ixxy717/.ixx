# IXX Language Dictionary

Complete reference for IXX v0.6. Everything here is tested and real — nothing is
made up. If it is not listed, it is not part of the language yet.

---

## Contents

1. [Terminal / CLI commands](#1-terminal--cli-commands)
2. [Language syntax](#2-language-syntax)
3. [Values and types](#3-values-and-types)
4. [Variables](#4-variables)
5. [Operators](#5-operators)
6. [Comparisons](#6-comparisons)
7. [Logic](#7-logic)
8. [Control flow](#8-control-flow)
9. [Loops](#9-loops)
10. [Functions](#10-functions)
11. [try / catch](#11-try--catch)
12. [Built-in functions](#12-built-in-functions)
13. [IXX Shell commands](#13-ixx-shell-commands)
14. [Reserved words](#14-reserved-words)
15. [Error handling rules](#15-error-handling-rules)
16. [Environment variables](#16-environment-variables)
17. [File encoding and format notes](#17-file-encoding-and-format-notes)

---

## 1. Terminal / CLI commands

All IXX commands are run from any terminal (PowerShell, CMD, bash, etc.) after
`pip install ixx`.

| Command | What it does |
|---|---|
| `ixx` | Open the interactive IXX shell |
| `ixx shell` | Open the interactive IXX shell (explicit) |
| `ixx <file.ixx>` | Run an `.ixx` script |
| `ixx run <file.ixx>` | Run an `.ixx` script (explicit form) |
| `ixx check <file.ixx>` | Parse the script and report syntax errors; does NOT run it |
| `ixx version` | Print the installed IXX version |
| `ixx help` | Print the help overview |
| `ixx demo` | Run the bundled `try-it.ixx` demo script |
| `ixx demo interactive` | Run the step-by-step interactive walkthrough |
| `ixx setup` | Register the `.ixx` file type and icon on Windows |
| `ixx do "<command>"` | Run one IXX shell command and exit |
| `ixx showoff` | Animated terminal presentation of IXX features |
| `ixx showoff quick` | Short trailer (~8 seconds) |
| `ixx showoff full` | Extended presentation (~50 seconds) |
| `ixx showoff plain` | No animation, plain text output |

**Examples:**

```
ixx examples\hello.ixx
ixx run examples\condition.ixx
ixx check examples\advanced.ixx
ixx version
ixx do "ip wifi"
ixx do "ram used"
ixx demo interactive
```

**Update IXX:**

```
pip install --upgrade ixx
```

**Install a specific version:**

```
pip install ixx==0.6.0
```

---

## 2. Language syntax

### Files

- File extension: `.ixx`
- Encoding: UTF-8 (with or without BOM — both are accepted)
- Indentation: dash characters (`-`, `--`, `---`, etc.) instead of spaces
- Comments: `# this is a comment` (everything after `#` on a line is ignored)

### Indentation with dashes

IXX uses leading dashes to indicate block depth, not whitespace.

| Level | Prefix |
|---|---|
| Top level | no prefix |
| 1 deep | `- ` |
| 2 deep | `-- ` |
| 3 deep | `--- ` |

```
if age more than 17
- say "Adult"
- if age more than 64
-- say "Senior"
```

You can also use spaces or tabs as long as each level is consistently deeper than
the one above it. Dashes are the recommended IXX style.

### Say

Print a value or interpolated string to the terminal.

```
say "Hello"
say name
say "Hello, {name}"
say 42
say YES
say nothing
```

`say` with no arguments prints a blank line.

`say` with multiple comma-separated arguments prints them space-separated:

```
say "Total:", total       # Total: 42
say a, "+", b, "=", a + b
```

### String interpolation

Put a variable name inside `{curly braces}` in a quoted string to embed its value.

```
name = "Ixxy"
say "Hello, {name}"         # Hello, Ixxy
```

Rules:
- Only `{identifier}` syntax is supported — no expressions inside braces.
- If the variable is not defined, `{?name}` is shown in the output and a warning
  is printed to stderr. The script continues without crashing.
- String literals do **not** process escape sequences. `"\n"` is literally
  backslash-n, not a newline character.

---

## 3. Values and types

| IXX type | `type()` returns | Examples | Notes |
|---|---|---|---|
| Text (string) | `"text"` | `"hello"`, `"42"`, `""` | Always double-quoted literals |
| Number (int or float) | `"number"` | `42`, `3.14`, `-5`, `0` | No quotes |
| Bool | `"bool"` | `YES`, `NO`, `yes`, `no` | Case-insensitive |
| List | `"list"` | `1, 2, 3` or `"a", "b"` | Comma-separated |
| Nothing | `"nothing"` | `nothing` | IXX null — falsy |

### Display rules

When a value is printed (`say`) or written to a file (`write`, `append`), IXX
applies these display rules:

| Internal value | Displays as |
|---|---|
| `True` (YES) | `YES` |
| `False` (NO) | `NO` |
| `None` (nothing) | `nothing` |
| list `[1, 2, 3]` | `1, 2, 3` |
| string `"hello"` | `hello` |
| int `42` | `42` |
| float `3.14` | `3.14` |

---

## 4. Variables

Assign with `=`. No declaration keyword needed.

```
name = "Ixxy"
age = 25
active = YES
items = "apple", "banana", "grape"
empty = nothing
```

### Scope rules

- Variables declared at the top level are **global**.
- Variables first assigned inside `if`, `loop`, `try`, or `catch` blocks are
  **local to that block** and do not exist after it ends.
- To use a value computed inside a block outside of it, pre-declare the variable
  before the block:

```
result = nothing
if condition
- result = "found"
say result    # works because result was pre-declared
```

- Functions have their own isolated scope. Parameters and any new variables
  created inside a function do not affect the caller's environment.
- A variable first assigned inside a function stays local to that function call.

### Multiple assignment (list literal)

Assigning two or more comma-separated expressions creates a list:

```
items = "apple", "banana", "grape"
numbers = 1, 2, 3
```

A single expression on the right side is a plain value, not a list:

```
x = 5          # number, not a list
x = 5,         # parse error — trailing comma is not valid
```

---

## 5. Operators

| Operator | Symbol | Example | Result type |
|---|---|---|---|
| Addition / concatenation | `+` | `3 + 4` | number |
| String concatenation | `+` | `"Hello, " + name` | text |
| Subtraction | `-` | `10 - 3` | number |
| Multiplication | `*` | `5 * 2` | number |
| Division | `/` | `10 / 4` | number (float) |
| Negation | `-x` | `-5` | number |
| Grouping | `(expr)` | `(2 + 3) * 4` | any |

`+` works on numbers and on text. When either side is text, the result is string
concatenation — the other side is converted to its display form first:

```
greeting = "Hello, " + name
label = "Score: " + text(score)
mixed = "Count: " + count(items)
```

---

## 6. Comparisons

All comparisons return a bool (`YES` or `NO`).

| Comparison | Syntax | Example |
|---|---|---|
| Equal | `is` | `name is "Ixxy"` |
| Not equal | `is not` | `name is not "Guest"` |
| Less than | `less than` | `age less than 18` |
| More than | `more than` | `score more than 100` |
| At least (>=) | `at least` | `score at least 90` |
| At most (<=) | `at most` | `score at most 50` |
| Contains | `contains` | `items contains "banana"` |

`contains` works on both lists (membership check) and text (substring check):

```
items = "apple", "banana", "grape"
if items contains "banana"
- say "Found"

msg = "Hello World"
if msg contains "World"
- say "Substring found"
```

---

## 7. Logic

| Keyword | Meaning | Example |
|---|---|---|
| `and` | Both must be true | `age more than 17 and active is YES` |
| `or` | Either must be true | `x is 1 or x is 2` |
| `not` | Negate | `not active` |

`not` applied to a list: `YES` if the list is empty, `NO` if it has items.
`not` applied to `nothing`: `YES`.
`not` applied to `0` or `""`: `YES`.

---

## 8. Control flow

### if / else

```
if condition
- statement
- statement
else
- statement
```

The `else` block is optional. There is no `else if` — nest a second `if` inside
`else` if needed:

```
if score more than 90
- say "A"
else
- if score more than 80
-- say "B"
-- else
-- say "C"
```

Conditions are any expression that is truthy or falsy (see display rules table for
what is falsy: `NO`, `nothing`, `0`, `0.0`, `""`, empty list).

---

## 9. Loops

### loop (while-style)

Repeats the block as long as the condition is true.

```
count = 3
loop count more than 0
- say count
- count = count - 1
```

There is no built-in `break` or `continue`. Use a flag variable to exit early:

```
found = NO
i = 0
loop i less than count(items) and found is NO
- if items[i] is target      # note: index access not yet in language
-- found = YES
- i = i + 1
```

**Note:** Infinite loops are possible if the condition never becomes false.

---

### loop each (list iteration)

Iterates over every item in a list.

```
loop each name in list_expr
- statement
```

- `list_expr` must evaluate to a list.  Passing text, a number, or any other type raises a runtime error.
- The loop variable follows normal block scoping: it survives after the loop only if it was declared before the loop.

Examples:

```
names = "Ixxy", "Lune", "Zach"

loop each name in names
- say "Hello, {name}!"
```

```
numbers = 1, 2, 3, 4, 5
total = 0

loop each n in numbers
- total = total + n

say total
```

Nested:

```
rows = 1, 2, 3
cols = 10, 100

loop each r in rows
- loop each c in cols
-- say r * c
```

---

## 10. Functions

### Defining a function

```
function greet name
- say "Hello, {name}"
```

Zero-parameter function:

```
function hello
- say "Hello World"
```

Multiple parameters (comma-separated):

```
function add a, b
- return a + b
```

### Calling a function

**Statement position** (space-separated arguments, no parentheses, no return value):

```
greet "Ixxy"
hello
add 3, 4
```

**Expression position** (parentheses required, captures return value):

```
result = add(3, 4)
say add(10, 20)
say count(items)
```

### Return

```
function double x
- return x * 2
```

Bare `return` (no value) returns `nothing`:

```
function done
- return
```

Return exits the function immediately. Code after `return` in the same block is
not executed.

### Scope

- Parameters are local to the function.
- Variables first assigned inside a function are local to that call.
- Variables declared outside the function are accessible as read-only from inside
  (they can be read but cannot be reassigned from inside the function — a local
  variable of the same name would shadow them).
- Two-pass collection: all functions in a file are collected before execution
  begins, so you can call a function that is defined later in the file.

### Recursion

Recursion is supported. The maximum call depth is 100. Exceeding it raises a
runtime error.

```
function factorial n
- if n less than 2
-- return 1
- return n * factorial(n - 1)

say factorial(5)    # 120
```

---

## 11. try / catch

Run a block of code and handle any error without crashing the script.

```
try
- statement
catch
- say "Something went wrong: {error}"
```

- The `catch` block is optional. Without `catch`, errors are swallowed and
  execution continues after the `try` block.
- Inside `catch`, the variable `error` holds the error message as text.
- `try` catches IXX runtime errors and OS/IO errors (file not found, permission
  denied, type errors, etc.).
- Execution always continues after the `try`/`catch` block.

### Scoping inside try/catch

- `try` and `catch` each run in a **child scope**.
- **Pre-declared variables are updated** — if a variable existed before the
  block, writing to it inside the block changes the original.
- **New variables stay local** — a variable first created inside `try` or `catch`
  does not exist after the block.
- `error` is always local to `catch`.

```
# Pre-declared — survives the block
result = nothing
try
- result = read("data.txt")
catch
- say "Error: {error}"
say result    # available here

# First-declared inside try — does NOT survive
try
- local_only = "hello"
say local_only    # runtime error: not defined
```

---

## 12. Built-in functions

Built-ins are called like user-defined functions: parentheses in expression
position, space-separated in statement position.

### Core (v0.4)

| Function | Arguments | Returns | Notes |
|---|---|---|---|
| `count(x)` | list or text | number | Items in a list, or characters in text |
| `text(x)` | any | text | Converts any value to its text representation |
| `number(x)` | text or number | number | Converts text to a number; runtime error if not numeric |
| `type(x)` | any | text | Returns the IXX type name: `text`, `number`, `bool`, `list`, `nothing`. `type(YES)` returns `"bool"` — this is intentional |
| `ask(prompt)` | text (optional) | text | Prompts the user for input; returns what they typed |

```
say count("hello")          # 5
say count(1, 2, 3)          # error — pass a list variable, not bare args
items = 1, 2, 3
say count(items)            # 3
say text(42)                # 42
say number("7")             # 7
say type(YES)               # bool
say type(nothing)           # nothing
answer = ask("Name? ")
say "Hello, {answer}"
```

### Text (v0.5)

| Function | Arguments | Returns | Notes |
|---|---|---|---|
| `upper(x)` | text | text | ALL CAPS |
| `lower(x)` | text | text | all lowercase |
| `trim(x)` | text | text | Removes leading and trailing whitespace |
| `replace(x, find, with)` | text, text, text | text | Replaces all occurrences of `find` with `with` |
| `split(x, sep)` | text, text | list | Splits text on separator |
| `join(list, sep)` | list, text | text | Joins list items with separator |

```
say upper("hello")                    # HELLO
say lower("HELLO")                    # hello
say trim("  hello  ")                 # hello
say replace("the cat sat", "cat", "dog")  # the dog sat
parts = split("a,b,c", ",")
say join(parts, " | ")                # a | b | c
```

### Math (v0.5)

| Function | Arguments | Returns | Notes |
|---|---|---|---|
| `round(x)` | number | number | Round to nearest integer (or decimal places with second arg) |
| `abs(x)` | number | number | Absolute value |
| `min(a, b)` | number, number | number | Smaller of two numbers |
| `min(list)` | list | any | Smallest item in a list |
| `max(a, b)` | number, number | number | Larger of two numbers |
| `max(list)` | list | any | Largest item in a list |

```
say round(3.7)           # 4
say round(3.14159, 2)    # 3.14
say abs(-12)             # 12
say min(5, 3)            # 3
say max(5, 3)            # 5
```

### Lists (v0.5)

| Function | Arguments | Returns | Notes |
|---|---|---|---|
| `first(list)` | list | any | First element |
| `last(list)` | list | any | Last element |
| `sort(list)` | list | list | Sorted ascending (new list, original unchanged) |
| `reverse(list)` | list | list | Reversed (new list, original unchanged) |

```
items = "banana", "apple", "grape"
say first(items)       # banana
say last(items)        # grape
sorted = sort(items)
say sorted             # apple, banana, grape
rev = reverse(sorted)
say rev                # grape, banana, apple
```

### Color (v0.5)

| Function | Arguments | Returns | Notes |
|---|---|---|---|
| `color(name, text)` | text, text | text | Returns ANSI-colored text |

Supported color names: `red`, `green`, `yellow`, `cyan`, `bold`, `dim`.

```
say color("green", "All good")
say color("red", "Something wrong")
say color("yellow", "Worth checking")
say color("bold", "Important")
```

Color is disabled automatically when:
- `NO_COLOR` is set in the environment (any value)
- `IXX_COLOR=0` is set
- The output is not a terminal (piped/redirected)

Color is forced on with `IXX_COLOR=1`.

On Windows, Virtual Terminal Processing is enabled automatically when color is
used.

### File I/O (v0.6)

| Function | Arguments | Returns | Notes |
|---|---|---|---|
| `read(path)` | text | text | Reads entire file as a single string |
| `readlines(path)` | text | list | Reads file and returns list of lines |
| `write(path, content)` | text, any | nothing | Writes content to file (overwrites) |
| `append(path, content)` | text, any | nothing | Appends content to file (creates if missing) |
| `exists(path)` | text | bool | YES if the file exists, NO otherwise |

`write` and `append` use `_display()` — so `write "out.txt", YES` writes `YES`,
and `write "out.txt", nothing` writes `nothing`.

`write` and `append` are called as **statements** (space-separated, no parens for
the call itself):

```
write "notes.txt", "Hello"
append "notes.txt", " World"
```

---

### Shell bridge (v0.6.4)

| Function | Arguments | Returns | Notes |
|---|---|---|---|
| `do(command)` | text | text | Runs an IXX shell command and returns its output as text |

`do` runs the same commands available in the `ixx>` interactive shell and via
`ixx do "..."`, and returns their output as a text value instead of printing it.

```
ram_info = do("ram used")
say ram_info

ip = do("wifi ip")
say "Wi-Fi address: {ip}"

cpu = do("cpu info")
write "cpu-report.txt", cpu
```

**Error handling** — unknown commands, incomplete commands, and commands that
fail at runtime all raise a runtime error, which means `try`/`catch` works:

```
try
- result = do("bad command")
catch
- say "Command failed: {error}"
```

**Important:** `do` only runs IXX shell commands (the same set visible in
`ixx help`). It does **not** execute raw PowerShell, CMD, or Bash commands.
Raw native shell execution is a separate future feature.

`read`, `readlines`, and `exists` are typically used in **expression position**:

```
content = read("notes.txt")
lines   = readlines("notes.txt")
if exists("config.txt")
- say "Config found"
```

All five raise a runtime error if the file cannot be accessed (file not found,
permission denied, etc.). Wrap in `try`/`catch` to handle gracefully.

**Note on string escape sequences:** IXX string literals do **not** process `\n`,
`\t`, or other escape sequences. To write multi-line files, use multiple `append`
calls (the actual newline character is not writable from a string literal).

---

## 13. IXX Shell commands

These are the commands available inside the IXX interactive shell (`ixx`) or via
`ixx do "<command>"`. Commands marked ⚠️ are destructive or restricted.

### Hardware

| Command | Aliases | What it shows |
|---|---|---|
| `cpu` | — | CPU name, usage, core count |
| `cpu core-count` | `cores`, `threads` | Core and thread count |
| `cpu info` | — | Full CPU summary |
| `cpu speed` | — | Clock speed |
| `cpu temperature` | `temp` | CPU temperature (if hardware supports it) |
| `cpu usage` | `used`, `load` | CPU usage % |
| `ram` | `memory` | Total, used, and free RAM |
| `ram free` | `available`, `avail` | Free RAM |
| `ram usage` | `used`, `consumed` | RAM usage % |
| `ram total` | — | Total installed RAM |
| `ram speed` | — | RAM speed in MHz |
| `gpu` | — | All GPUs: name, VRAM, driver |
| `gpu vram` | — | VRAM size |
| `gpu driver` | — | Driver version |
| `gpu temp` | `temperature` | GPU temperature |

### Disk / Storage

| Command | Aliases | What it shows |
|---|---|---|
| `disk` | `storage`, `drive`, `drives` | List of disks |
| `disk space` | `free`, `usage`, `used` | Used/free space per disk |
| `disk partitions` | — | Partition table |
| `disk health` | — | Physical disk health status |
| `disk smart` | — | SMART predictive-failure flag |
| `disk smart full` | — | Full SMART attribute table (⚠️ requires admin) |

### Network

| Command | Aliases | What it shows |
|---|---|---|
| `network` | — | All adapters, IPs, status, gateway |
| `ip` | — | Active local IPs |
| `ip all` | — | All active IPs |
| `ip wifi` | — | Wi-Fi IPv4 address |
| `ip ethernet` | — | Ethernet IPv4 address |
| `ip local` | — | All local/private IPs |
| `ip public` | — | Public-facing IP (external lookup) |
| `wifi` | — | Wi-Fi name, IP, and signal strength |
| `ethernet` | — | Ethernet IPv4 address |
| `ports` | — | Listening ports |

### Processes

| Command | What it does |
|---|---|
| `processes` | Running processes, top 30 by RAM |
| `kill process <name\|PID>` | ⚠️ End a process by name or ID (stub — not yet live) |

### Files and Folders

| Command | Aliases | What it does |
|---|---|---|
| `folder size <path>` | — | Size of a folder |
| `open <path>` | — | Open a file or folder in Explorer |
| `list <path>` | — | List files and folders |
| `find file <pattern>` | — | Search for files by name or glob |

Supported shorthand paths: `downloads`, `desktop`, `documents`, `home`.

```
folder size downloads
open desktop
list downloads
find file "*.pdf" in downloads
```

### Scripts and demo

| Command | What it does |
|---|---|
| `demo` | Run the bundled `try-it.ixx` demo |
| `demo interactive` | Step-by-step interactive walkthrough |
| `setup` | Register `.ixx` file type and icon on Windows |

### Planned (stub — not yet live)

| Command | Note |
|---|---|
| `copy <src> to <dest>` | File copy |
| `move <src> to <dest>` | ⚠️ File move |
| `delete file <path>` | ⚠️ Delete a file |
| `delete folder <path>` | ⚠️ Delete a folder |
| `delete temp` | ⚠️ Clean temp files |
| `delete empty-trash` | ⚠️ Empty the recycle bin |
| `kill process <name>` | ⚠️ End a process |
| `native "<cmd>"` | Pass a command directly to the host shell |
| `ssh <user@host>` | Connect via SSH |
| `servers` | List saved SSH profiles |
| `server add <name>` | Save a server profile |
| `server list` | List saved server profiles |

### Shell navigation

| Input | What it does |
|---|---|
| `help` | Show help overview |
| `exit` | Exit the IXX shell |
| `quit` | Exit the IXX shell |
| Up/Down arrows | Navigate command history |
| `?` after a command | Show help for that command (`cpu ?`) |

---

## 14. Reserved words

These words cannot be used as variable or function names:

| Word | Role |
|---|---|
| `function` | Start a function definition |
| `return` | Return from a function |
| `if` | Conditional |
| `else` | Alternative branch |
| `loop` | Looping |
| `say` | Print |
| `try` | Error-handling block |
| `catch` | Error-handling handler |
| `YES` / `yes` | Boolean true literal |
| `NO` / `no` | Boolean false literal |
| `nothing` | Null literal |
| `is` | Equality comparison |
| `not` | Negation |
| `and` | Logical and |
| `or` | Logical or |
| `less` | Part of `less than` |
| `more` | Part of `more than` |
| `than` | Part of comparisons |
| `at` | Part of `at least` / `at most` |
| `least` | Part of `at least` |
| `most` | Part of `at most` |
| `contains` | Membership / substring check |

**Note:** Identifiers that start with a reserved word are allowed as long as they
are longer (e.g. `notify`, `notable`, `return_value` are all valid variable
names). The lexer uses negative lookahead to prevent keyword/identifier conflicts.

---

## 15. Error handling rules

### Runtime errors

A runtime error in a script prints an error message and exits with code 1.

```
Error: runtime error in hello.ixx
  <message>
```

Inside the IXX shell (`ixx`), runtime errors print the message and return to the
prompt — the shell does not exit.

### Syntax errors

A syntax error prints the line, a caret pointing at the problem, and a friendly
message:

```
ixx: syntax error in hello.ixx line 3

  if age less than
  ^
  Expected a value after "less than".
  Example:  if age less than 18
```

### `ixx check`

Run `ixx check <file.ixx>` to check syntax without executing.

### Error variable in catch

Inside a `catch` block, `error` is automatically set to the error message as text:

```
try
- x = number("abc")
catch
- say "Got: {error}"    # Got: cannot convert 'abc' to a number
```

---

## 16. Environment variables

| Variable | Effect |
|---|---|
| `NO_COLOR` | Set to any value to disable all ANSI color output |
| `IXX_COLOR=0` | Disable ANSI color output |
| `IXX_COLOR=1` | Force ANSI color output even if terminal detection says no |
| `IXX_NO_UPDATE_CHECK=1` | Disable the background PyPI version check |

---

## 17. File encoding and format notes

- IXX files are UTF-8. A leading BOM (`\ufeff`) is silently stripped.
- Line endings: `\n` (Unix) and `\r\n` (Windows) are both accepted. `\r` is
  stripped before parsing.
- Blank and whitespace-only lines are ignored by the preprocessor.
- Comments (`#`) are stripped before parsing; they do not affect line numbers
  significantly but error line numbers may shift slightly in heavily-commented
  files.
- IXX string literals do **not** process escape sequences. `"\n"` is literally
  backslash-n. To embed a real newline in a written file, use multiple `append`
  calls.

---

*Dictionary current as of IXX v0.6.4.*
