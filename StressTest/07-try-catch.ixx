say color("cyan", "07 try catch")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

status = "start"
try
- status = "try success"
catch
- status = "catch should not run"
assert "try success path", status, "try success"

caught = NO
errtype = "none"
try
- content = read("StressTest/tmp/missing-file-for-catch.txt")
catch
- caught = YES
- errtype = type(error)
assert "catch ran", caught, YES
assert "error variable type", errtype, "text"

aftercatch = "continued"
assert "execution continued", aftercatch, "continued"

silent = "before"
try
- bad = read("StressTest/tmp/missing-file-for-silent-try.txt")
assert "silent try continued", silent, "before"

tryvalue = nothing
try
- tryvalue = "survived"
catch
- tryvalue = "failed"
assert "predeclared try variable survives", tryvalue, "survived"

leakresult = "unknown"
try
- localonly = "secret"
catch
- leakresult = "unexpected catch"

try
- say localonly
- leakresult = "leaked"
catch
- leakresult = "blocked"
assert "try local does not escape", leakresult, "blocked"

nested = "start"
try
- try
-- missing = read("StressTest/tmp/missing-inner.txt")
- catch
-- nested = "inner caught"
catch
- nested = "outer caught"
assert "nested try catch", nested, "inner caught"

say color("green", "07 try catch complete")
