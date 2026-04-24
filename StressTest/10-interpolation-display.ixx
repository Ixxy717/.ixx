say color("cyan", "10 interpolation display")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

name = "Ixxy"
num = 42
truth = YES
lie = NO
empty = nothing
items = "alpha", "beta", "ixx"

line1 = "Name={name}"
line2 = "Number={num}"
line3 = "Truth={truth}"
line4 = "Lie={lie}"
line5 = "Empty={empty}"
line6 = "Items={items}"
line7 = "Missing={ghost}"

assert "interpolate text", line1, "Name=Ixxy"
assert "interpolate number", line2, "Number=42"
assert "interpolate YES", line3, "Truth=YES"
assert "interpolate NO", line4, "Lie=NO"
assert "interpolate nothing", line5, "Empty=nothing"
assert "interpolate list", line6, "Items=alpha, beta, ixx"
assert "undefined interpolation", line7, "Missing={?ghost}"

say color("green", "10 interpolation display complete")
