say color("cyan", "64 loop each file report")
function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

function assertyes name, value
- if value
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: YES"
- say "Got: NO"
- crash = number("ASSERT_FAIL")

function asserttext name, value
- assert name + " type", type(value), "text"
- ok = NO
- if count(value) more than 0
-- ok = YES
- assertyes name + " not empty", ok

paths = "StressTest/tmp/loop-each-64-a.txt", "StressTest/tmp/loop-each-64-b.txt", "StressTest/tmp/loop-each-64-c.txt"

idx = 1
loop each path in paths
- write path, "file " + idx
- idx = idx + 1

combined = ""
loop each path in paths
- combined = combined + read(path) + "|"

assert "file report combined", combined, "file 1|file 2|file 3|"
assert "last idx after loop", idx, 4

exists_count = 0
loop each path in paths
- if exists(path)
-- exists_count = exists_count + 1

assert "all loop files exist", exists_count, 3
say color("green", "64 loop each file report complete")
