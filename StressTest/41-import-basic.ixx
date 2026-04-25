say color("cyan", "41 import basic")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

use "Modules/helpers.ixx"

assert "double 5", double(5), 10
assert "triple 4", triple(4), 12
assert "greet", greet("World"), "Hello, World!"
