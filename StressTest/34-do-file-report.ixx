say color("cyan", "34 do file report")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

function assertyes name, value
- if value
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: YES"
- say "Got: NO"
- crash = number("ASSERT_FAIL")

function asserttext name, value
- t = type(value)
- assert name, t, "text"
- ok = NO
- if count(value) more than 0
-- ok = YES
- assertyes name + " not empty", ok

path = "StressTest/tmp/do-report.txt"

ram = do("ram used")
cpu = do("cpu info")
ip = do("ip local")

write path, "IXX system report"
append path, " | RAM: "
append path, ram
append path, " | CPU: "
append path, cpu
append path, " | IP: "
append path, ip

report = read(path)
assert "report type", type(report), "text"

ok = NO
if count(report) more than count(ram)
- ok = YES
assert "report includes command output", ok, YES

existsyes = exists(path)
assert "report exists", existsyes, YES

say color("green", "34 do file report complete")
