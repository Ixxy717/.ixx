# Kitchen sink — uses every major language feature in one script

use std "time"
use std "date"

# Variables and types
name = "IXX"
version = "0.6.7"
active = YES
nothing_val = nothing
count_of = 0

# Arithmetic
x = 10 + 5 * 2 - 3
y = round(x / 3, 2)
z = abs(x - 30)

# String operations
greeting = "Hello from " + name + " v" + version
say greeting
say "x=" + x + " y=" + y + " z=" + z

# Functions
function double n
- return n * 2

function greet who
- return "Hi, " + who + "!"

function bounded val, lo, hi
- if val less than lo
-- return lo
- if val more than hi
-- return hi
- return val

say double(21)
say greet("World")
say bounded(150, 0, 100)

# If/else
if active
- say "System is active"

if x more than 20
- say "x > 20"
else
- say "x <= 20"

# Loop (while style)
i = 1
total = 0
loop i at most 5
- total = total + i
- i = i + 1
say "Sum 1..5 = " + total

# List operations
items = 3, 1, 4, 1, 5, 9, 2, 6
say "Count: " + count(items)
say "First: " + first(items)
say "Sorted: " + join(sort(items), ",")
say "Min: " + min(items) + "  Max: " + max(items)

# Loop each
loop_sum = 0
loop each n in items
- loop_sum = loop_sum + n
say "Loop sum: " + loop_sum

# Try/catch
caught = NO
try
- bad = number("oops")
catch
- caught = YES
- say "Caught: " + error
say "Error caught: " + text(caught)

# File I/O
ks_path = "StressTest/tmp/rw-50-ks.txt"
write ks_path, "kitchen sink test"
content = read(ks_path)
say "File content: " + content
if exists(ks_path)
- say "File exists: YES"

# Text builtins
say upper("hello")
say lower("WORLD")
say trim("  spaces  ")
say replace("foo bar baz", "bar", "qux")
say count(split("one two three"))

# Math builtins
say round(3.14159, 3)
say abs(-99)

# Stdlib
say time_greeting(10)
say text(is_leap_year(2024))

# Type checks
say type(42) + " " + type("hi") + " " + type(YES) + " " + type(nothing_val) + " " + type(items)

say "Kitchen sink complete."
