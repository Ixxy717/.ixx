say color("cyan", "60 loop each nested")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

rows = 1, 2, 3
cols = 10, 100
total = 0

loop each r in rows
- loop each c in cols
-- total = total + r * c

assert "nested loop each sum", total, 660

pairs_count = 0
outer = "a", "b"
inner = "x", "y", "z"

loop each o in outer
- loop each i in inner
-- pairs_count = pairs_count + 1

assert "nested pair count", pairs_count, 6

say color("green", "60 loop each nested complete")
