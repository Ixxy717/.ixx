say color("cyan", "37 check json companion")
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

say "This file is intentionally simple."
say "The run-all.ps1 runner performs the actual ixx check --json tests."
marker = "json companion ok"
assert "json companion marker", marker, "json companion ok"
say color("green", "37 check json companion complete")
