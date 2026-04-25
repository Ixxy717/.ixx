say color("cyan", "32 do aliases")
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

memory = do("memory used")
asserttext "do memory used alias", memory

processor = do("processor cores")
asserttext "do processor cores alias", processor

storage = do("storage space")
asserttext "do storage space alias", storage

wifi = do("wifi ip")
assert "wifi ip type", type(wifi), "text"

say color("green", "32 do aliases complete")
