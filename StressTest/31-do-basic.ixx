say color("cyan", "31 do basic")
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
asserttext "do ram used", ram

cpu = do("cpu info")
asserttext "do cpu info", cpu

ip = do("ip local")
asserttext "do ip local", ip

say color("green", "31 do basic complete")
