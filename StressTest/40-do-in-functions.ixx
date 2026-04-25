say color("cyan", "40 do in functions")
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

function getram
- result = do("ram used")
- return result

function trybad
- value = "unset"
- try
-- value = do("badcommandinsidefunction")
- catch
-- value = "caught"
- return value

ram = getram()
asserttext "do inside function", ram

bad = trybad()
assert "do failure caught inside function", bad, "caught"

say color("green", "40 do in functions complete")
