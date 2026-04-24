say color("cyan", "26 silent try recovery")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

state = "before"

try
- missing = read("StressTest/tmp/silent-missing.txt")

state = "after silent"
assert "state after silent try", state, "after silent"

fallback = "unset"
try
- fallback = read("StressTest/tmp/nope-again.txt")
catch
- fallback = "fallback value"
assert "fallback catch", fallback, "fallback value"

numbervalue = nothing
try
- numbervalue = number("bad")
catch
- numbervalue = 123
assert "recover from bad number", numbervalue, 123

say color("green", "26 silent try recovery complete")
