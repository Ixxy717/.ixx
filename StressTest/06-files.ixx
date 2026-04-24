say color("cyan", "06 files")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

path = "StressTest/tmp/io-main.txt"
write path, "Hello"
append path, " IXX"
content = read(path)
assert "write append read", content, "Hello IXX"

yespath = "StressTest/tmp/write-yes.txt"
write yespath, YES
yescontent = read(yespath)
assert "write YES display", yescontent, "YES"

nopath = "StressTest/tmp/write-no.txt"
write nopath, NO
nocontent = read(nopath)
assert "write NO display", nocontent, "NO"

nothingpath = "StressTest/tmp/write-nothing.txt"
write nothingpath, nothing
nothingcontent = read(nothingpath)
assert "write nothing display", nothingcontent, "nothing"

appendpath = "StressTest/tmp/append-values.txt"
write appendpath, "Start:"
append appendpath, YES
append appendpath, "-"
append appendpath, NO
append appendpath, "-"
append appendpath, nothing
appendcontent = read(appendpath)
assert "append values display", appendcontent, "Start:YES-NO-nothing"

fixture = "StressTest/tmp/readlines-fixture.txt"
lines = readlines(fixture)
linecount = count(lines)
assert "readlines count", linecount, 3
assert "readlines first", first(lines), "alpha"
assert "readlines last", last(lines), "gamma"

existsyes = exists(path)
assert "exists yes", existsyes, YES

existsno = exists("StressTest/tmp/this-file-should-not-exist.txt")
assert "exists no", existsno, NO

say color("green", "06 files complete")
