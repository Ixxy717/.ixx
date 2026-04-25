say color("cyan", "50 import top level side effects blocked")
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

use "Modules/SideEffects/top-level-write.ixx"

marker = "StressTest/tmp/import-top-level-should-not-run.txt"
exists_marker = exists(marker)

assert "imported top-level write did not run", exists_marker, NO
assert "imported helper still callable", side_effect_helper(), "helper ran"
say color("green", "50 import top level side effects blocked complete")
