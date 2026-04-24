say color("cyan", "19 scope edgecases")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

value = "root"

if YES
- value = "if updated"
assert "if updates root", value, "if updated"

loopcount = 1
loop loopcount more than 0
- value = "loop updated"
- loopcount = loopcount - 1
assert "loop updates root", value, "loop updated"

try
- value = "try updated"
catch
- value = "catch bad"
assert "try updates root", value, "try updated"

try
- bad = read("StressTest/tmp/missing-for-catch-scope.txt")
catch
- value = "catch updated"
assert "catch updates root", value, "catch updated"

function shadowroot
- value = "function local"
- return value

inside = shadowroot()
assert "function returns local value", inside, "function local"
assert "function does not update root", value, "catch updated"

say color("green", "19 scope edgecases complete")
