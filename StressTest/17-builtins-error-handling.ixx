say color("cyan", "17 builtins error handling")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

caught = NO
try
- bad = count(42)
catch
- caught = YES
assert "count number fails", caught, YES

caught = NO
try
- bad = first("notlist")
catch
- caught = YES
assert "first text fails", caught, YES

caught = NO
try
- bad = last(123)
catch
- caught = YES
assert "last number fails", caught, YES

caught = NO
try
- bad = sort("abc")
catch
- caught = YES
assert "sort text fails", caught, YES

caught = NO
try
- bad = reverse(123)
catch
- caught = YES
assert "reverse number fails", caught, YES

caught = NO
try
- bad = number("abc")
catch
- caught = YES
assert "number abc fails", caught, YES

say color("green", "17 builtins error handling complete")
