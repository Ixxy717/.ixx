say color("cyan", "45 import file helper")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

use "Modules/file-helper.ixx"

out = "StressTest/tmp/module-file-test.txt"
write_greeting out, "IXX"
content = read(out)
assert "file written by module function", content, "Hello from module, IXX!"
