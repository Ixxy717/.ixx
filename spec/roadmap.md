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
- **`command help` / `command ?`** — trailing help keyword supported
- **Fuzzy correction** — unknown commands suggest closest match
- **Guidance system** — fully data-driven via `CommandNode`, no hardcoded behavior

Still stubbed (planned for v0.4.0+):
- `kill process`, `ports`, `processes` — process management
- `copy`, `move`, `delete` — file operations
- `find file` — file search
- `native` — passthrough
- `ssh`, `server`, `servers` — remote access

> **Terminal UI note:** Full inline live completions (cursor movement, colored
> suggestion menus, prompt rendering) are intentionally deferred. The current
> readline-based REPL with data-driven guidance is sufficient for v0.3/v0.4.
> The future standalone IXX terminal app (v1.x) is the right home for a custom TUI.

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

/ixx
  (Phase 0-0.x: Python prototype package)
  grammar.lark
  parser.py
  interpreter.py
  __main__.py
  shell/
    repl.py
    registry.py
    guidance.py
    renderer.py
    paths.py
    safety.py
    commands/
    platform/

/runtime
  (Phase 1+: compiled runtime in Rust/Go/Zig/C#)

/stdlib
  (Phase 4: standard library modules)

/tests
  test_ixx.py         language and CLI tests
  test_shell.py       shell guidance/registry tests
  test_v030.py        v0.3.0 command handler/path tests

/docs
  getting-started.md
  command-reference.md
```

---

## What IXX is not trying to be

- Not a full replacement for Python, JavaScript, or Rust for complex software.
- Not a general-purpose systems language.
- Not trying to have the most features.
- Not just a helper wrapper around existing commands — the endgame is a full replacement command layer for everyday system interaction across every OS.

IXX is trying to be the thing people open instead of memorising the differences between PowerShell, CMD, Bash, and macOS Terminal for the things they do every day.

---

## Functions — v0.4.0

Functions are the next major IXX language feature. They are deliberately held to v0.4.0 because they require grammar changes, interpreter changes, and a scoping model that does not exist yet.

### Planned syntax

```
define greet name
- say "Hello, {name}"

greet "Ixxy"
```

Or with return values:

```
define add a b
- result = a + b
- return result

total = add 10 20
say total
```

### Why not now

- The current interpreter has no call stack or return mechanism.
- The grammar has no `define` or `return` keyword yet.
- The scoping model (outer-scope modification vs. local) needs extending.

Functions are a `v0.4.0` milestone. All other v0.3.x improvements come first.

---

## Command normalization — v0.3.x (completed)

IXX now accepts natural language variants and phrase synonyms for commands without requiring exact canonical spelling.

Two layers:

**Root aliases** — single-token synonyms at the root level:
- `memory` → `ram`
- `processor` → `cpu`
- `storage` / `drive` / `drives` → `disk`

**Phrase aliases** — multi-word patterns:
- `memory used` → `ram usage`
- `wifi ip` → `ip wifi`
- `wifi address` → `ip wifi`
- `downloads size` → `folder size downloads`
- and more

**Protected commands** — never silently rerouted:
- `delete`, `kill`, `copy`, `move`, `native`, `ssh`, `server`, `servers`

Alias-aware help: `help ram` now shows "Also accepts: memory" and subcommands show their alternate names in parentheses.

---

## Future: disk commands — diskpart-style read-only interface

The goal is a read-only disk inspection workflow that feels like `diskpart` without requiring `diskpart` or admin rights.

### Planned commands

```
disk list                   List all physical disks (name, size, type, health)
disk health                 Per-disk health status from Get-PhysicalDisk
disk smart                  Predictive failure flag + basic SMART status (WMI)
disk smart full             Full SMART attribute table (requires admin)
disk select <n>             Select a disk by index for subsequent commands
disk detail                 Show details for the selected disk
disk partitions             Partition table for the selected disk (already live for all disks)
disk speed                  Sequential read/write benchmark (non-destructive)
```

### Implementation notes

- `disk list`, `disk health`, `disk smart` (basic): implementable now with `Get-PhysicalDisk` — no admin required
- `disk smart full`: needs WMI `MSStorageDriver_FailurePredictData` — admin required, deferred
- `disk select` / `disk detail`: requires **stateful session** — the shell must remember a selected disk index across commands. This is a new architectural concept for the IXX shell (no stateful context exists yet). Design and implement the session context layer first.
- `disk speed`: non-destructive read benchmark is feasible; write benchmark is risky — destructive flag required

### Stateful session design (required for `disk select`)

The shell currently has no concept of session state between commands. A `SessionContext` object would need to be threaded through the shell loop and passed to handlers. Design considerations:

- `context["selected_disk"]` — index or name
- Commands that require a selection should check context and print a clear error if nothing is selected
- `disk deselect` or `disk reset` to clear selection
- Context is in-memory only — not persisted across shell restarts

---

## Future: update checking (doc only — not yet implemented)

When IXX starts interactively, it may optionally check whether a newer version
is available.

### Behavior

- If the installed version is current: show nothing
- If a newer stable version exists, show a small non-intrusive line below the banner:

  ```
  Version 0.4.0 available.  Run "update" to get the latest version.
  ```

Rules:
- Do not block or slow down shell startup
- Use a background thread or cached result — do not hold the prompt
- Cache the last check timestamp; do not re-check on every launch
- Allow the user to disable update checks entirely
- Never auto-update without explicit user action
- No banner for `ixx do`, scripts, or non-interactive invocations

### Future commands (stubs only for now)

```
update                     Update to the latest stable version
update check               Manually check for updates now
update latest              Install the latest stable version
update version 0.4.0       Install/switch to a specific version

version available          Show available versions
```

### Future configuration

```
IXX_NO_UPDATE_CHECK=1                   environment variable disable
ixx config update-check off             config file disable
ixx config update-channel stable|dev    release channel
```
