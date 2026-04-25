say color("cyan", "43 import chained")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

use "Modules/chain-a.ixx"

assert "chain_a_value", chain_a_value(), "from_a"
assert "chain_b_value (transitive)", chain_b_value(), "from_b"
