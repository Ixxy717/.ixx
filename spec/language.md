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

If the variable is not defined, `{name}` is left as-is.

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

`if`, `else`, `loop`, `say`, `and`, `or`, `not`, `is`, `less`, `more`, `than`, `at`, `least`, `most`, `contains`, `YES`, `NO`

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
