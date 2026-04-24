say color("cyan", "25 readlines processing")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

path = "StressTest/tmp/readlines-fixture.txt"

lines = readlines(path)
assert "line count three", count(lines), 3
assert "line first alpha", first(lines), "alpha"
assert "line last gamma", last(lines), "gamma"

sorted = sort(lines)
sortedtext = join(sorted, "|")
assert "line sort", sortedtext, "alpha|beta|gamma"

rev = reverse(sorted)
revtext = join(rev, "|")
assert "line reverse", revtext, "gamma|beta|alpha"

say color("green", "25 readlines processing complete")
