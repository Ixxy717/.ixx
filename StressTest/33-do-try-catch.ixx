say color("cyan", "33 do try catch")
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

caught = NO
errtext = ""

try
- bad = do("thiscommanddoesnotexist")
catch
- caught = YES
- errtext = error

assert "unknown do command caught", caught, YES
asserttext "unknown do error text", errtext

caught = NO
errtext = ""
try
- bad = do(42)
catch
- caught = YES
- errtext = error

assert "do nontext caught", caught, YES
asserttext "do nontext error text", errtext

caught = NO
errtext = ""
try
- bad = do("")
catch
- caught = YES
- errtext = error

assert "do empty caught", caught, YES
asserttext "do empty error text", errtext

say color("green", "33 do try catch complete")
