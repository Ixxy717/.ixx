say color("cyan", "13 keyword identifiers")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

notify = "not keyword"
notable = "also ok"
returnvalue = 12
functionname = "fn"
containscheck = YES
tryhard = "try"
catchme = "catch"
iflocal = "if prefix"
elsewhere = "else prefix"
loopback = "loop prefix"

assert "notify identifier", notify, "not keyword"
assert "notable identifier", notable, "also ok"
assert "returnvalue identifier", returnvalue, 12
assert "functionname identifier", functionname, "fn"
assert "containscheck identifier", containscheck, YES
assert "tryhard identifier", tryhard, "try"
assert "catchme identifier", catchme, "catch"
assert "iflocal identifier", iflocal, "if prefix"
assert "elsewhere identifier", elsewhere, "else prefix"
assert "loopback identifier", loopback, "loop prefix"

function tryhardfn value
- catchvalue = value + 1
- return catchvalue

assert "keyword prefix function", tryhardfn(9), 10

say color("green", "13 keyword identifiers complete")
