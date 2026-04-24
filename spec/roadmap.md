# IXX Roadmap

This document tracks the phases of IXX development from the current Python prototype toward a standalone runtime and shell.

---

## Phase 0 — Python prototype (current)

**Status:** active

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

**Goal:** `ixx shell` opens a working interactive console.

What Phase 2 adds:
- `ixx shell` / `ixx repl` opens an interactive prompt.
- Type IXX commands and expressions, see results immediately.
- Command history (up arrow, search).
- Live grammar-aware command guidance (see spec/shell.md).
- Fuzzy correction for mistyped commands.
- Basic help system (`help`, `? command`, `command ?`).

The guidance engine (`/shell/command-guidance/`) is the core investment of this phase. It must be structured as a data-driven grammar tree, not hardcoded string matching.

---

## Phase 3 — Built-in system commands

**Goal:** Common system tasks work out of the box.

What Phase 3 adds (see spec/shell.md for full list):
- `cpu`, `ram`, `gpu`, `disk` — hardware info
- `ip`, `wifi`, `network`, `ports` — network info
- `processes`, `kill process` — process management
- `folder size`, `find file`, `open`, `list` — file exploration
- `copy`, `move`, `delete` — file operations with safety prompts
- `delete temp`, `delete empty-trash` — cleanup
- Path aliases: `desktop`, `downloads`, `home`, `here`, etc.
- Native passthrough: `native "..."`, `ps "..."`, `cmd "..."`, `sh "..."`

Platform priority: Windows first (PowerShell/CMD replacement use case), then macOS, then Linux.

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
