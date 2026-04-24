say color("cyan", "29 type display matrix")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

txt = "hello"
num = 123
flag = YES
off = NO
nil = nothing
lst = "a", "b"

assert "type text", type(txt), "text"
assert "type number", type(num), "number"
assert "type YES", type(flag), "bool"
assert "type NO", type(off), "bool"
assert "type nothing", type(nil), "nothing"
assert "type list", type(lst), "list"

assert "text text", text(txt), "hello"
assert "text number", text(num), "123"
assert "text YES", text(flag), "YES"
assert "text NO", text(off), "NO"
assert "text nothing", text(nil), "nothing"
assert "text list", text(lst), "a, b"

say color("green", "29 type display matrix complete")
