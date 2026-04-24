say color("cyan", "09 color")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

redtext = color("red", "red works")
greentext = color("green", "green works")
yellowtext = color("yellow", "yellow works")
cyantext = color("cyan", "cyan works")
boldtext = color("bold", "bold works")
dimtext = color("dim", "dim works")

say redtext
say greentext
say yellowtext
say cyantext
say boldtext
say dimtext

assert "color returns text red", type(redtext), "text"
assert "color returns text dim", type(dimtext), "text"

say color("green", "09 color complete")
