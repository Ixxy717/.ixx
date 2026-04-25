say color("cyan", "62 loop each try catch")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

values = "5", "abc", "10", "xyz", "3"
total = 0
errors_caught = 0

loop each raw in values
- try
-- total = total + number(raw)
- catch
-- errors_caught = errors_caught + 1

assert "numeric sum with bad values", total, 18
assert "errors caught count", errors_caught, 2

paths = "StressTest/tmp/loop-each-62a.txt", "StressTest/tmp/loop-each-62b.txt"
idx = 1
loop each p in paths
- write p, "line " + idx
- idx = idx + 1

contents = ""
loop each p in paths
- contents = contents + read(p) + "|"

assert "loop each file write/read", contents, "line 1|line 2|"

say color("green", "62 loop each try catch complete")
