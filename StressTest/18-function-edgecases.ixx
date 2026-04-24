say color("cyan", "18 function edgecases")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

function early value
- if value at least 10
-- return "big"
- return "small"

assert "early return big", early(10), "big"
assert "early return small", early(2), "small"

function noargs
- return "ok"

assert "zero arg expression call", noargs(), "ok"

function chaina x
- return chainb(x + 1)

function chainb y
- return chainc(y + 1)

function chainc z
- return z + 1

assert "function chain", chaina(1), 4

function localbuilder base
- part = base + "-local"
- return part

built = localbuilder("ixx")
assert "local builder", built, "ixx-local"

leak = "none"
try
- say part
- leak = "bad"
catch
- leak = "blocked"
assert "local var hidden", leak, "blocked"

say color("green", "18 function edgecases complete")
