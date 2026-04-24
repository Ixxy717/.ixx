say color("cyan", "21 color display matrix")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

names = "red", "green", "yellow", "cyan", "bold", "dim"
line = join(names, ", ")
say "Supported colors: {line}"

r = color("red", "R")
g = color("green", "G")
y = color("yellow", "Y")
c = color("cyan", "C")
b = color("bold", "B")
d = color("dim", "D")

assert "red text type", type(r), "text"
assert "green text type", type(g), "text"
assert "yellow text type", type(y), "text"
assert "cyan text type", type(c), "text"
assert "bold text type", type(b), "text"
assert "dim text type", type(d), "text"

say r
say g
say y
say c
say b
say d

say color("green", "21 color display matrix complete")
