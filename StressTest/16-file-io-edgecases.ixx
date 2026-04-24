say color("cyan", "16 file io edgecases")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

folderpath = "StressTest/tmp"
folderexists = exists(folderpath)
assert "exists folder", folderexists, YES

newfile = "StressTest/tmp/append-creates.txt"
try
- old = read(newfile)
catch
- noop = "missing ok"

append newfile, "created"
created = read(newfile)
assert "append creates file", created, "created"

overwrite = "StressTest/tmp/overwrite.txt"
write overwrite, "first"
write overwrite, "second"
overcontent = read(overwrite)
assert "write overwrites", overcontent, "second"

emptyfile = "StressTest/tmp/empty.txt"
write emptyfile, ""
emptycontent = read(emptyfile)
assert "read empty file", emptycontent, ""

emptylines = readlines(emptyfile)
emptylinecount = count(emptylines)
assert "readlines empty count", emptylinecount, 0

mixed = "StressTest/tmp/mixed-display.txt"
write mixed, 42
append mixed, "|"
append mixed, YES
append mixed, "|"
append mixed, nothing
mixedcontent = read(mixed)
assert "mixed display writes", mixedcontent, "42|YES|nothing"

say color("green", "16 file io edgecases complete")
