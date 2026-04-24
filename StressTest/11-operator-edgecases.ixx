say color("cyan", "11 operator edgecases")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

a = 8
b = 3

assert "add numbers", a + b, 11
assert "sub numbers", a - b, 5
assert "mul numbers", a * b, 24
assert "div numbers", a / b, 2.6666666666666665
assert "paren precedence", (a + b) * 2, 22
assert "unary negative var", -a, -8
assert "double negative math", a - -b, 11

s1 = "I"
s2 = "XX"
assert "text plus text", s1 + s2, "IXX"
assert "text plus number", "v" + 6, "v6"
assert "number plus text", 6 + ".1", "6.1"

yes_text = "flag=" + text(YES)
nothing_text = "value=" + text(nothing)
assert "text yes via text builtin", yes_text, "flag=YES"
assert "text nothing via text builtin", nothing_text, "value=nothing"

say color("green", "11 operator edgecases complete")
