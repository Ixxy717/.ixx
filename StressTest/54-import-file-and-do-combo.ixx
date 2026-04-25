say color("cyan", "54 import file and do combo")
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

use "Modules/file-helper.ixx"
use "Modules/do-helper.ixx"

path = "StressTest/tmp/import-do-file-combo.txt"
ram = get_ram_info()
write_greeting path, ram
content = read(path)

assert "combo file content type", type(content), "text"
ok = NO
if content contains "Hello from module"
- ok = YES
assert "combo file contains module prefix", ok, YES
say color("green", "54 import file and do combo complete")
