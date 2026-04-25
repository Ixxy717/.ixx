say color("cyan", "42 import no toplevel")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

use "Modules/helpers.ixx"

assert "import top-level say suppressed", double(3), 6
