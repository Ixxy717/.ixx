# IXX Shell Design Specification

This document describes the design of the IXX interactive shell and console.

The shell is not yet implemented. This document is the authoritative design target.

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

### Examples

Typing `cpu` shows:

```
usage
core-count
temperature
speed
info
```

Typing `disk` shows:

```
list
health
space
partitions
mounts
```

Typing `disk health` shows:

```
all
disk 0
disk 1
C:
D:
```

Typing `delete` shows:

```
delete file <path>
delete folder <path> [recursive] [force] [dry-run]
delete temp
delete empty-trash
```

Typing `copy` shows:

```
copy <source> to <destination>

Examples:
  copy report.pdf to desktop
  copy downloads/file.zip to documents
  copy folder project to desktop/project-backup
```

Typing `find file` shows:

```
find file <name or pattern> [in <path>]

Examples:
  find file "invoice"
  find file "*.pdf" in downloads
  find file "resume" in documents
```

Typing `ip` shows:

```
all
wifi
ethernet
public
local
```

### What the guidance engine knows per command

For every built-in command, the guidance engine records:

- Valid next words and argument types
- Short description of each option
- Whether the option or command is destructive
- Whether admin or root access may be required
- Whether the command runs immediately or prompts first
- Whether a dry-run mode is available
- Example invocations

### Help commands

```
help                  broad categories
help disk             disk commands
help delete           delete syntax, examples, safety notes
? disk                same as help disk
disk ?                valid next options for disk
delete ?              valid next options for delete
```

### Fuzzy correction

If the user types something close but wrong:

```
cpoy file.txt to desktop
```

IXX responds:

```
Did you mean: copy file.txt to desktop?
```

```
wifi address
```

IXX suggests:

```
wifi ip
ip wifi
network ip
```

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
This command may require admin privileges.
Run as administrator or use: native "..."
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
/shell
  repl/               interactive loop, input handling, history
  command-guidance/   grammar tree for built-in commands, next-arg engine
  autocomplete/       render hints inline as user types
  history/            command history and search
  rendering/          output formatting, tables, colors, warnings
```

The `command-guidance/` module is the core of the shell's identity. It holds the command grammar as a structured data tree, not hardcoded strings. Adding a new command makes it automatically discoverable via guidance, help, and fuzzy correction.

---

## What the shell is not

- Not a Linux shell on Windows.
- Not a replacement for PowerShell for power users.
- Not a system administration tool.
- Not a way to hide the OS completely.

It is a simpler command layer for common everyday tasks.
