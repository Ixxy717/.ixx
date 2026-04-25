say color("cyan", "65 loop each scoping more")
function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

function assertyes name, value
- if value
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: YES"
- say "Got: NO"
- crash = number("ASSERT_FAIL")

function asserttext name, value
- assert name + " type", type(value), "text"
- ok = NO
- if count(value) more than 0
-- ok = YES
- assertyes name + " not empty", ok

values = "first", "middle", "last"

current = "before"
loop each current in values
- say "inside {current}"

assert "predeclared loop var survives", current, "last"

total = 0
nums = 2, 4, 6, 8
loop each n in nums
- total = total + n

assert "new loop var did not break total", total, 20

shadow = "outer"
groups = "A", "B"
loop each group in groups
- shadow = group

assert "outer updated by body", shadow, "B"
say color("green", "65 loop each scoping more complete")
