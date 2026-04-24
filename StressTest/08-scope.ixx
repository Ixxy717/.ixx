say color("cyan", "08 scope")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

flag = "before"
if YES
- flag = "after"
assert "if updates predeclared", flag, "after"

iflocal = "unknown"
if YES
- onlyif = "local"

try
- say onlyif
- iflocal = "leaked"
catch
- iflocal = "blocked"
assert "if local does not escape", iflocal, "blocked"

i = 3
sum = 0
loop i more than 0
- sum = sum + i
- looplocal = "hidden"
- i = i - 1
assert "loop updates predeclared", sum, 6

looplocalresult = "unknown"
try
- say looplocal
- looplocalresult = "leaked"
catch
- looplocalresult = "blocked"
assert "loop local does not escape", looplocalresult, "blocked"

global = "global"

function localtest param
- localvalue = "inside"
- global = "local shadow"
- return param

result = localtest("returned")
assert "function return", result, "returned"
assert "function shadow global unchanged", global, "global"

paramleak = "unknown"
try
- say param
- paramleak = "leaked"
catch
- paramleak = "blocked"
assert "function param does not leak", paramleak, "blocked"

localleak = "unknown"
try
- say localvalue
- localleak = "leaked"
catch
- localleak = "blocked"
assert "function local does not leak", localleak, "blocked"

try
- bad = read("StressTest/tmp/missing-error-scope.txt")
catch
- seen = type(error)

errorleak = "unknown"
try
- say error
- errorleak = "leaked"
catch
- errorleak = "blocked"
assert "catch error does not leak", errorleak, "blocked"

say color("green", "08 scope complete")
