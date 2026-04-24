# IXX v0.4 demo script
# Run with: ixx demo
# This script demonstrates the core language features available in v0.4.

# ── Variables and strings ──────────────────────────────────────────────────────
name = "IXX"
say "Welcome to {name}!"

# ── Numbers and math ──────────────────────────────────────────────────────────
x = 12
y = 5
say "Sum: {x} + {y} = " + text(x + y)
say "Product: {x} * {y} = " + text(x * y)

# ── Conditions ────────────────────────────────────────────────────────────────
age = 20
if age less than 18
- say "Too young"
else
- say "Old enough"

# ── Booleans ──────────────────────────────────────────────────────────────────
ready = YES
if ready is YES
- say "Let's go"

# ── Lists and contains ────────────────────────────────────────────────────────
fruits = "apple", "banana", "mango"
say "Fruit count: " + text(count(fruits))
if fruits contains "banana"
- say "Found banana"

# ── Loop ──────────────────────────────────────────────────────────────────────
n = 3
loop n more than 0
- say "Countdown: {n}"
- n = n - 1
say "Done"

# ── Functions ─────────────────────────────────────────────────────────────────
function greet person
- say "Hello, {person}!"

function add a, b
- return a + b

greet "World"
result = add(10, 7)
say "10 + 7 = {result}"

# ── Built-ins ─────────────────────────────────────────────────────────────────
items = "one", "two", "three"
say "Item count: " + text(count(items))
say "Type of result: " + type(result)
say "Number from text: " + text(number("42"))
