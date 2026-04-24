# Leading comment should be ignored

say color("cyan", "22 comments and format")

function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")


# Comment between function and code
value = 1

# Inline comments should be ignored too
value = value + 1 # becomes 2

assert "inline comment ignored", value, 2

if value is 2
- value = value + 3
- value = value + 0 # comment after statement

assert "comments inside block", value, 5

loop value more than 3
- value = value - 1 # lower value

assert "loop with comments", value, 3

say color("green", "22 comments and format complete")
