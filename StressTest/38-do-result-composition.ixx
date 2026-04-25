say color("cyan", "38 do result composition")
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

ram = do("ram used")
prefix = "RAM RESULT: "
line = prefix + ram

assert "composition type", type(line), "text"

ok = NO
if count(line) more than count(prefix)
- ok = YES
assert "composition longer than prefix", ok, YES

write "StressTest/tmp/do-composed.txt", line
back = read("StressTest/tmp/do-composed.txt")
assert "composition roundtrip", back, line

say color("green", "38 do result composition complete")
