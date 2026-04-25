say color("cyan", "36 do command matrix")
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

a = do("ram")
b = do("cpu")
c = do("disk space")
d = do("network")
e = do("ports")

asserttext "do ram overview", a
asserttext "do cpu overview", b
asserttext "do disk space", c
asserttext "do network", d
asserttext "do ports", e

say color("green", "36 do command matrix complete")
