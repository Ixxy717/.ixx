say color("cyan", "01 basics")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

name = "Ixxy"
project = "IXX"
age = 19
active = YES
inactive = NO
empty = nothing

say "Hello, {name}"
say "Undefined variable should show {?ghost}: {ghost}"

assert "text variable", name, "Ixxy"
assert "number variable", age, 19
assert "YES bool", active, YES
assert "NO bool", inactive, NO
assert "nothing type", type(empty), "nothing"

math = 2 + 3 * 4
assert "operator precedence", math, 14

math2 = (2 + 3) * 4
assert "parentheses", math2, 20

concat = "Hello, " + project
assert "string concat", concat, "Hello, IXX"

minus = 10 - 3
assert "subtraction", minus, 7

times = 6 * 7
assert "multiplication", times, 42

divided = 10 / 4
assert "division", divided, 2.5

branch = "bad"
if age at least 18
- branch = "adult"
else
- branch = "minor"
assert "if else adult", branch, "adult"

comp = NO
if age is 19
- comp = YES
assert "is comparison", comp, YES

comp = NO
if age is not 18
- comp = YES
assert "is not comparison", comp, YES

comp = NO
if age more than 18
- comp = YES
assert "more than comparison", comp, YES

comp = NO
if age less than 20
- comp = YES
assert "less than comparison", comp, YES

comp = NO
if age at most 19
- comp = YES
assert "at most comparison", comp, YES

items = "apple", "banana", "ixx"
hasbanana = NO
if items contains "banana"
- hasbanana = YES
assert "list contains", hasbanana, YES

message = "hello ixx world"
hasixx = NO
if message contains "ixx"
- hasixx = YES
assert "text contains", hasixx, YES

logic = NO
if active and age at least 18
- logic = YES
assert "and logic", logic, YES

logic = NO
if inactive or active
- logic = YES
assert "or logic", logic, YES

logic = NO
if not inactive
- logic = YES
assert "not logic", logic, YES

logic = NO
if not empty
- logic = YES
assert "not nothing", logic, YES

countdown = 3
total = 0
loop countdown more than 0
- total = total + countdown
- countdown = countdown - 1
assert "loop sum", total, 6

say color("green", "01 basics complete")
