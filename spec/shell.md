# IXX Shell Design Specification

This document describes the design of the IXX interactive shell and console.

---

## Identity

The IXX shell should replace the annoying parts of PowerShell, CMD, Bash, and WSL for everyday tasks.

Not because those tools are wrong. Because they require too much memorization for common things.

Compare:

```powershell
(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias 'Wi-Fi').IPAddress
```

vs.

```
ip wifi
```

Both return the same result. The second is IXX.

```powershell
Get-ChildItem -Path ".\TargetFolder" -Recurse -Force | Remove-Item -Force -Recurse
```

vs.

```
delete folder TargetFolder recursive
```

The shell should just work.

---

## Goals

- Works on Windows, macOS, and Linux where possible.
- Feels the same across platforms.
- Simple commands for common everyday tasks.
- Hides OS-specific complexity.
- Allows native passthrough when needed.
- Useful interactively and in scripts.
- Uses the same language style as `.ixx` scripts.
- Does not require users to know PowerShell pipelines, CMD flags, Bash syntax, or WSL.

---

## CLI entry points

```
ixx                    open the IXX interactive shell
ixx shell              open the IXX shell explicitly
ixx run script.ixx     run a script
ixx do "cpu"           run a single IXX command inline
ixx version            print version
ixx help               print help
ixx check file.ixx     check syntax without running
ixx fmt file.ixx       format a file (planned)
ixx repl               open the language REPL (planned)
```

---

## Live grammar-aware command guidance

This is a first-class design goal, not a bonus feature.

When the user types a command, the shell understands the current partial input and shows what valid arguments can come next. This is not dumb autocomplete. It is grammar-aware guidance.

### What is implemented

The current REPL provides:

- **`command ?`** — show valid next options for any command
- **`help command`** — show full help, subcommands, examples, and safety notes
- **`command help`** — same as above (trailing keyword)
- **`? command`** — same as above (leading ?)
- **Hint display** — when a partial command is entered (e.g. `delete`), the shell shows its subcommands and examples automatically
- **Fuzzy correction** — unknown commands suggest the closest match
- **Argument hints** — commands that take a free-form argument (e.g. `folder size <path>`) display their hint in the guidance output
- **`ixx do "command"`** — single-dispatch mode for scripts and automation

All of this is data-driven from the `CommandNode` tree. Adding a new command gives it guidance, help, and fuzzy correction automatically.

### Help command examples

```
help                  broad list of all commands
help disk             disk commands, subcommands, examples
help delete           delete syntax, examples, safety notes
? disk                same as help disk
disk ?                valid next options for disk
disk help             same as disk ?
delete ?              valid next options for delete
```

### Fuzzy correction

If the user types something close but wrong:

```
ixx> cpoy
  Unknown command: cpoy
  Did you mean: copy?

ixx> diks
  Unknown command: diks
  Did you mean: disk?
```

---

## Terminal UI boundary

The current REPL is deliberately simple. It uses standard `input()` with optional readline history. This is intentional.

### What the current shell does — and keeps doing

- Guidance via `?`, `help`, trailing `help` keyword
- Hint display when partial commands are entered
- Fuzzy correction for mistyped commands
- Command history via readline / pyreadline3
- Basic Tab completion via readline if easy to wire without custom rendering

### What belongs to the future IXX terminal app

Full inline live completions require control over:

- Input rendering (overwriting the current line as you type)
- Cursor movement (moving between suggestion items)
- Colored inline menus (rendering completions beside or below the cursor)
- Multi-line editing
- Proper resize handling

These need a library like `prompt_toolkit` or a fully custom TUI, and they need
the standalone compiled binary where input handling can be owned end-to-end.

**Do not build this in the Python prototype.** The guidance system works well without it.
The future IXX terminal app (standalone binary, v1.x) is the right home for full
inline completions.

### What this means in practice

| Feature | Current REPL | Future TUI |
|---|---|---|
| `?` / `help` guidance | done | carry forward |
| `cmd help` trailing keyword | done | carry forward |
| Fuzzy correction | done | carry forward |
| Argument hints in output | done | carry forward |
| readline history | done | replace |
| Basic Tab (readline) | acceptable if simple | replace |
| Inline live completions | not here | future TUI |
| Colored suggestion menus | not here | future TUI |
| Cursor movement in hints | not here | future TUI |

The rule: **guidance lives in the data (CommandNode). Display is replaceable.**
When the terminal app is built, it reads the same registry and renders richer output.
Nothing in the guidance engine needs to change.

---

## Built-in system commands

### Hardware info

```
cpu                   CPU name, usage, cores, threads, speed, temperature
cpu usage             current usage percentage
cpu core-count        core and thread count
cpu temperature       temperature if available

ram                   total, used, free, speed
ram free              free RAM
ram usage             usage percentage

gpu                   GPU name, VRAM, usage, driver

disk                  list all disks
disk list             list all disks
disk health           health / SMART info
disk space            used and free space
disk partitions       partition table
```

### Network

```
network               all adapters, IPs, status, gateway, DNS
ip                    active local IPs
ip wifi               Wi-Fi IPv4
ip ethernet           Ethernet IPv4
ip public             public-facing IP
wifi                  Wi-Fi name, IP, signal, adapter
ports                 listening ports in readable table
```

### Processes

```
processes             running processes
kill process chrome   end process by name
kill process 1234     end process by ID
```

### Files and folders

```
folder size downloads          size of a folder
folder size "My Documents"     quoted path for spaces
find file "invoice"            search by name
find file "*.pdf" in downloads search with pattern in path
open downloads                 open folder in file explorer
open desktop                   open desktop
list downloads                 list files in folder
list desktop/Hardware          list subfolder
```

### File operations

```
copy file.txt to desktop
copy downloads/file.zip to documents
copy folder project to desktop/backup

move report.pdf to documents
move folder old-stuff to documents/archive

delete file old.txt
delete folder TargetFolder
delete folder TargetFolder recursive
delete temp
delete empty-trash
```

### Cleanup

```
delete temp            clean temporary files
delete empty-trash     empty the trash / recycle bin
```

---

## Safety behavior

Destructive commands must ask before acting unless `force` is specified.

Example:

```
delete folder TargetFolder recursive
```

Response:

```
About to delete:
  TargetFolder
  including all files and folders inside it.

Continue? yes / no
```

Force mode for scripts:

```
delete folder TargetFolder recursive force
```

Dry-run mode to preview:

```
delete folder TargetFolder recursive dry-run
```

Response:

```
Dry run - nothing will be deleted.
Would delete:
  TargetFolder/file1.txt
  TargetFolder/file2.txt
  TargetFolder/subfolder/
```

Admin/root warnings:

```
This command may require administrator privileges (run as admin).
```

---

## Path aliases

These friendly names resolve to real paths automatically.

| Alias       | Resolves to                        |
|-------------|-----------------------------------|
| `desktop`   | current user Desktop               |
| `downloads` | current user Downloads             |
| `documents` | current user Documents             |
| `pictures`  | current user Pictures              |
| `music`     | current user Music                 |
| `videos`    | current user Videos                |
| `home`      | user home directory                |
| `temp`      | system temp directory              |
| `appdata`   | application data directory         |
| `here`      | current folder                     |
| `.`         | current folder                     |

Forward-slash paths work on all platforms:

```
open desktop/Hardware/ThisFolder
copy file.txt to desktop/backup
```

Quoted paths for names with spaces:

```
open "desktop/My Projects/App"
```

---

## Native passthrough

For cases where IXX doesn't have a built-in, native passthrough is the escape hatch.

```
native "powershell command here"
native "cmd command here"
native "bash command here"
```

Platform-specific shortcuts:

```
ps "Get-NetIPAddress"
cmd "dir"
sh "ls -la"
```

Native passthrough is secondary. The point of IXX is to avoid needing it for common tasks.

---

## Shell project structure

```
ixx/shell/
  repl.py             interactive loop, input handling, history, run_command_once()
  registry.py         CommandNode dataclass and CommandRegistry
  guidance.py         determines executability and next valid options from the tree
  renderer.py         all output formatting (tables, colors, ANSI)
  paths.py            path alias resolution (desktop, downloads, here, ...)
  safety.py           format_bytes(), render_table() helpers
  commands/
    __init__.py
    stubs.py          register_all() — wires every node, real and stub
    hardware.py       cpu, ram handlers
    network.py        ip, network handlers
    system.py         disk, disk space handlers
    files.py          folder size, open, list handlers
  platform/
    __init__.py       current() — selects the right platform module
    common.py         run_command() subprocess helper
    windows.py        real Windows implementations (PowerShell/CIM internally)
    linux.py          placeholder stubs for future
    macos.py          placeholder stubs for future
```

The `registry.py` module is the core of the shell's identity. It holds the command grammar as a structured data tree, not hardcoded strings. Adding a new command makes it automatically discoverable via guidance, help, and fuzzy correction.

---

## What the shell is not

- Not a Linux shell on Windows.
- Not a replacement for PowerShell for power users.
- Not a system administration tool.
- Not a way to hide the OS completely.

It is a simpler command layer for common everyday tasks.

---

## SSH / Remote administration (long-term vision)

IXX should eventually support SSH as a first-class workflow, not raw terminal passthrough.

### Planned friendly syntax

```
ssh user@192.168.1.50
ssh my-server

servers
server add my-server

run on my-server "disk space"
run on my-server "cpu"

copy report.pdf to my-server:/home/user/
copy my-server:/var/log/syslog to downloads
```

### Remote prompt identity

```
ixx>                   local shell
ixx my-server>         connected remote shell
ixx user@server>       connected remote shell
```

### Remote output labelling

When commands are run remotely, output labels the target:

```
[my-server]
Drive   Total    Free
/       915 GB   880 GB
/data   3.6 TB   3.6 TB
```

### Design requirements (future)

- Use the system OpenSSH client or a mature SSH library. Never implement raw crypto.
- Prefer SSH key authentication. Never store plaintext passwords.
- Saved server profiles are explicit and user-managed (`server add`).
- Support safe remote command preview before execution.
- Local and remote commands use the same IXX syntax where possible.
- The remote target is always clearly visible in the prompt and output.

### Current status

`ssh`, `servers`, `server add`, `server list` are registered in the command
guidance tree as stubs. They provide guidance and help text but do not
connect to anything. No credentials are stored or prompted.

Full SSH functionality is planned for a future release.

### Staged roadmap for remote access

| Milestone | What gets added |
|---|---|
| Stubs (current) | `ssh`, `servers`, `server` stubs in guidance tree only |
| Near term | First `ssh user@host` connection prototype |
| Later | Saved server profiles, `run on server "..."` |
| Future | Remote file copy, remote IXX commands, multi-server |
