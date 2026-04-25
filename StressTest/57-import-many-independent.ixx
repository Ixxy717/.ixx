say color("cyan", "57 import many independent")
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
use "Modules/Nested/wrapper.ixx"
use std "date"

assert "helpers double", double(2), 4
assert "nested quad", nested_quad(2), 8
assert "stdlib month good", is_valid_month(6), YES
assert "stdlib month bad", is_valid_month(99), NO
say color("green", "57 import many independent complete")
