say color("cyan", "78 letter-o float display")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

# O1: 0.1 + 0.2 must display as "0.3" (not 0.30000000000000004)
# Use text() to compare the display string, not the raw float value
result = 0.1 + 0.2
assert "point-one plus point-two display", text(result), "0.3"

# O1: 1.1 + 2.2
result2 = 1.1 + 2.2
assert "1.1 plus 2.2 display", text(result2), "3.3"

# O1: integer division — 10/2 displays as 5, not 5.0
int_div = 10 / 2
assert "integer division display", text(int_div), "5"

# O1: normal float literals unchanged
assert "3.14 display", text(3.14), "3.14"
assert "0.5 display", text(0.5), "0.5"

# O3: number("1e5") must display as 100000, not 100000.0
n = number("1e5")
assert "number 1e5 display", text(n), "100000"

# O3: number("1.0") clean display (trailing .0 stripped)
n2 = number("1.0")
assert "number 1.0 display", text(n2), "1"

# normal number conversion still works
assert "number 42 string", number("42"), 42
assert "number 3.14 string", text(number("3.14")), "3.14"
assert "number minus 7", number("-7"), -7

say color("green", "78 letter-o float display complete")
