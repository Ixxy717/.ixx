# IXX functions example — v0.4
# Demonstrates: definitions, calls, return values, scope, recursion, built-ins

# ── Basic function ─────────────────────────────────────────────────────────────
function greet name
- say "Hello, {name}!"

greet "World"
greet "IXX"

# ── Multiple parameters ────────────────────────────────────────────────────────
function add a, b
- return a + b

result = add(10, 7)
say "10 + 7 = {result}"

# ── Conditional return ─────────────────────────────────────────────────────────
function classify score
- if score at least 90
-- return "A"
- if score at least 80
-- return "B"
- if score at least 70
-- return "C"
- return "F"

say "92 -> " + classify(92)
say "85 -> " + classify(85)
say "55 -> " + classify(55)

# ── Scoping: local variables don't leak ───────────────────────────────────────
x = "global"

function demo_scope
- x = "local"
- say "Inside function: {x}"

demo_scope
say "Outside function: {x}"

# ── Recursion ─────────────────────────────────────────────────────────────────
function factorial n
- if n at most 1
-- return 1
- sub = factorial(n - 1)
- return n * sub

say "5! = " + text(factorial(5))
say "10! = " + text(factorial(10))

# ── Divider helper (no args) ───────────────────────────────────────────────────
function divider
- say "--------------------"

divider
say "Functions example complete"
divider

# ── Built-ins alongside functions ─────────────────────────────────────────────
function describe_list items
- say "Count: " + text(count(items))
- say "Type: " + type(items)

fruits = "apple", "banana", "mango"
describe_list fruits
