say color("cyan", "15 try catch edgecases")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

caught = NO
message = "none"

try
- x = number("not-a-number")
catch
- caught = YES
- message = type(error)

assert "number error caught", caught, YES
assert "error is text", message, "text"

continued = "yes"
assert "continued after catch", continued, "yes"

silent = "before"
try
- bad = number("still-bad")
silent = "after"
assert "silent try continues", silent, "after"

outer = "unset"
try
- try
-- badinner = read("StressTest/tmp/no-inner-file.txt")
- catch
-- outer = "inner handled"
catch
- outer = "outer handled"
assert "inner catch handles", outer, "inner handled"

outer = "unset"
ok = nothing
try
- try
-- ok = "fine"
- catch
-- outer = "inner catch should not run"
- outer = ok
catch
- outer = "outer catch should not run"
assert "nested try success with predeclared var", outer, "fine"

say color("green", "15 try catch edgecases complete")
