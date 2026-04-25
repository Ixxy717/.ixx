say color("cyan", "44 import with local function")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

use "Modules/helpers.ixx"

function quadruple x
- return double(double(x))

assert "quadruple 5 via imported double", quadruple(5), 20
assert "local and imported coexist", greet("IXX"), "Hello, IXX!"
