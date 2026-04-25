say color("cyan", "55 import try catch call")
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
use "Modules/runtime-error-helper.ixx"

caught = NO
try
- value = imported_bad_number()
catch
- caught = YES

assert "imported runtime error catchable", caught, YES

caught_file = NO
try
- value = imported_missing_file()
catch
- caught_file = YES

assert "imported missing file catchable", caught_file, YES
assert "normal imported call still works after catch", double(6), 12
say color("green", "55 import try catch call complete")
