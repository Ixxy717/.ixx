say color("cyan", "35 do output processing")
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

raw = do("ram used")
clean = trim(raw)
uppered = upper(clean)
texttype = type(uppered)

assert "processed do type", texttype, "text"

ok = NO
if count(uppered) more than 0
- ok = YES
assert "processed do not empty", ok, YES

parts = split(clean)
joined = join(parts, " ")
assert "split join command output type", type(joined), "text"

ok = NO
if count(joined) more than 0
- ok = YES
assert "split join command output not empty", ok, YES

say color("green", "35 do output processing complete")
