say color("cyan", "58 import output roundtrip")
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

use "Modules/helpers.ixx"

path = "StressTest/tmp/import-output-roundtrip.txt"
value = greet("Roundtrip")
write path, value
back = read(path)

assert "import output write read", back, "Hello, Roundtrip!"
say color("green", "58 import output roundtrip complete")
