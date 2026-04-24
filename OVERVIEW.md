# IXX — In-Depth Overview

A language and shell for people who just want to tell the computer what to do.

---

## Table of contents

1. [What IXX is](#1-what-ixx-is)
2. [Why it exists](#2-why-it-exists)
3. [The language](#3-the-language)
4. [The shell](#4-the-shell)
5. [How it works — architecture](#5-how-it-works--architecture)
6. [Design philosophy](#6-design-philosophy)
7. [Project layout](#7-project-layout)
8. [Current status and versions](#8-current-status-and-versions)
9. [Long-term vision](#9-long-term-vision)
10. [What IXX is not](#10-what-ixx-is-not)

---

## 1. What IXX is

IXX is two things in one package:

**A small programming language** that looks like a checklist or a set of plain instructions. It uses real English words for comparisons, visible dash characters to show block structure, and `say` to print. It does not require a main function, curly braces, indentation rules, or semicolons.

**An interactive command shell** designed to replace the everyday parts of PowerShell, CMD, Bash, and macOS Terminal with a single consistent syntax. System queries, file operations, network info, and hardware info all answer in plain readable output. The same commands work the same way regardless of which OS is underneath.

IXX's long-term goal is to be the one command interface people actually reach for instead of memorizing the syntax differences between `ipconfig`, `ip addr`, `Get-NetIPAddress`, and `ifconfig` — and everything else like them.

Both halves share the same identity: readable, calm, obvious output.

```
say "Hello, {name}"

if age less than 18
- say "Not adult"
else
- say "Adult"
```

```
ixx> ip wifi
Wi-Fi: 192.168.1.42

ixx> cpu
  CPU:     AMD Ryzen 9 5950X
  Cores:   16
  Threads: 32
  Usage:   12%

ixx> folder size downloads
  downloads: 14.2 GB
```

---

## 2. Why it exists

### The problem with existing tools

**PowerShell** is powerful but hostile to anyone who does not live in it. Getting a Wi-Fi IP address looks like this:

```powershell
(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi').IPAddress
```

Getting folder size looks like this:

```powershell
(Get-ChildItem -Path "$env:USERPROFILE\Downloads" -Recurse -Force |
 Measure-Object -Property Length -Sum).Sum / 1GB
```

These are real answers to simple questions. Nobody should need to memorize them.

**CMD** is older, less capable, and even less readable.

**Bash** is better but inconsistent across platforms and still requires substantial learning for common tasks.

**Python** is an excellent language but requires `import`, indentation rules, `if __name__ == "__main__"`, and a dozen ways to print a string. It is a great tool but not the right tool for a ten-line task or a quick command.

**The gap:** There is a large space between "type a command and get an answer" and "write a full script in a real language." That space is where IXX lives.

### The language half

Plenty of people can read a recipe, a checklist, or a set of instructions. IXX tries to make code look exactly like that. The logic of `if age is less than 18, say "Not adult"` is obvious to anyone. The only change IXX makes is writing it on two lines with a dash:

```
if age less than 18
- say "Not adult"
```

That is it. That is the syntax.

### The shell half

IXX is also tired of the fact that asking a computer a simple question requires knowing which tool to reach for (`ipconfig`? `Get-NetIPAddress`? `ip addr`? `ifconfig`?), which syntax that tool uses, and then parsing output that looks like it was written for a log file rather than a person.

The IXX shell answers those questions in a consistent, readable way, regardless of what OS you are on or which native command sits underneath.

---

## 3. The language

### 3.1 Running a script

```
ixx myscript.ixx
```

Or explicitly:

```
ixx run myscript.ixx
```

Or just check syntax without running:

```
ixx check myscript.ixx
```

Scripts start executing from the first line. No entry point boilerplate.

---

### 3.2 Variables

```
name = "Ixxy"
age = 19
score = 3.14
active = YES
```

Variable names are single words: letters, numbers, underscores, starting with a letter or underscore. Assignment uses `=`. No `let`, no `var`, no type annotations.

---

### 3.3 Types

| Type    | Examples                       | Notes                             |
|---------|--------------------------------|-----------------------------------|
| Text    | `"Hello"`, `"world"`           | Double quotes. UTF-8.             |
| Number  | `42`, `3.14`, `-10`            | Integer or float. Same type.      |
| Boolean | `YES`, `NO`                    | Case-insensitive.                 |
| List    | `"apple", "banana", "grape"`   | Comma-separated series of values. |

---

### 3.4 String interpolation

Use `{varname}` anywhere inside a string:

```
name = "Ixxy"
say "Hello, {name}"
# → Hello, Ixxy
```

```
score = 92
say "Your score is {score} out of 100"
# → Your score is 92 out of 100
```

If the variable does not exist, `{varname}` is left as literal text without crashing.

---

### 3.5 The dash block system

This is the most distinctive part of IXX. Instead of indentation or curly braces, blocks use leading dashes.

```
no dash   = top-level
-         = one level deep
--        = two levels deep
---       = three levels deep
```

The space after the dash is optional but recommended. The block belongs to the last statement at the level above it.

**Simple block:**

```
if score at least 90
- say "Grade A"
- say "Well done"
```

**Nested block:**

```
if user is "Ixxy"
- say "Hello Ixxy"
- if age at least 18
-- say "Adult account"
-- say "Full access"
- else
-- say "Limited account"
```

This is unambiguous. You can read it at a glance. No counting spaces. No invisible indentation errors.

Under the hood, the preprocessor converts dashes to spaces before the Lark parser sees the source. The user never has to think about this.

---

### 3.6 Comparisons

All comparison operators use words:

| Operator    | Meaning            | Example                        |
|-------------|--------------------|--------------------------------|
| `is`        | equal              | `if score is 100`              |
| `is not`    | not equal          | `if status is not "banned"`    |
| `less than` | strictly less      | `if age less than 18`          |
| `more than` | strictly greater   | `if score more than 50`        |
| `at least`  | greater or equal   | `if score at least 90`         |
| `at most`   | less or equal      | `if lives at most 2`           |
| `contains`  | membership / text  | `if items contains "banana"`   |

`contains` works on both lists and text:

```
fruits = "apple", "banana", "grape"
if fruits contains "banana"
- say "Found it"

message = "Hello World"
if message contains "World"
- say "Found World"
```

---

### 3.7 Logic

```
if ready and logged_in
- say "Go"

if tired or bored
- say "Take a break"

if not active
- say "Account is inactive"
```

`and`, `or`, `not` are the complete set. Parentheses can be used for grouping.

---

### 3.8 Arithmetic

```
total  = score + bonus
diff   = 100 - score
area   = width * height
half   = total / 2
neg    = -score
```

String concatenation uses `+`:

```
greeting = "Hello, " + name
```

---

### 3.9 if / else

```
if condition
- statement
- statement
else
- statement
- statement
```

`else` is optional. There is no `else if` yet — nested `if` inside the `else` block serves the same purpose:

```
if score at least 90
- say "A"
else
- if score at least 80
-- say "B"
- else
-- say "Below B"
```

---

### 3.10 loop

Repeats while a condition is true:

```
count = 3

loop count more than 0
- say "Countdown: {count}"
- count = count - 1

say "Done"
```

This is equivalent to `while` in other languages. There is no `for` loop yet. `loop` is the one loop construct.

---

### 3.11 say

Outputs to the screen. Accepts one or more comma-separated expressions:

```
say "Hello World"
say name
say "Score:", score
say fruits
# → apple, banana, grape
```

Lists are printed as comma-separated values. Numbers and booleans are printed as-is.

---

### 3.12 Comments

```
# This is a comment
say "Hello"   # This also works inline
```

Lines starting with `#` are ignored. Inline comments after code are supported.

---

### 3.13 Truthiness

| Value type | True when      | False when   |
|------------|----------------|--------------|
| Boolean    | `YES`          | `NO`         |
| Number     | any non-zero   | `0`          |
| Text       | any non-empty  | `""`         |
| List       | non-empty list | empty list   |

---

### 3.14 Scoping

Variables set inside a block that were already defined in an outer scope are updated in the outer scope. Variables created for the first time inside a block are local to that block.

```
count = 10

if count more than 5
- count = count - 1     # outer count is modified

say count               # → 9
```

---

### 3.15 A complete example

```
name = "Ixxy"
age = 19
score = 92
fruits = "apple", "banana", "grape"

say "Hello, {name}"

if age less than 18
- say "Not adult"
else
- say "Adult"

if score at least 90
- say "Grade: A"

if fruits contains "banana"
- say "Found banana"

count = 3
loop count more than 0
- say "Countdown: {count}"
- count = count - 1

say "Done"
```

Output:

```
Hello, Ixxy
Adult
Grade: A
Found banana
Countdown: 3
Countdown: 2
Countdown: 1
Done
```

---

## 4. The shell

### 4.1 Opening the shell

```
ixx
```

or:

```
ixx shell
```

Both open the IXX interactive prompt:

```
IXX Shell  0.3.0-dev
Type a command to get started, or 'help' for a list.
Type 'exit' to leave.

ixx>
```

---

### 4.2 What works in v0.3.0

These commands run real system queries on Windows:

**Network**

```
ixx> ip
Adapter      IPv4
-----------  ---------------
Wi-Fi        192.168.1.42
Ethernet     not connected

ixx> ip wifi
Wi-Fi: 192.168.1.42

ixx> ip ethernet
No connected Ethernet adapter found.

ixx> ip local
192.168.1.42          Wi-Fi

ixx> network
Adapter   Status       IPv4          Gateway
--------  -----------  ------------  -----------
Wi-Fi     connected    192.168.1.42  192.168.1.1
```

**Hardware**

```
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
```

**Disk**

```
ixx> disk
Drive  Label   Total    Free
-----  ------  -------  --------
C:     System  2.0 TB   870.0 GB
D:     Data    4.0 TB   2.1 TB

ixx> disk space
Drive  Label   Total    Used    Free      Used%
-----  ------  -------  ------  --------  -----
C:     System  2.0 TB   1.1 TB  870.0 GB  57%
```

**Files and folders**

```
ixx> folder size downloads
  downloads: 14.2 GB

ixx> folder size "desktop/my project"
  my project: 841.3 MB

ixx> list downloads
  C:\Users\you\Downloads

  Name              Type    Size
  ----------------  ------  --------
  Projects          folder  -
  report.pdf        file    1.2 MB
  photo.png         file    842 KB

ixx> open desktop
  Opened: C:\Users\you\Desktop
```

---

### 4.3 Single-command mode

Run one shell command and exit — useful for automation and scripts:

```
ixx do "ip"
ixx do "ip wifi"
ixx do "cpu core-count"
ixx do "folder size downloads"
```

Both of these work identically:

```
ixx do "ip wifi"
ixx do ip wifi
```

---

### 4.4 Path aliases

These aliases are understood anywhere a path is accepted:

| Alias       | Resolves to                     |
|-------------|----------------------------------|
| `desktop`   | `~/Desktop`                      |
| `downloads` | `~/Downloads`                    |
| `documents` | `~/Documents`                    |
| `pictures`  | `~/Pictures`                     |
| `music`     | `~/Music`                        |
| `videos`    | `~/Videos`                       |
| `home`      | `~` (user home directory)        |
| `temp`      | system temp folder               |
| `appdata`   | `%APPDATA%` on Windows           |
| `here`      | current working directory        |
| `current`   | current working directory        |
| `.`         | current working directory        |

Sub-paths work with forward slashes regardless of OS:

```
ixx> folder size desktop/projects
ixx> list "documents/school stuff"
ixx> open downloads
```

---

### 4.5 Command guidance

If you type a command that has sub-options, the shell shows what you can type next instead of silently failing:

```
ixx> delete

  file      Delete a single file
  folder    Delete a folder [recursive] [force] [dry-run]
  temp      Clean temporary files
  empty-trash  Empty the recycle bin / trash

  Warning: destructive — will prompt before acting.
```

Commands that are "executable parents" — `ip`, `cpu`, `ram`, `disk`, `network` — run an overview and also show their options when you type `?`:

```
ixx> ip ?

  all        All active IPs
  wifi       Wi-Fi IPv4 address
  ethernet   Ethernet IPv4 address
  local      All local/private IPs
  public     Public-facing IP address
```

---

### 4.6 Help system

```
ixx> help

ixx> help ip
ip  -  Show active local IP addresses

  Subcommands:
    all       All active IPs
    wifi      Wi-Fi IPv4 address
    ethernet  Ethernet IPv4 address
    local     All local/private IPs
    public    Public-facing IP address

  Examples:
    ip
    ip wifi
    ip ethernet
    ip local

ixx> help folder
folder  -  Folder operations

  Subcommands:
    size   Size of a folder

  Examples:
    folder size downloads
    folder size desktop
    folder size "desktop/my folder"
```

---

### 4.7 Fuzzy correction

Mistyped commands get a suggestion instead of a hard error:

```
ixx> diks
  Unknown command: diks
  Did you mean: disk?

ixx> foler
  Unknown command: foler
  Did you mean: folder?

ixx> cpoy
  Unknown command: cpoy
  Did you mean: copy?
```

---

### 4.8 Stubs — commands registered but not yet live

Some commands are in the guidance tree but do not execute real operations yet. They print a clean stub message:

```
ixx> gpu
  [gpu  -  not yet implemented, planned for a future release]

ixx> kill process chrome
  [kill process  -  not yet implemented, planned for a future release]

ixx> ssh my-server
  [ssh  -  not yet implemented, planned for remote access release]
```

Registered stub commands: `gpu`, `ports`, `processes`, `kill process`, `copy`, `move`, `delete`, `find file`, `native`, `ssh`, `servers`, `server add`, `server list`, `wifi` (standalone), `cpu temperature`, `cpu speed`, `cpu info`, `ram free`, `ram usage`, `ram speed`, `disk health`, `disk partitions`, `ip public`.

---

## 5. How it works — architecture

### 5.1 The language pipeline

```
your .ixx file
      |
      v
  Preprocessor              ixx/preprocessor.py
  Converts - -- --- lines   
  to standard indentation   
      |
      v
  Lark LALR Parser           ixx/parser.py + ixx/grammar.lark
  Reads the grammar,         
  produces a parse tree      
      |
      v
  AST Transformer            ixx/build_ast.py
  Converts the parse tree    
  to clean data structures   ixx/ast_nodes.py
      |
      v
  Interpreter                ixx/interpreter.py
  Walks the AST and          
  executes your program      
```

**The preprocessor** runs first. It converts dash-based lines into standard 4-space indentation so Lark can handle them with its normal `INDENT`/`DEDENT` mechanism. The user never sees this step.

**The grammar** (`grammar.lark`) is about 70 lines and defines the entire IXX language in LALR form. It is the authoritative language definition.

**The AST transformer** (`build_ast.py`) converts the Lark parse tree into typed Python dataclasses (`ast_nodes.py`): `Program`, `Assign`, `IfStmt`, `LoopStmt`, `SayStmt`, `Compare`, `BinOp`, `ListLit`, and others.

**The interpreter** walks these nodes recursively. It maintains an `Environment` for variable scoping and dispatches each node type to the correct evaluation function.

---

### 5.2 The shell pipeline

```
user types: ip wifi
      |
      v
  Tokenizer                  ixx/shell/repl.py → _tokenize()
  Splits on whitespace,      
  preserves quoted strings   ["ip", "wifi"]
      |
      v
  Guidance Engine            ixx/shell/guidance.py → get_guidance()
  Walks the command tree,    
  returns GuidanceResult:    
  - matched_node             ip.subcommands["wifi"]
  - is_executable            True
  - remaining_args           []
      |
      v
  Handler Dispatch           repl.py main loop
  Calls node.handler()       
      |
      v
  Command Handler            ixx/shell/commands/network.py → handle_ip_wifi()
  Calls platform adapter     
      |
      v
  Platform Adapter           ixx/shell/platform/windows.py → get_wifi_ip()
  Runs PowerShell/stdlib      
  internally, returns data   "192.168.1.42"
      |
      v
  Renderer                   ixx/shell/renderer.py
  Formats and prints         "Wi-Fi: 192.168.1.42"
```

**The command registry** (`registry.py`) holds the entire command grammar as a tree of `CommandNode` dataclasses. Each node carries its name, description, subcommands, argument hints, examples, safety flags, and handler. No hardcoded string matching anywhere in the REPL.

**The guidance engine** (`guidance.py`) takes a list of tokens and walks the tree to determine: what matched, what comes next, whether it is executable, and what the remaining arguments are. A node with `executable_with_children=True` (like `ip`, `cpu`) runs its overview handler AND keeps its subcommands available.

**Platform adapters** (`platform/`) isolate all OS-specific code. `windows.py` contains PowerShell and WMIC queries. `linux.py` and `macos.py` are stubs for future releases. Command handlers never contain OS-specific logic — they call adapter functions and render the result.

**The renderer** (`renderer.py`) handles all output. It enables ANSI escape codes on Windows via `SetConsoleMode`. It gracefully falls back to plain text on terminals that do not support colour.

---

### 5.3 Data-driven design

The most important architectural principle: the shell is data-driven, not code-driven.

When you type `find file "invoice"`, the REPL does not contain an `if tokens[0] == "find"` check. It asks the guidance engine, which walks the registry tree and returns what to do. Adding a new command means registering a `CommandNode`. Nothing else changes.

This means:
- Help, fuzzy correction, and guidance work automatically for every command.
- Stub commands have exactly the same guidance/help/correction as live commands.
- Replacing a stub handler with a real one requires changing exactly one field.

---

### 5.4 Key files

```
ixx/
  __main__.py              CLI entry point (ixx run / check / shell / do)
  grammar.lark             IXX language grammar (~70 lines, LALR)
  preprocessor.py          dash → spaces converter
  parser.py                Lark parser config
  ast_nodes.py             typed AST data structures
  build_ast.py             parse tree → AST transformer
  interpreter.py           AST execution engine

  shell/
    repl.py                REPL loop + run_command_once()
    registry.py            CommandNode, CommandRegistry
    guidance.py            get_guidance() engine
    renderer.py            all output formatting
    paths.py               path alias resolution
    safety.py              format_bytes(), render_table()

    commands/
      stubs.py             full command tree: metadata + handler wiring
      hardware.py          cpu, ram handlers
      network.py           ip, network handlers
      system.py            disk handlers
      files.py             folder size, open, list handlers

    platform/
      __init__.py          current() → selects adapter by sys.platform
      common.py            run_command() subprocess helper
      windows.py           all real Windows implementations
      linux.py             stubs for future Linux support
      macos.py             stubs for future macOS support
```

---

## 6. Design philosophy

### Rule 1: The user types the obvious thing

The user should type what they mean. The system figures out the rest.

```
ip wifi                  not:  (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi').IPAddress
folder size downloads    not:  (Get-ChildItem $HOME\Downloads -Recurse | Measure-Object -Sum Length).Sum
cpu core-count           not:  Get-CimInstance Win32_Processor | Select NumberOfCores,NumberOfLogicalProcessors
```

### Rule 2: Readable output, not raw data dumps

```
Wi-Fi: 192.168.1.42
```

not:

```
InterfaceAlias : Wi-Fi
AddressFamily  : IPv4
IPAddress      : 192.168.1.42
PrefixLength   : 24
Type           : Unicast
PrefixOrigin   : Manual
SuffixOrigin   : Manual
AddressState   : Preferred
ValidLifetime  : Infinite
PreferredLifetime : Infinite
SkipAsSource   : False
PolicyStore    : ActiveStore
```

### Rule 3: Errors explain themselves

Syntax errors in `.ixx` scripts show the source line, a caret, and a human explanation:

```
ixx: syntax error in script.ixx line 5
  if age less than
                 ^
  Expected a value after "less than".
  Example:  if age less than 18
```

Shell errors are equally calm:

```
ixx: path not found
  desktop/does-not-exist

Try:
  open desktop
```

### Rule 4: Nothing surprising

- Commands that can delete, move, or stop things are clearly labelled as destructive.
- Destructive commands show a warning in their guidance before you run them.
- No command silently fails. No command crashes with a raw Python traceback.
- If something is not implemented yet, it says so clearly.

### Rule 5: The hard OS-specific stuff hides underneath

The platform adapter layer (`shell/platform/`) means the IXX user never sees a PowerShell command, a WMIC query, a `ctypes` call, or a `subprocess` invocation. Those details are the implementation. The IXX command is the interface.

### Rule 6: Adding a command is adding data

The command tree in `stubs.py` is a set of `CommandNode` declarations. Every node carries its own metadata. Guidance, help, fuzzy correction, and safety warnings are derived automatically. There is no separate "help writer" or "autocomplete handler" — those systems read the same data the handlers use.

---

## 7. Project layout

```
IXX/
├── ixx/
│   ├── __main__.py              CLI entry point
│   ├── grammar.lark             language grammar
│   ├── preprocessor.py          dash → indent converter
│   ├── parser.py                Lark parser
│   ├── ast_nodes.py             AST dataclasses
│   ├── build_ast.py             parse tree transformer
│   ├── interpreter.py           execution engine
│   └── shell/
│       ├── repl.py
│       ├── registry.py
│       ├── guidance.py
│       ├── renderer.py
│       ├── paths.py
│       ├── safety.py
│       ├── commands/
│       │   ├── stubs.py         command tree + handler wiring
│       │   ├── hardware.py
│       │   ├── network.py
│       │   ├── system.py
│       │   └── files.py
│       └── platform/
│           ├── __init__.py
│           ├── common.py
│           ├── windows.py
│           ├── linux.py
│           └── macos.py
│
├── tests/
│   ├── test_ixx.py              98 language tests
│   ├── test_shell.py            54 shell architecture tests
│   └── test_v030.py             66 v0.3.0 tests (paths, formats, handlers, ixx do)
│
├── examples/
│   ├── hello.ixx
│   ├── condition.ixx
│   ├── lists.ixx
│   ├── advanced.ixx
│   └── system-info.ixx
│
├── spec/
│   ├── language.md              full language reference
│   ├── shell.md                 shell design + SSH vision
│   └── roadmap.md               development phases
│
├── docs/
│   └── getting-started.md
│
├── CHANGELOG.md
├── README.md
├── OVERVIEW.md                  this file
└── pyproject.toml
```

---

## 8. Current status and versions

### v0.1.0 — Language prototype (stable, tagged)

The IXX language is working. Scripts run. All language features are implemented and tested.

- `say`, variables, string interpolation
- `if` / `else` with dash blocks
- `loop` with dash blocks
- Nested blocks (up to 3 levels deep)
- Lists and `contains`
- Arithmetic and logic
- `YES` / `NO` booleans
- Comments
- Friendly syntax error messages with source line and caret
- 98 tests passing

### v0.2.0 — Shell skeleton (stable, on `v0.2.0-shell-planning`)

The interactive shell architecture is working. The REPL loop is live. All commands are stubs but the guidance engine, help system, and fuzzy correction all work.

- `ixx` and `ixx shell` open the REPL
- Data-driven `CommandNode` + `CommandRegistry`
- `get_guidance()` engine
- Hint display, help system, fuzzy correction
- 18 commands registered as stubs
- 152 tests passing

### v0.3.0-dev — Real commands (in progress, on `v0.3.0-system-commands`)

First real-usefulness release. Shell commands actually do things.

- 14 live command entries with real Windows implementations
- Platform adapter layer (`shell/platform/`)
- Path alias system (`shell/paths.py`)
- Format helpers: `format_bytes()`, `render_table()`
- `executable_with_children` — parent commands run overview AND show subcommands
- `ixx do "command"` single-dispatch mode
- SSH/server command stubs in the guidance tree
- UTF-8 console output on Windows
- **218 tests passing** (98 language + 54 shell + 66 v0.3.0)

### Implementation note

The current runtime is Python with the Lark parser library. Python is the **prototype vehicle** — it is not the identity of IXX. A future release will ship as a standalone binary compiled from Go, Rust, or a similar language. The Python version will remain as the reference implementation but is clearly labelled as prototype v0.

---

## 9. Long-term vision

IXX's endgame is to be a single command console that covers the useful everyday parts of PowerShell, CMD, Bash, Linux shells, macOS terminal, and SSH administration — all in one consistent syntax, on any machine.

The goal is not to be a scripting language for DevOps pipelines or a replacement for Python in production software. The goal is to give everyone — not just developers — a single, calm interface for every task they actually do on a computer every day: check what's using RAM, find a file, see the IP, copy something, manage a disk, reach a remote server.

IXX should be the thing you open instead of Google-searching "how do I check disk space in PowerShell."

### Command categories — near term

**System info** (partial in v0.3.x)
```
cpu    ram    gpu    disk    disk health    temps    uptime
```

**Network** (partial in v0.3.x)
```
ip    ip wifi    ethernet    network    ports    wifi
```

**Processes**
```
processes    kill process chrome
```

**Files** (partial in v0.3.x)
```
list    open    folder size    find file
copy report.pdf to desktop
move old-folder to archive
delete folder temp recursive
```

**Services and system**
```
services    restart service nginx
logs    tail logs nginx
```

**Remote / SSH** (stubs in v0.3.x, implementation planned v0.5.0+)
```
ssh user@192.168.1.50
ssh my-server

run on my-server "disk space"
run on my-server "cpu"

copy report.pdf to my-server:/home/user/
copy my-server:/var/log/syslog to downloads

servers
server add my-server
```

Remote commands use the same IXX syntax as local ones. The prompt makes the target obvious:

```
ixx>                   local
ixx my-server>         connected remote shell
```

### Language evolution

IXX the language will grow alongside the shell. Functions are the next major language feature (v0.4.0), enabling reusable logic, parameterised scripts, and eventually callable shell macros.

After functions: modules, standard library integration, and the ability to author IXX scripts that feel like real programs rather than one-off notes.

### Staged roadmap

| Version | Theme                        | Key additions                                              |
|---------|------------------------------|------------------------------------------------------------|
| v0.1.0  | Language prototype           | IXX language, syntax, interpreter, 98 tests               |
| v0.2.0  | Shell skeleton               | REPL, guidance, fuzzy correction, stub commands            |
| v0.3.x  | First real commands          | ip, cpu, ram, disk, folder, open, list, aliases, ethernet  |
| v0.4.0  | Functions + files            | IXX functions, copy/move, find file, processes, ports      |
| v0.5.0  | Remote access                | SSH profiles, run on server, saved targets                 |
| v0.6.0+ | Services, packages, scripting| systemctl/services, logs, docker helpers, repair tools     |

### The standalone binary

The Python prototype will eventually be replaced by a compiled binary. Likely candidates: **Go** (fastest to ship, good cross-platform), **Rust** (best long-term quality and performance). The binary ships as a single file with no dependencies.

The goal is `ixx` works out of the box on any machine, with no Python, no Lark, no pip install required.

---

## 10. What IXX is not

- **Not just an everyday helper.** IXX is aiming to be a full replacement command layer. The goal is not a better `ipconfig` wrapper — it is a consistent shell that makes the relevant parts of every shell redundant for everyday use.

- **Not trying to clone every advanced use case.** For production-scale software, complex algorithms, or deep OS scripting, Python, Go, and Rust are still the right tools. IXX's constraint is readability: it handles the things where readability matters most.

- **Not a Bash replacement for DevOps pipelines.** IXX does not aim to replace CI automation, complex pipe chains, or deeply Unix-flavoured shell scripting. It aims to replace the parts of those tools that normal users reach for daily.

- **Not a configuration language.** IXX is imperative — logic and commands — not declarative config.

- **Not trying to have the most features.** The design constraint is to stay readable. If a feature makes the language harder to read at a glance, it does not belong in the core.

- **Not trying to be clever.** No magic inference, no implicit type coercion weirdness, no surprising operator overloading. IXX does what it says.

---

## The one-sentence version

IXX is a replacement command layer — readable scripts, readable shell, one syntax, every machine.
