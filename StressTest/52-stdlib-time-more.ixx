say color("cyan", "52 stdlib time more")
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

use std "time"

assert "minutes to hours", minutes_to_hours(90), 1.5
assert "seconds to minutes", seconds_to_minutes(150), 2.5
assert "time greeting boundary 12", time_greeting(12), "Good afternoon"
assert "time greeting boundary 18", time_greeting(18), "Good evening"
say color("green", "52 stdlib time more complete")
