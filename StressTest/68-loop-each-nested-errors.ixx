say color("cyan", "68 loop each nested errors")
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


rows = "1,2,bad", "3,nope,4", "5,6,7"
total = 0
errors = 0

loop each row in rows
- cells = split(row, ",")
- loop each cell in cells
-- try
--- total = total + number(cell)
-- catch
--- errors = errors + 1

assert "nested parsed total", total, 28
assert "nested parse errors", errors, 2

say color("green", "68 loop each nested errors complete")
