say color("cyan", "66 loop each imported helpers")
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

use "Modules/loop-each-extra.ixx"

numbers = 10, 20, 30, 40
assert "imported sum_items", sum_items(numbers), 100

words = "alpha", "beta", "gamma"
assert "imported join_items", join_items(words, " / "), "alpha / beta / gamma"

files = "good-a.txt", "bad-b.tmp", "good-c.txt", "bad-d.tmp"
assert "imported count contains", count_contains(files, "bad"), 2
assert "imported first match", first_match(files, "good"), "good-a.txt"

say color("green", "66 loop each imported helpers complete")
