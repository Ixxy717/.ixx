say color("cyan", "67 loop each split sort pipeline")
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


raw = "delta,alpha,charlie,bravo"
parts = split(raw, ",")
sorted = sort(parts)

joined = ""
loop each part in sorted
- joined = joined + upper(part) + "|"

assert "loop sorted uppercase join", joined, "ALPHA|BRAVO|CHARLIE|DELTA|"

reversed = reverse(sorted)
first_seen = ""
loop each item in reversed
- if first_seen is ""
-- first_seen = item

assert "reverse first seen", first_seen, "delta"

counted = 0
loop each part in split("one two three four")
- counted = counted + 1

assert "split default loop count", counted, 4
say color("green", "67 loop each split sort pipeline complete")
