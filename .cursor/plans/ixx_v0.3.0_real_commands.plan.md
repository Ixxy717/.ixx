---
name: IXX v0.3.0 Real Commands
overview: "First real-usefulness release. Implement 13 read-only/safe shell commands for Windows, a path alias system, platform adapters, format helpers, ixx do CLI command, guidance model update for executable-parent nodes, and a full test suite. No destructive commands. SSH/server stubs only."
todos:
  - id: branch
    content: Create branch v0.3.0-system-commands
    status: pending
  - id: registry
    content: "registry.py: add executable_with_children field to CommandNode"
    status: pending
  - id: guidance
    content: "guidance.py: update executability rule to respect executable_with_children"
    status: pending
  - id: paths
    content: "Create ixx/shell/paths.py: path alias resolution"
    status: pending
  - id: safety
    content: "Create ixx/shell/safety.py: format_bytes() and render_table()"
    status: pending
  - id: platform
    content: "Create ixx/shell/platform/: __init__, common, windows, linux, macos"
    status: pending
  - id: commands
    content: "Create commands/hardware.py (cpu, ram), network.py (ip, network), files.py (folder, open, list), system.py (disk)"
    status: pending
  - id: wire
    content: "Wire real handlers into stubs.py; update remaining stub messages to v0.4.0; add ssh/servers/server stubs"
    status: pending
  - id: repl
    content: "repl.py: add run_command_once(); add UTF-8 stdout fix for Windows"
    status: pending
  - id: cli
    content: "__main__.py: version 0.3.0-dev, add ixx do command"
    status: pending
  - id: tests
    content: "Create tests/test_v030.py covering paths, formats, guidance, handlers, ixx do"
    status: pending
  - id: docs
    content: "Update CHANGELOG, README, spec/roadmap.md, spec/shell.md"
    status: pending
isProject: false
---

# IXX v0.3.0 Real Commands

Branch: `v0.3.0-system-commands` from `v0.2.0-shell-planning`.
`master` stays at v0.1.0 until a stable merge is tagged.

---

## New file layout

```
ixx/shell/
  platform/
    __init__.py      current() helper — returns the right adapter
    common.py        shared helpers (run_command, safe_run)
    windows.py       all Windows-specific implementations
    linux.py         stub placeholders
    macos.py         stub placeholders
  commands/
    __init__.py      (existing)
    stubs.py         (existing — real handlers removed for commands going live)
    hardware.py      cpu, ram handlers
    network.py       ip, network handlers
    files.py         folder size, open, list handlers
    system.py        disk handlers
  paths.py           path alias resolution
  safety.py          format_bytes(), render_table()
  registry.py        add executable_with_children field
  guidance.py        handle executable_with_children
  repl.py            add run_command_once(); UTF-8 fix
  renderer.py        no changes needed
```

---

## 1. Registry — `executable_with_children` field

Add one field to `CommandNode` in `ixx/shell/registry.py`:

```python
executable_with_children: bool = False
# When True, typing the command alone executes it AND subcommands remain available.
# ip, cpu, ram, disk, network get this flag.
```

---

## 2. Guidance engine update — `ixx/shell/guidance.py`

Current rule (v0.2.0): nodes with subcommands are never executable alone.
New rule: nodes where `executable_with_children=True` ARE executable alone
AND keep their subcommand options visible.

```python
executable = (
    (has_handler or has_arg_hint)
    and (not bool(node.subcommands) or node.executable_with_children)
)
```

`ip ?` / `cpu ?` — already handled by `tokens[-1] == "?"` in `repl.py`
routing to `_handle_help`. No change needed to guidance for `?` queries.

---

## 3. Path aliases — `ixx/shell/paths.py` (new)

```python
ALIASES = {
    "desktop":   Path.home() / "Desktop",
    "downloads": Path.home() / "Downloads",
    "documents": Path.home() / "Documents",
    "pictures":  Path.home() / "Pictures",
    "music":     Path.home() / "Music",
    "videos":    Path.home() / "Videos",
    "home":      Path.home(),
    "temp":      Path(tempfile.gettempdir()),
    "appdata":   Path(os.environ.get("APPDATA", str(Path.home()))),
    "here":      Path.cwd(),
    "current":   Path.cwd(),
    ".":         Path.cwd(),
}

class PathNotFoundError(Exception):
    pass

def resolve(raw: str) -> Path:
    """Resolve alias or forward-slash path to an absolute Path.
    Raises PathNotFoundError with friendly message if result doesn't exist.
    """
```

`folder size downloads/projects` — split on first `/`, resolve alias, append rest.

---

## 4. Format helpers — `ixx/shell/safety.py` (new)

```python
def format_bytes(n: int) -> str:
    """512 B / 1.2 KB / 842 MB / 14.2 GB / 2.0 TB"""

def render_table(headers: list[str], rows: list[list[str]],
                 *, min_col_width: int = 4) -> str:
    """Return a plain-text aligned table string. Missing values show as -."""
```

---

## 5. Platform adapters

### `ixx/shell/platform/__init__.py`

```python
import sys

def current():
    if sys.platform == "win32":
        from . import windows; return windows
    if sys.platform == "darwin":
        from . import macos; return macos
    from . import linux; return linux
```

### `ixx/shell/platform/common.py`

```python
def run_command(cmd: list[str], timeout: int = 10) -> str:
    """Run subprocess, return stdout, never raise — return '' on error."""
```

### `ixx/shell/platform/windows.py` — real implementations

Uses `subprocess` + PowerShell/WMIC internally. User never sees it.

```python
def get_ip_info() -> list[dict]:      # [{adapter, ipv4, status, gateway}]
def get_wifi_ip() -> str | None
def get_ethernet_ip() -> str | None

def get_cpu_info() -> dict:           # {name, cores, threads, usage_pct}
def get_cpu_core_count() -> dict:     # {name, cores, threads}

def get_ram_info() -> dict:           # {total_bytes, used_bytes, free_bytes}

def get_disk_info() -> list[dict]:    # [{drive, label, total_bytes, free_bytes}]
```

### `ixx/shell/platform/linux.py` and `macos.py`

Stub each function:

```python
def get_ip_info():
    raise NotImplementedError("not yet available on this platform")
```

Command handlers catch `NotImplementedError` and print:
`[<command> — not yet available on this platform]`

---

## 6. Command handlers

### `ixx/shell/commands/network.py`

```python
def handle_ip(args)           # table: Adapter | IPv4, skip loopback
def handle_ip_wifi(args)      # "Wi-Fi: x.x.x.x" or friendly no-adapter msg
def handle_ip_ethernet(args)
def handle_ip_local(args)     # all private IPs
def handle_network(args)      # table: Adapter | Status | IPv4 | Gateway
```

### `ixx/shell/commands/hardware.py`

```python
def handle_cpu(args)          # CPU: name / Cores: N / Threads: N / Usage: N%
def handle_cpu_cores(args)    # name + cores/threads only
def handle_ram(args)          # Total: N GB / Used: N GB / Free: N GB
```

### `ixx/shell/commands/system.py`

```python
def handle_disk(args)         # table: Drive | Total | Free
def handle_disk_space(args)   # same + Percent used column
```

### `ixx/shell/commands/files.py`

```python
def handle_folder_size(args)  # resolve alias, walk recursively, format_bytes
def handle_open(args)         # resolve alias, os.startfile
def handle_list(args)         # resolve alias, table: Name | Type | Size
```

#### Quoted path handling in `folder size`, `open`, `list`

The REPL tokenizer (`_tokenize`) already strips quotes from individual tokens.
Command handlers receive `args` as a list of strings. For these three commands,
the handler joins all args back into a single path string before resolving:

```python
raw_path = " ".join(args) if args else ""
path = paths.resolve(raw_path)
```

This supports all four forms without special-casing in the REPL:

```
folder size downloads              → args = ["downloads"]
folder size "desktop/my folder"    → args = ["desktop/my folder"]
open "desktop/my folder"           → args = ["desktop/my folder"]
list "documents/school stuff"      → args = ["documents/school stuff"]
```

The tokenizer's quote-stripping ensures the surrounding quotes are removed
before the handler sees the string.

---

## 7. Wire real handlers into stubs — `ixx/shell/commands/stubs.py`

For each command going live, replace `handler=_stub("...")` with the real handler.

Commands going live (14 live command entries):
`ip`, `ip all`, `ip wifi`, `ip ethernet`, `ip local`, `network`,
`cpu`, `cpu core-count`, `ram`, `disk`, `disk space`,
`folder size`, `open`, `list`

Note: `ip all` is a distinct registry entry (same behavior as bare `ip`) rather than an alias.
Counting it separately gives 14 entries. The "13 commands" framing from earlier docs was off by one.

Set `executable_with_children=True` on: `ip`, `cpu`, `ram`, `disk`, `network`

Commands staying as stubs — update message to say `"coming in v0.4.0"`:
`cpu temperature`, `cpu speed`, `cpu info`, `ram speed`, `gpu`,
`disk health`, `disk partitions`, `ports`, `processes`, `kill process`,
`copy`, `move`, `delete *`, `find file`

Commands staying as stubs permanently for this release (no real implementation):
`native`, `ssh`, `server`, `servers` — stub-only, no passthrough or SSH execution.

New SSH/server stub nodes added:
- `ssh` — `arg_hint="<user@host or saved-server>"`, stub
- `servers` — leaf stub
- `server` — subcommands: `add` (stub), `list` (stub)

Stub message for all remaining: `[<cmd> — not yet implemented, planned for a future release]`

---

## 8. `repl.py` — `run_command_once()` + Unicode fix

```python
def run_command_once(line: str) -> None:
    """Build registry, dispatch one command, exit. Used by ixx do."""
    registry = _make_registry()
    tokens = _tokenize(line.strip())
    if not tokens:
        return
    # same dispatch logic as the main loop, no banner
```

UTF-8 stdout for Windows — add at top of `run()` and `run_command_once()`:

```python
if sys.platform == "win32":
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass
```

---

## 9. `ixx/__main__.py`

- `VERSION = "0.3.0-dev"`
- Add `"do"` to `_KNOWN_COMMANDS`
- Add `ixx do "command"` to `HELP_TEXT`
- Add handler block:

```python
if cmd == "do":
    if len(args) < 2:
        print("ixx: 'do' requires a command.  Example: ixx do \"ip wifi\"")
        sys.exit(1)
    from .shell.repl import run_command_once
    run_command_once(" ".join(args[1:]))
    return
```

`" ".join(args[1:])` means both invocation styles work identically:

```
ixx do "ip wifi"      → args[1:] = ["ip wifi"]         → "ip wifi"
ixx do ip wifi        → args[1:] = ["ip", "wifi"]       → "ip wifi"
```

---

## 10. Tests — `tests/test_v030.py` (new, existing tests untouched)

```
TestPaths
  test_resolve_desktop, test_resolve_downloads, test_resolve_home
  test_resolve_here, test_resolve_dot
  test_resolve_subpath (desktop/somefolder)
  test_unknown_alias_raises_PathNotFoundError

TestFormatBytes
  test_bytes, test_kb, test_mb, test_gb, test_tb, test_zero

TestRenderTable
  test_column_alignment, test_missing_value_shown_as_dash

TestGuidanceExecutableWithChildren
  test_ip_is_executable_alone
  test_ip_wifi_is_executable
  test_ip_shows_subcommands_in_next_options
  test_cpu_is_executable_alone
  test_cpu_core_count_is_executable

TestCommandHandlers (mock platform.current())
  test_ip_no_crash
  test_ip_wifi_no_adapter_message
  test_cpu_no_crash
  test_ram_no_crash
  test_disk_no_crash
  test_folder_size_on_tempdir
  test_list_on_tempdir
  test_open_mocked (mock os.startfile)

TestReplDo
  test_run_command_once_does_not_raise
  test_ixx_do_via_subprocess
```

---

## 11. Documentation

Light touch — no wholesale rewrites:

- `CHANGELOG.md` — add `[0.3.0-dev]` section
- `README.md` — add "IXX Shell examples" section with `ip`, `cpu`, etc.
- `spec/roadmap.md` — Phase 3 "in progress", sketch v0.4.0–v0.6.0 stages
- `spec/shell.md` — add SSH / remote administration vision section

---

## Definition of done

- `ixx` opens shell
- `ixx version` → `0.3.0-dev`
- `ixx do "ip"` prints IP info and exits
- Inside shell: all 14 live command entries return real output on Windows
- Leaf stubs say "planned for a future release"
- Existing 152 tests still pass
- New v0.3.0 tests pass
- No destructive command actually executes
