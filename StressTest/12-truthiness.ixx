say color("cyan", "12 truthiness")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

result = "unset"
if YES
- result = "yes true"
assert "YES truthy", result, "yes true"

result = "unchanged"
if NO
- result = "bad"
assert "NO falsy", result, "unchanged"

result = "unchanged"
if nothing
- result = "bad"
assert "nothing falsy", result, "unchanged"

result = "unchanged"
if 0
- result = "bad"
assert "zero falsy", result, "unchanged"

result = "unchanged"
if 1
- result = "one true"
assert "one truthy", result, "one true"

result = "unchanged"
if ""
- result = "bad"
assert "empty text falsy", result, "unchanged"

result = "unchanged"
if "hello"
- result = "text true"
assert "nonempty text truthy", result, "text true"

items = "one", "two"
result = "unchanged"
if items
- result = "list true"
assert "nonempty list truthy", result, "list true"

notresult = "unset"
if not 0
- notresult = "not zero true"
assert "not zero", notresult, "not zero true"

say color("green", "12 truthiness complete")
