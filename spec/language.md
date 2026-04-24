# IXX Language Specification

IXX is executable checklist-style code using visible dash blocks and simple English comparisons.

It sits between plain English and normal code. It should feel like writing a checklist or a set of instructions, not programming.

---

## Identity

- Top-level code runs directly. No required `main`.
- No braces, no semicolons, no required parentheses for basic logic.
- No indentation-based blocks. Use visible `-` lines instead.
- Minimal punctuation. `=`, commas, quotes, and periods are fine. Symbolic soup like `===`, `&&`, `||`, `{}` is not.
- Short, obvious commands. No giant keyword dictionary.

---

## Comments

Lines starting with `#` are comments and are ignored.

```
# This is a comment
say "Hello"   # This is also fine
```

---

## Variables

Assignment uses `=`.

```
name = "Ixxy"
age = 19
score = 0
active = YES
```

Variable names are single words. Letters, numbers, and underscores are allowed. Must start with a letter or underscore.

---

## Values

| Type    | Examples                        |
|---------|---------------------------------|
| Text    | `"Hello"`, `"Ixxy"`             |
| Number  | `42`, `3.14`, `-10`             |
| Boolean | `YES`, `NO` (case-insensitive)  |
| List    | `"apple", "banana", "grape"`    |

### String interpolation

Use `{varname}` inside a string to insert a variable's value.

```
name = "Ixxy"
say "Hello, {name}"
# prints: Hello, Ixxy
```

If the variable is not defined, `{?name}` is shown in the output and a warning is printed to stderr.

### Lists

A comma-separated series of values creates a list.

```
fruits = "apple", "banana", "grape"
```

Lists work with `contains` and `say`.

```
say fruits
# prints: apple, banana, grape
```

---

## Blocks and nesting

A block is a group of lines that belong to the statement above them.
Lines belonging to a block start with dashes.

```
- one level deep
-- two levels deep
--- three levels deep
```

The space after the dashes is optional but recommended for readability.

Rules:
- No dash = top-level code.
- `-` = one level inside the previous block header.
- `--` = two levels inside.
- `---` = three levels inside.

```
if logged_in is YES
- say "Welcome"
- show_dashboard = YES
else
- say "Please sign in"
```

Nested example:

```
if user is "Ixxy"
- say "Hello Ixxy"
- if age at least 18
-- say "Adult account"
-- say "Full access"
- else
-- say "Limited account"
```

---

## if / else

```
if condition
- statement
- statement
else
- statement
- statement
```

`else` is optional.

```
score = 92

if score at least 90
- say "A"
else
- say "Not A"
```

---

## loop

Repeats while the condition is true.

```
loop condition
- statement
- statement
```

Example:

```
count = 3

loop count more than 0
- say "Tick: {count}"
- count = count - 1
```

---

## say

Outputs values to the screen. Accepts one or more comma-separated expressions.

```
say "Hello World"
say name
say "Score:", score
say "Hello, {name}"
```

---

## Comparisons

Word-based operators are preferred. Symbolic operators may be added as aliases later.

| Operator   | Meaning            | Example                  |
|------------|--------------------|--------------------------|
| `is`       | equal              | `if score is 100`        |
| `is not`   | not equal          | `if status is not "ban"` |
| `less than`| strictly less      | `if age less than 18`    |
| `more than`| strictly greater   | `if score more than 50`  |
| `at least` | greater or equal   | `if score at least 90`   |
| `at most`  | less or equal      | `if lives at most 2`     |
| `contains` | membership / text  | `if items contains "x"`  |

`contains` works on both lists and text strings:

```
fruits = "apple", "banana", "grape"
if fruits contains "banana"
- say "Found it"

message = "Hello World"
if message contains "World"
- say "Found World"
```

---

## Logic

```
if ready and logged_in
- say "Go"

if tired or bored
- say "Take a break"

if not active
- say "Account is inactive"
```

---

## Arithmetic

```
total = score + bonus
diff  = 100 - score
area  = width * height
half  = total / 2
neg   = -score
```

String concatenation uses `+`:

```
greeting = "Hello, " + name
```

---

## Truthiness

A value is true when:
- Boolean: `YES`
- Number: any non-zero value
- Text: any non-empty string
- List: any non-empty list

A value is false when:
- Boolean: `NO`
- Number: `0`
- Text: `""`
- List: empty list

---

## Scoping

Variables set inside a block (`if`, `loop`) that were previously defined in an outer scope are updated in the outer scope.

Variables created for the first time inside a block stay in that block.

---

## Reserved words

These words cannot be used as variable names:

`if`, `else`, `loop`, `say`, `and`, `or`, `not`, `is`, `less`, `more`, `than`, `at`, `least`, `most`, `contains`, `YES`, `NO`, `nothing`, `function`, `return`, `try`, `catch`

---

## Functions

Define a function with the `function` keyword. The body is a dash block.

```
function greet name
- say "Hello, {name}"

greet "World"
```

### Parameters

Multiple parameters are comma-separated:

```
function add a, b
- say a + b

add 3, 4
```

### Return values

Use `return` to return a value. Bare `return` returns `nothing`.

Functions called in expression position (RHS of assignment, inside `say`,
inside arithmetic) must use parentheses:

```
function add a, b
- return a + b

result = add(5, 3)          # expression position — parens required
say "Result: {result}"

say add(10, 2)              # expression position in say — parens required
```

Functions called as standalone statements use space-separated arguments:

```
greet "World"               # statement position — no parens needed
countdown 5
```

### Scoping

Functions have their own local scope. Local variables do not leak out to
the calling scope. Reads can see global variables; writes are always local.

```
x = 100

function show x
- say x          # sees the parameter x, not the global

show 42          # prints: 42
say x            # prints: 100  (global unchanged)
```

### Recursion

Functions may call themselves. Recursion is limited to 100 levels to
prevent infinite recursion from hanging the program.

```
function factorial n
- if n at most 1
-- return 1
- sub = factorial(n - 1)
- return n * sub

say factorial(5)             # prints: 120
```

### Forward calls

The interpreter collects all function definitions in a first pass before
executing any code. Functions defined later in the file can be called from
earlier lines.

---

## Built-in functions (v0.4)

Built-ins are always available. No import is needed.
In expression position they require parentheses like user-defined functions.

| Name | Arguments | Returns | Description |
|------|-----------|---------|-------------|
| `count(x)` | list or text | number | Number of items or characters |
| `text(x)` | any | text | Converts a value to its text representation |
| `number(x)` | text or number | number | Converts text to a number; raises an error if conversion fails |
| `type(x)` | any | text | Returns the IXX type name: `text`, `number`, `bool`, `list`, `nothing` — `bool` is the documented name for `YES`/`NO` values |
| `ask(prompt)` | text (optional) | text | Prompts the user for input and returns what they typed |

Examples:

```
items = "one", "two", "three"
say count(items)              # 3
say text(42)                  # 42
say number("7")               # 7
say type(YES)                 # bool
answer = ask("Your name? ")
say "Hello, {answer}"
```

---

## Built-in functions (v0.5)

### Text

| Name | Arguments | Returns | Description |
|------|-----------|---------|-------------|
| `upper(x)` | text | text | Convert to uppercase |
| `lower(x)` | text | text | Convert to lowercase |
| `trim(x)` | text | text | Remove spaces from both ends |
| `replace(x, find, with)` | text, text, text | text | Replace all occurrences of `find` with `with` |
| `split(x)` | text | list | Split on whitespace |
| `split(x, sep)` | text, text | list | Split on a separator |
| `join(items)` | list | text | Join with `", "` |
| `join(items, sep)` | list, text | text | Join with a separator |

### Math

| Name | Arguments | Returns | Description |
|------|-----------|---------|-------------|
| `round(x)` | number | number | Round to the nearest whole number |
| `round(x, digits)` | number, number | number | Round to `digits` decimal places |
| `abs(x)` | number | number | Absolute value (removes the minus sign) |
| `min(a, b)` | number, number | number | The smaller of two values |
| `min(list)` | list | any | The smallest item in a list |
| `max(a, b)` | number, number | number | The larger of two values |
| `max(list)` | list | any | The largest item in a list |

### Lists

| Name | Arguments | Returns | Description |
|------|-----------|---------|-------------|
| `first(items)` | list | any | First item, or `nothing` if empty |
| `last(items)` | list | any | Last item, or `nothing` if empty |
| `sort(items)` | list | list | Sorted copy (alphabetical or numeric) |
| `reverse(items)` | list | list | Reversed copy |

### Color output

| Name | Arguments | Returns | Description |
|------|-----------|---------|-------------|
| `color(name, text)` | text, text | text | Wrap text in a terminal color |

Available color names: `red`, `green`, `yellow`, `cyan`, `bold`, `dim`

Respects `NO_COLOR` and `IXX_COLOR=0`. Falls back to plain text with no ANSI codes when color is disabled.

```
say color("green", "All good")
say color("red", "Something went wrong")
say color("yellow", "Warning: check your input")
say color("bold", "Done.")
```

---

## nothing

`nothing` is the IXX null value. It is returned by functions that do not explicitly return a value, and can be used as a default before a `try` block.

```
status = nothing
say type(status)   # nothing

function empty
- return

r = empty()
say type(r)        # nothing
```

---

## File I/O built-ins (v0.6)

Read and write files using the built-in functions below. Paths are relative to the current working directory unless absolute.

| Name | Arguments | Returns | Description |
|------|-----------|---------|-------------|
| `read(path)` | text | text | Read the full contents of a file as a single string |
| `readlines(path)` | text | list | Read a file and return its lines as a list (newlines stripped) |
| `write(path, content)` | text, any | nothing | Write (overwrite) any value to a file — uses IXX display format |
| `append(path, content)` | text, any | nothing | Append any value to the end of a file — uses IXX display format |
| `exists(path)` | text | YES/NO | Check whether a file or folder exists |

All five raise an `IXXRuntimeError` with a friendly message if the file cannot be read or written (file not found, permission denied, etc.).

`write` and `append` are called as statements with space-separated arguments:
```
write "notes.txt", "My note"
append "notes.txt", " More text."
```

`read`, `readlines`, and `exists` are typically used in expression position:
```
content = read("notes.txt")
lines   = readlines("notes.txt")

if exists("config.txt")
- say "Config found"
```

---

## try / catch (v0.6)

Run a block of code and handle any error without crashing.

```
try
- statement
- statement
catch
- say "Something went wrong: {error}"
```

- The `catch` block is optional. Without it, errors are swallowed silently and execution continues.
- Inside `catch`, the variable `error` is automatically set to the error message text.
- `try` catches `IXXRuntimeError` and OS/IO errors (file not found, permission denied, etc.).
- Execution always continues after the `try`/`catch` block.

### Scoping

`try` and `catch` bodies each run in a **child scope** — a fresh environment that inherits every variable from the surrounding scope.

Rules:
- **Pre-declared variables can be updated** — if a variable exists before `try`, setting it inside `try` or `catch` changes the original.
- **New variables stay local** — a variable first introduced inside `try` or `catch` does not exist after the block ends.
- **`error` is local to `catch`** — it is only accessible inside the `catch` block.
- **Silent try** — `try` without `catch` swallows the error and execution continues normally after the block.

```
# Pre-declared variable: update survives the block
result = nothing
try
- result = read("data.txt")
catch
- say "Read failed: {error}"

if result is not nothing
- say "Got: {result}"

# New variable: does NOT survive the block
try
- local_only = "inside"
say local_only   # runtime error -- not defined here

# Silent try: errors are discarded, execution continues
try
- x = read("might-not-exist.txt")
say "Always runs"
```

### Examples

```
# Graceful file read
content = nothing
try
- content = read("notes.txt")
catch
- say "Could not read notes: {error}"

# Silent try -- error swallowed, execution continues
try
- risky = read("might-not-exist.txt")
say "Continuing..."

# Nested: try inside a function
function load_config path
- cfg = nothing
- try
-- cfg = read(path)
-- catch
-- say "Config missing, using defaults"
- return cfg
```

---

## Full example

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
