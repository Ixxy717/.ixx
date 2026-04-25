say color("cyan", "39 do multiple calls")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

function assertyes name, value
- if value
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: YES"
- say "Got: NO"
- crash = number("ASSERT_FAIL")

function asserttext name, value
- t = type(value)
- assert name, t, "text"
- ok = NO
- if count(value) more than 0
-- ok = YES
- assertyes name + " not empty", ok

one = do("ram used")
two = do("ram used")
three = do("cpu info")

assert "first call text", type(one), "text"
assert "second call text", type(two), "text"
assert "third call text", type(three), "text"

ok = NO
if count(one) more than 0 and count(two) more than 0
- ok = YES
assert "two repeated calls nonempty", ok, YES

say color("green", "39 do multiple calls complete")
