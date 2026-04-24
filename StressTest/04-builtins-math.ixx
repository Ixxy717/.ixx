say color("cyan", "04 builtins math")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

rounded = round(3.7)
assert "round whole", rounded, 4

rounded2 = round(3.14159, 2)
assert "round digits", rounded2, 3.14

absolute = abs(-42)
assert "abs", absolute, 42

small = min(10, 4)
assert "min pair", small, 4

big = max(10, 4)
assert "max pair", big, 10

nums = 9, 3, 7, 1, 5
smallest = min(nums)
biggest = max(nums)
assert "min list", smallest, 1
assert "max list", biggest, 9

math = (5 + 3) * 2
assert "grouped arithmetic", math, 16

div = 10 / 4
assert "division float", div, 2.5

negative = -5
assert "negative literal", negative, -5

say color("green", "04 builtins math complete")
