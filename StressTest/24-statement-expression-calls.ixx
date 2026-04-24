say color("cyan", "24 statement expression calls")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

seen = "none"

function mark text
- say "Marked {text}"
- return text

function add a, b
- return a + b

function calladd a, b
- result = add(a, b)
- return result

marked = mark("statement call")
assert "function return captures value", marked, "statement call"
assert "function write does not update outer", seen, "none"

value = calladd(20, 22)
assert "expression call nested", value, 42

shown = text(add(1, 2))
assert "builtin around user call", shown, "3"

say add(3, 4)
assert "say expression call still continues", add(5, 5), 10

say color("green", "24 statement expression calls complete")
