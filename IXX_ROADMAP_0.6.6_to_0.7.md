# IXX Roadmap: 0.6.6 → 0.7 Candidate

This is the working IXX roadmap, not a locked prophecy.

You’ll still send plans, repo zips, logs, and test output. The process stays the same:

- Review the current repo, plan, and logs.
- Check whether the plan fits IXX’s identity.
- Write Cursor prompts for code changes.
- Write PowerShell scripts for tests.
- Keep normal, hard, and scenario gates separate.
- Decide whether failures are:
  - my bad test
  - stale install
  - real IXX bug
  - intentional IXX behavior

## Compact Roadmap

| Version | Focus |
|---|---|
| 0.6.6 | `loop each item in items` ✅ |
| 0.6.7 | Bug & Edge Case Audit ✅ |
| 0.6.8 | Deep Audit Fixes (A–V) ✅ |
| 0.6.9 | `empty list` + `put item into list` |
| 0.6.10 | `run("native command")` and native passthrough |
| 0.6.11 | Better interactive IXX shell |
| 0.6.12 | `ixxterm` launcher + Windows integration |
| 0.7 candidate | Real local scripting shell milestone |

## Guiding Rule

Collections → Native execution → Shell → Windows integration → 0.7 candidate

IXX is becoming a local scripting language, not just a small interpreter.

The next releases should build toward this:

- Write real scripts.
- Reuse code.
- Process lists.
- Call the OS.
- Live inside the IXX shell.
- Launch it like a real tool.

## Current Foundation

IXX already has a serious base:

- Readable syntax
- Dash blocks
- Variables
- Text / number / bool / list / nothing
- Readable comparisons
- Functions
- Return values
- Try / catch
- File I/O
- `do()` IXX shell commands
- Modules/imports
- Local stdlib foundation
- Checker
- `ixx check --json`
- VS Code/Cursor diagnostics
- Normal StressTest
- Hard StressTest
- Scenario StressTest

The next work should not be random. It should build toward IXX becoming a real local scripting shell.

---

# v0.6.6 — List Iteration

## Headline

`loop each item in items`

## Goal

Add natural list iteration in IXX’s own style.

This lets IXX process batches without hardcoding `item1`, `item2`, `item3`, etc.

## Syntax

```ixx
names = "Ixxy", "Lune", "Zach"

loop each name in names
- say "Hello, {name}"
```

```ixx
numbers = 1, 2, 3, 4, 5
total = 0

loop each n in numbers
- total = total + n

say total
```

Expected output:

```text
15
```

## Why This Matters

Right now, real-world scripts have to do stuff like this:

```ixx
sale1 = 129.99
sale2 = 89.50
sale3 = 249.00

total = sale1 + sale2 + sale3
```

That works for demos, but it does not scale.

With `loop each`, IXX can handle:

- Asset batches
- Sales lists
- Report lines
- File lists
- Ticket lists
- System checks
- Inventory groups
- Log entries
- Exports

## Scope

Add:

```ixx
loop each item in list
- ...
```

Do not add yet:

- Indexing
- Empty list
- `put into`
- Map/filter/reduce
- Objects/dictionaries
- Python-style for loops

## Required Behavior

```ixx
items = "a", "b", "c"

loop each item in items
- say item
```

Runs three times.

If the source is not a list:

```ixx
loop each ch in "hello"
- say ch
```

Runtime error:

```text
'loop each' expects a list, got text.
```

Use current IXX type names:

- `text`
- `number`
- `bool`
- `list`
- `nothing`

## Scoping Behavior

If the loop variable existed before the loop, it survives with the last value:

```ixx
items = "a", "b"
item = ""

loop each item in items
- say item

say item
```

Expected final `item`:

```text
b
```

If the loop variable did not exist before the loop, it does not leak:

```ixx
items = "a", "b"

loop each item in items
- say item

say item
```

That should fail because `item` was local to the loop.

## Checker Requirements

`ixx check` should:

- Understand `loop each` syntax.
- Allow the loop variable inside the loop body.
- Respect loop variable scoping after the loop.
- Catch obvious non-list literals conservatively.
- Return valid JSON with `--json`.

Example checker case:

```ixx
loop each ch in "abc"
- say ch
```

Expected diagnostic:

```text
'loop each' expects a list, got text.
```

Only catch obvious literal cases. Do not overreach.

## Tests Expected

Python tests:

- Parser parses `loop each`.
- AST contains `LoopEach` node.
- Sum number list.
- Build text from word list.
- Nested `loop each`.
- `loop each` inside function.
- Return from inside `loop each`.
- `try/catch` inside `loop each`.
- Predeclared variable survives.
- New variable does not leak.
- Non-list text runtime error.
- Non-list number runtime error.
- Checker accepts loop variable inside body.
- Checker catches use after loop when variable was not predeclared.
- `check --json` reports literal non-list source.

StressTest additions:

- `StressTest\59-loop-each-basic.ixx`
- `StressTest\60-loop-each-nested.ixx`
- `StressTest\61-loop-each-functions.ixx`
- `StressTest\62-loop-each-try-catch.ixx`
- `StressTest\63-loop-each-imports.ixx`

ExpectedFailures:

- `bad-loop-each-text.ixx`
- `bad-loop-each-number.ixx`
- `bad-loop-each-undefined-list.ixx`

CheckJson:

- `good-loop-each.ixx`
- `bad-loop-each-text-literal.ixx`
- `bad-loop-each-number-literal.ixx`

## Release Condition

- Python tests pass.
- StressTest passes.
- Hard suite passes or only needs test updates.
- Scenario suite passes or only needs scenario updates.
- Cursor diagnostics still work.
- Docs match behavior.
- Version is `0.6.6`, not `0.7`.

---

# v0.6.7 — Bug & Edge Case Audit ✅ (completed)

v0.6.7 was used for a broad bug and edge-case audit rather than list building.
List building (`empty list` + `put into`) is planned for v0.6.9.

---

# v0.6.8 — Deep Audit Fixes (A–V) ✅ (completed)

v0.6.8 was used for a systematic set of deep audit fixes (letters A through V),
covering crash paths, error message quality, number display, REPL persistence,
checker quality, and documentation.

Native command execution (`run()`) is planned for v0.6.10.

---

# v0.6.9 — List Building / Accumulation

## Headline

`empty list`

`put item into list`

## Goal

After IXX can iterate lists, it needs to build lists.

`loop each` lets IXX read lists.

`empty list` + `put into` lets IXX create result lists.

## Syntax

```ixx
items = empty list

put "a" into items
put "b" into items

say count(items)
```

Expected output:

```text
2
```

## Filtering Example

```ixx
assets = "LAP-1001", "DESK-2001", "LAP-1002"
laptops = empty list

loop each asset in assets
- if asset contains "LAP"
-- put asset into laptops

say count(laptops)
```

Expected output:

```text
2
```

## Why This Matters

This unlocks real scripting patterns:

- Collect failed assets.
- Collect passed checks.
- Collect report lines.
- Collect files to process.
- Collect warnings.
- Collect tickets by priority.
- Filter inventory.
- Build exports.
- Batch audits.

Without this, `loop each` is useful but incomplete.

## Syntax Design

Use:

```ixx
empty list
put value into listname
```

Avoid:

```ixx
list.append(value)
append(list, value)
push(value)
add value to list
```

Reasons:

- `append` already means file append.
- `add` is commonly used as a function name.
- `put value into list` reads like IXX.

## Required Behavior

```ixx
items = empty list
put "hello" into items
put 42 into items
put YES into items
put nothing into items
```

Should work.

Lists can hold mixed IXX values.

## Runtime Errors

Missing target:

```ixx
put "x" into missing
```

Should use normal undefined-variable style.

Non-list target:

```ixx
name = "not a list"
put "x" into name
```

Runtime error:

```text
put into expects a list, got text.
```

## Scoping

This should update an outer list:

```ixx
items = empty list
names = "a", "b", "c"

loop each name in names
- put name into items

say count(items)
```

Expected output:

```text
3
```

Inside functions:

```ixx
function collect_laptops assets
- results = empty list
- loop each asset in assets
-- if asset contains "LAP"
--- put asset into results
- return results
```

## Checker Requirements

`ixx check` should:

- Understand `empty list`.
- Understand `put into`.
- Know target must exist.
- Know obvious non-list target errors.
- Return JSON errors cleanly.
- Not overreach on dynamic values.

Example checker case:

```ixx
name = "not a list"
put "x" into name
```

Expected diagnostic:

```text
put into expects a list, got text.
```

Only catch obvious/simple cases.

## Tests Expected

Python tests:

- Parse `empty list`.
- Parse `put into`.
- Empty list count is `0`.
- Put text into list.
- Put number into list.
- Put bool into list.
- Put `nothing` into list.
- Put list into list.
- Put inside `loop each`.
- Put inside function.
- Put inside `try/catch`.
- Missing target runtime error.
- Non-list target runtime error.
- Checker catches simple non-list target.
- `check --json` works for put errors.

StressTest additions:

- List accumulation.
- Filtering with `loop each`.
- Building report lines.
- Function returns built list.
- Imported function builds list.

Hard/Scenario additions:

- Collect failed assets.
- Collect warnings.
- Collect report lines.
- Collect system command results.

## Release Condition

- Normal StressTest green.
- Hard suite green.
- Scenario suite green.
- New list-building tests green.
- No mutation/scoping leaks.
- Docs match behavior.
- Version is `0.6.9`, not `0.7`.

---

# v0.6.10 — Native Command Execution in Scripts

## Headline

`run("native command")`

## Goal

Add native OS passthrough from IXX scripts.

This is different from `do()`.

Current:

```ixx
do("ram used")
```

Means:

```text
Run an IXX shell command.
```

New:

```ixx
run("git status")
```

Means:

```text
Run a native OS command.
```

## Syntax

```ixx
output = run("git status")
say output
```

```ixx
try
- output = run("command-that-does-not-exist")
catch
- say "Command failed: {error}"
```

## Why This Matters

This turns IXX into an actual automation language.

It can start doing things like:

- Git automation
- Windows command automation
- PowerShell wrappers
- File conversion pipelines
- Server checks
- Deployment scripts
- Test runners
- Project setup scripts

## Important Distinction

```ixx
do("ram used")
```

IXX command bridge.

```ixx
run("ipconfig")
```

Native system command.

Do not merge these. The difference should stay clear.

## Required Behavior

```ixx
out = run("echo hello")
say out
```

Should output text containing:

```text
hello
```

If command exits nonzero:

```ixx
run("not-a-real-command")
```

Should raise an IXX runtime error.

If inside `try/catch`, it should be catchable.

## Runtime Errors

Empty command:

```ixx
run("")
```

Error:

```text
run() received an empty command.
```

Wrong type:

```ixx
run(123)
```

Error:

```text
'run' expects a native command as text, not number.
```

Nonzero exit:

```text
Native command failed with exit code X.
stderr...
```

## Security / Clarity

Docs must be blunt:

```text
run() executes native system commands on your machine.
```

This is powerful and should not be hidden.

## Implementation Expectations

Use Python `subprocess`.

For `0.6.8`, simple text command is okay:

```ixx
run("git status")
```

Later maybe add safer multi-arg form:

```ixx
run("git", "status")
```

Do not add multi-arg form yet unless it is simple and well-tested.

## Checker Requirements

`ixx check` should validate:

- Arity.
- Literal empty command.
- Literal wrong type.
- JSON output.

It should not execute commands during check.

## Tests Expected

Python tests:

- `run("echo hello")` returns text.
- Bad command fails.
- Empty command fails.
- Non-text command fails.
- `run()` works in `try/catch`.
- `run()` works inside function.
- `run()` works inside `loop each`.
- `do()` still works separately.
- `check --json` catches `run("")`.
- `check --json` catches `run(123)`.

StressTest additions:

- Native command report.
- `run()` in loops.
- `run()` in imported functions.
- `run()` plus file output.
- `run()` failure catch.

Scenario update:

- System report scenario can use `run("ipconfig")` or similar.

## Release Condition

- All old `do()` tests still pass.
- New `run()` tests pass.
- Docs clearly separate `do()` vs `run()`.
- Native commands do not execute during imports/checking.
- Version is `0.6.10`, not `0.7`.

---

# v0.6.11 — Better Interactive IXX Shell

## Headline

Improve `ixx>`.

## Goal

Make the interactive shell useful as a daily home base.

Right now IXX has an interactive mode, but the goal is to make it feel like a small shell, not just a language REPL.

## Desired Shell Behavior

Inside:

```cmd
ixx
```

You should be able to do:

```text
ixx> say "hello"
ixx> ram used
ixx> do "ram used"
ixx> cd C:\Users\cbuck\Desktop\IXX
ixx> pwd
ixx> clear
ixx> history
ixx> ! git status
ixx> ! ipconfig
ixx> run StressTest\run-all.cmd
```

## Feature Set

Add shell-level commands:

- `cd`
- `pwd`
- `clear`
- `history`
- `exit`
- `help`
- `version`

Add native passthrough:

```text
! git status
! ipconfig
! dir
```

Use `!` at first so passthrough is explicit.

Do not silently send unknown input to the OS yet. If someone mistypes IXX code, it should not accidentally run a native command.

## Why This Matters

After `run()` exists, IXX can execute native commands in scripts.

The shell should then let IXX become the place where you:

- Run IXX scripts.
- Check files.
- Call IXX commands.
- Call native commands.
- Move around folders.
- Inspect system info.

## Shell Command Categories

### IXX code

```ixx
say "hello"
x = 5
say x
```

### IXX shell command

```text
ram used
cpu info
disk space
```

### Native passthrough

```text
! git status
! ipconfig
```

### Shell control

```text
cd
pwd
clear
history
exit
```

## Required Behavior

`cd` changes the shell working directory and affects:

- Relative file paths.
- IXX script runs.
- `run()` commands.

`pwd` prints current working directory.

`history` shows recent commands.

`clear` clears the screen.

`! command` runs native OS command and prints output.

## Tests Expected

This needs different tests than normal `.ixx` scripts.

Automated shell tests if practical:

- Start shell process.
- Send commands.
- Verify output.
- `cd` changes directory.
- `pwd` reports directory.
- `! echo hello` works.
- `history` includes commands.
- `exit` exits cleanly.

If automated shell testing is annoying, create a manual `ShellTest` runner with PowerShell.

## Docs

Update:

- `ixx help`
- README shell section
- Dictionary shell command section

## Release Condition

- `run()` already works.
- `do()` still works.
- Shell can `cd`, `pwd`, `clear`, and `history`.
- `!` passthrough works.
- No accidental native command execution without `!`.
- Version is `0.6.11`, not `0.7`.

---

# v0.6.12 — Windows Integration / Launcher

## Headline

`ixxterm`

Windows Terminal profile

Win+R / Explorer entrypoint

## Goal

Make IXX launch like a real local tool on Windows.

This is where the Win+R / Explorer address bar idea belongs.

## Deliverables

### Console Command

Add a console script:

```cmd
ixxterm
```

That launches the IXX shell directly.

Equivalent to:

```cmd
ixx
```

or:

```cmd
ixx shell
```

but specifically named like a terminal entrypoint.

## Win+R

After install, this should work:

```text
Win+R → ixxterm
```

## Explorer Address Bar

In a folder, typing:

```text
ixxterm
```

should open IXX in that folder if Windows launches it with the current directory.

This may require wrapper behavior or documentation depending on how Windows handles it.

## Windows Terminal Profile

Optional but important:

Create or document a Windows Terminal profile:

```json
{
  "name": "IXX Shell",
  "commandline": "ixxterm",
  "startingDirectory": "%USERPROFILE%"
}
```

Could later include:

- Icon
- Color scheme
- Tab title

## Start Menu Shortcut

Maybe:

```text
IXX Shell
```

Starts `ixxterm`.

## Installer Thoughts

This may require either:

- Pip-installed console scripts
- PowerShell setup script
- Optional Windows Terminal profile installer
- Future MSI/EXE installer

Do not build a full installer yet unless everything else is solid.

## Why After 0.6.9

No point making a fancy launcher before the shell is useful.

The order is:

```text
run() native passthrough
better ixx shell
ixxterm launcher
Windows Terminal integration
```

## Tests Expected

Installer-ish tests:

- `pip install -e .`
- `where ixx`
- `where ixxterm`
- `ixxterm` launches shell
- `ixxterm --version` maybe works
- Windows Terminal profile file generated correctly

Manual tests:

- Win+R `ixxterm`
- Explorer address bar `ixxterm`
- New terminal opens in expected folder

## Release Condition

- `ixxterm` entrypoint exists.
- It launches IXX shell.
- Docs explain Win+R and Explorer use.
- Existing `ixx` command still works.
- Version is `0.6.12` unless this becomes the actual `0.7` milestone.

---

# v0.7 Candidate — IXX Feels Real

Do not bump to `0.7` just because one feature is big.

`0.7` should be the point where IXX feels like a real local scripting shell.

## Required Foundation Before 0.7

By then, IXX should have:

- Modules/imports
- Stdlib foundation
- `loop each`
- `empty list`
- `put into`
- Native `run()`
- Better interactive shell
- `ixxterm` launcher
- Editor diagnostics
- Normal StressTest
- Hard StressTest
- Scenario StressTest
- Docs that match behavior

## What 0.7 Should Mean

A user can install IXX and actually use it for local automation:

```ixx
use "helpers.ixx"
use std "date"

files = "a.txt", "b.txt", "c.txt"
missing = empty list

loop each file in files
- if exists(file)
-- say "Found {file}"
- else
-- put file into missing

result = run("git status")
write "status.txt", result
```

And can also work interactively:

```text
ixxterm
ixx> cd C:\Users\cbuck\Desktop\IXX
ixx> ram used
ixx> ! git status
ixx> ixx check StressTest\run-all.cmd
```

## Possible 0.7 Headline

```text
IXX 0.7 — Local Scripting Shell Foundation
```

Not:

```text
One random feature got added.
```

## 0.7 Release Gates

Before `0.7`, require:

- Python unit tests green.
- StressTest green.
- Hard suite green.
- Scenario suite green.
- Clean venv install test green.
- Wheel/package-data test green.
- Basic editor extension test green.
- Docs reviewed against actual behavior.
- `ixx version` matches package version.
- PyPI install verified.
- Editable install verified.

---

# Parallel Tracks

These do not have to wait perfectly in line.

## Editor / Cursor Extension Track

Already has diagnostics.

Next useful editor work:

- Run current `.ixx` file command.
- Check current `.ixx` file command.
- Open terminal in file folder.
- Snippets for:
  - function
  - if
  - loop
  - loop each
  - try/catch
  - use
- Hover docs for built-ins.
- Maybe quick fixes later.

This can happen anytime after current feature work settles.

## Stdlib Track

Current stdlib is tiny.

After list building, stdlib can become more useful:

- `std text`
- `std reports`
- `std files`
- `std csv`
- `std math`
- `std sys`
- `std date`
- `std time`

Do not overbuild before lists are strong.

## Testing Track

Current test layers:

- `StressTest\run-all.cmd`
- `StressTest\Hard\run-hard.cmd`
- `StressTest\Scenario\run-scenario.cmd`

Next testing upgrades:

- Clean venv install test.
- Wheel/package-data test.
- Linux smoke test.
- Windows shell test.
- Editor extension smoke test.
- Performance timing summary.
- PyPI install verification.
- Fresh clone verification.

## Packaging Track

Before `ixxterm`, verify:

- PyPI install works.
- Editable install works.
- Wheel includes grammar.
- Wheel includes stdlib `.ixx` files.
- Extension packaging works.
- Version command matches package version.
- Console entrypoints work.

---

## Final Compact Map

```text
0.6.6  loop each              ✅ done
0.6.7  bug & edge case audit  ✅ done
0.6.8  deep audit fixes A–V   ✅ done
0.6.9  empty list + put into
0.6.10 run() native passthrough
0.6.11 better ixx shell
0.6.12 ixxterm / Windows integration
0.7    real local scripting shell milestone
```
