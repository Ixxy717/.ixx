# IXX Roadmap

This document tracks the phases of IXX development from the current Python prototype toward a standalone runtime and shell.

---

## Phase 0 — Python prototype

**Status:** complete (tagged v0.1.0)

The IXX interpreter is written in Python using the Lark parser library.

This phase proves the grammar, syntax, and interpreter design without the overhead of building a compiler or runtime from scratch.

Python is the implementation language for this phase only. It is not the identity of IXX.

What exists in Phase 0:
- `ixx/grammar.lark` — the IXX grammar
- `ixx/parser.py` — Lark-based parser
- `ixx/interpreter.py` — tree-walking interpreter
- `ixx/__main__.py` — CLI: `ixx run`, `ixx check`, `ixx version`, `ixx help`
- `examples/` — working example scripts
- `spec/` — language, shell, and roadmap specifications

Limitations:
- Requires Python 3.11+ and the Lark library to be installed.
- No interactive shell or REPL.
- No built-in system commands.
- No standalone executable.

---

## Phase 1 — Language complete + standalone CLI

**Goal:** IXX runs as a standalone binary with no Python dependency.

Two paths forward, both valid:

### Path A: PyInstaller bundle

Bundle the Python interpreter + IXX runtime into a single `ixx.exe` using PyInstaller.

Pros: fast to ship, same codebase.
Cons: large binary (~10-20 MB), slower startup.

Good for: shipping a working prototype to people who don't have Python.

### Path B: Rewrite in a compiled language

Rewrite the IXX interpreter in Rust, Go, Zig, or C# (native AOT).

**Rust** — best long-term choice. Fast, safe, great tooling, good cross-platform support. Steeper learning curve.

**Go** — fast to write, excellent CLI tooling, easy cross-compilation. Slightly larger binaries.

**Zig** — minimal, extremely fast binaries. Very low-level, less ecosystem.

**C# native AOT** — familiar if coming from .NET. Good Windows integration. AOT compilation produces small fast binaries.

Recommended for Phase 1: **Go** for fastest iteration, **Rust** for long-term quality.

What Phase 1 adds:
- Standalone `ixx` binary with no external dependencies.
- `ixx run`, `ixx check`, `ixx version`, `ixx help` work out of the box.
- Language feature complete (all spec/language.md features working).

---

## Phase 2 — Interactive shell and REPL

**Status:** complete (branch: `v0.2.0-shell-planning`)

What Phase 2 added:
- `ixx shell` / `ixx` opens an interactive prompt
- Command history, fuzzy correction, help system
- Data-driven `CommandNode` / `CommandRegistry` guidance tree
- All shell commands registered as stubs with metadata

---

## Phase 3 — Built-in system commands

**Status:** in progress (branch: `v0.3.0-system-commands`)

First real-usefulness release. 14 command entries go live on Windows.

What Phase 3 adds:

- **Live commands:** `ip`, `ip wifi/ethernet/local`, `network`, `cpu`,
  `cpu core-count`, `ram`, `disk`, `disk space`, `folder size`, `open`, `list`
- **Platform adapter layer** (`shell/platform/`) — Windows real, Linux/macOS stubs
- **Path alias system** (`shell/paths.py`) — `desktop`, `downloads`, `home`, `here`, etc.
- **Format helpers** (`shell/safety.py`) — `format_bytes()`, `render_table()`
- **`ixx do "command"`** — single-dispatch CLI mode
- **`executable_with_children`** — parent commands execute overview AND show subcommands
- **SSH/server command stubs** — in tree for guidance, no execution yet

Still stubbed (planned for v0.4.0+):
- `kill process`, `ports`, `processes` — process management
- `copy`, `move`, `delete` — file operations
- `find file` — file search
- `native` — passthrough
- `ssh`, `server`, `servers` — remote access

---

## Phase 4 — Standard library and scripting power

**Goal:** IXX can write real useful scripts.

What Phase 4 adds:
- Functions / procedures
- More data types (maps/dicts, sets)
- File I/O: read file, write file, append file
- HTTP: fetch url
- Date and time
- Error handling
- Importing other `.ixx` files
- A standard library (`stdlib/`) for common tasks

---

## Project structure (long-term)

```
/spec
  language.md         IXX language specification
  shell.md            IXX shell and console design
  roadmap.md          this file

/examples
  hello.ixx
  condition.ixx
  lists.ixx
  advanced.ixx
  system-info.ixx
  files.ixx

/runtime
  (Phase 0: Python prototype — ixx/ package)
  (Phase 1+: compiled runtime in Rust/Go/Zig/C#)

/shell
  repl/
  command-guidance/
  autocomplete/
  history/
  rendering/

/stdlib
  (Phase 4: standard library modules)

/tests
  language/
  commands/
  paths/
  safety/

/docs
  getting-started.md
  command-reference.md
```

---

## What IXX is not trying to be

- Not a full replacement for Python, JavaScript, or Rust for complex software.
- Not a general-purpose systems language.
- Not trying to have the most features.

IXX is trying to be the easiest way to tell the computer what to do for the things people do every day.
