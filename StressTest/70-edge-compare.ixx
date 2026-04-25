function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

assert "is number", 1 is 1, YES
assert "is text", "a" is "a", YES
assert "is not", 1 is not 2, YES
assert "is nothing", nothing is nothing, YES
assert "bool is", YES is YES, YES
assert "less than", 1 less than 2, YES
assert "more than", 5 more than 3, YES

a = 3
b = 3
assert "at least", a at least b, YES

c = 2
d = 5
assert "at most", c at most d, YES

mylist = 1, 2, 3
assert "contains list YES", mylist contains 2, YES
assert "contains list NO", mylist contains 9, NO
assert "contains text YES", "hello" contains "ell", YES
assert "contains text NO", "hello" contains "xyz", NO

try
- x = "abc" more than 1
catch
- assert "compare text vs number caught", YES, YES

try
- y = 1 less than "two"
catch
- assert "compare number vs text caught", YES, YES
