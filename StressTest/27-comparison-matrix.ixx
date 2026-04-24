say color("cyan", "27 comparison matrix")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

a = 5
b = 10
same = 5

r = NO
if a is same
- r = YES
assert "number is", r, YES

r = NO
if a is not b
- r = YES
assert "number is not", r, YES

r = NO
if a less than b
- r = YES
assert "less than", r, YES

r = NO
if b more than a
- r = YES
assert "more than", r, YES

r = NO
if a at least same
- r = YES
assert "at least equal", r, YES

r = NO
if a at most same
- r = YES
assert "at most equal", r, YES

texta = "abc"
textb = "abc"
r = NO
if texta is textb
- r = YES
assert "text is", r, YES

r = NO
if "abcdef" contains "cd"
- r = YES
assert "text contains inline", r, YES

say color("green", "27 comparison matrix complete")
