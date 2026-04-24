# IXX

IXX is a replacement command layer — readable scripts, readable shell, one syntax, every machine.

It is two things in one package:

- **A small language** that looks like a checklist. Plain English comparisons, visible dash blocks, no braces, no indentation rules.
- **An interactive shell** that replaces the everyday parts of PowerShell, CMD, Bash, and macOS Terminal with a single consistent syntax.

```
age = 19

if age less than 18
- say "Not adult"
else
- say "Adult"
```

```
ixx> ip wifi
  Wi-Fi: 192.168.1.42

ixx> memory used
  Used:  15.5 GB  (50%)

ixx> downloads size
  downloads: 14.2 GB
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
ixx> disk partitions
ixx> folder size downloads
  downloads: 14.2 GB

ixx> open desktop
  Opened: C:\Users\you\Desktop

ixx> list downloads

ixx> gpu
  GPU:     NVIDIA GeForce RTX 4070 SUPER
  VRAM:    12.0 GB
  Driver:  32.0.15.8157

ixx> gpu vram
ixx> cpu temperature
ixx> cpu speed
ixx> cpu info
ixx> ram free
ixx> ram speed
ixx> wifi
  Network:  MyNetwork
  Signal:   90%
  IP:       192.168.1.42

ixx> ip public
  Public IP:  203.0.113.5
  (via external lookup: api.ipify.org)

ixx> ports
ixx> processes
ixx> find file "*.pdf" in downloads
```

Single-command mode (useful for scripts and automation):

```
ixx do "ip"
ixx do "cpu core-count"
ixx do "gpu"
ixx do "folder size downloads"
ixx do "find file *.pdf in downloads"
```

Notes:
- v0.3.x is Windows-first for real system commands.
- Cross-platform adapters (Linux, macOS) are planned for a future release.
- Destructive commands (`delete`, `kill process`, `copy`, `move`) are still stubbed for safety.
- The Python implementation is prototype v0 — not the final runtime.

IXX also understands natural synonyms — you do not have to spell out the canonical command:

```
ixx> memory used          → same as: ram usage
ixx> processor cores      → same as: cpu core-count
ixx> wifi address         → same as: ip wifi
ixx> downloads size       → same as: folder size downloads
ixx> storage              → same as: disk
```

---

## File extension

IXX source files use the `.ixx` extension.

```
hello.ixx
system-info.ixx
deploy-checklist.ixx
```

> **Note:** `.ixx` is also used by C++20 module interface files. Some editors
> may misdetect `.ixx` as C++. Install the editor support below to override
> this association.

---

## Editor support

IXX ships with syntax highlighting for VS Code and Notepad++, plus a Windows
file icon.

### VS Code

The `editor/vscode/` folder contains a VS Code language extension that:

- Registers `.ixx` as **IXX** (overriding C++ detection)
- Highlights comments, strings, keywords, booleans, numbers, and operators
- Highlights string interpolation (`{name}` inside double-quoted strings)
- Configures `#` as the line comment character

See [`editor/vscode/README.md`](editor/vscode/README.md) for installation
instructions.

### Notepad++

The `editor/notepad-plus-plus/` folder contains a User Defined Language (UDL)
XML for Notepad++ that highlights `.ixx` files with the same colour scheme.

See [`editor/notepad-plus-plus/README.md`](editor/notepad-plus-plus/README.md)
for step-by-step installation instructions.

### Windows file icon

The IXX icon asset lives in `assets/`:

```
assets/
  ixx-icon-source.png       source image (673×673)
  generate_icons.py         generates all sizes automatically
  generated/
    ixx-icon-16.png
    ixx-icon-24.png
    ixx-icon-32.png
    ixx-icon-48.png
    ixx-icon-64.png
    ixx-icon-128.png
    ixx-icon-256.png
    ixx-icon.ico             multi-size Windows icon
```

To generate the icons (requires Pillow):

```
pip install Pillow
python assets/generate_icons.py
```

To associate `.ixx` files with the IXX icon on Windows, see
[`editor/windows/file-association.md`](editor/windows/file-association.md).

> **SVG note:** SVG output is intentionally skipped — converting a raster PNG
> to SVG would embed the bitmap data rather than produce a true vector image.
> PNG and ICO are the canonical IXX icon formats.

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

**282 tests passing** across: language basics, strings, numbers, booleans, conditions, dash blocks, loops, lists, comparisons, `contains`, logic, error handling, CLI commands, shell guidance, command handlers, path aliases, format helpers, banner, and new system commands.

---

## Project layout

```
ixx/            prototype interpreter (Python)
examples/       example .ixx scripts
spec/           language spec, shell design, roadmap
docs/           getting started guide
tests/          automated tests
assets/         icon source and generate_icons.py script
  generated/    generated PNG sizes and ixx-icon.ico
editor/         syntax highlighting and file association
  vscode/       VS Code language extension
  notepad-plus-plus/  Notepad++ User Defined Language
  windows/      Windows file association documentation
CHANGELOG.md    version history
```

---

## More

- [`spec/language.md`](spec/language.md) — full language reference
- [`spec/shell.md`](spec/shell.md) — planned interactive shell design
- [`spec/roadmap.md`](spec/roadmap.md) — where IXX is going
- [`docs/getting-started.md`](docs/getting-started.md) — step by step setup
- [`editor/vscode/README.md`](editor/vscode/README.md) — VS Code extension
- [`editor/notepad-plus-plus/README.md`](editor/notepad-plus-plus/README.md) — Notepad++ UDL
- [`editor/windows/file-association.md`](editor/windows/file-association.md) — Windows file icon and association
