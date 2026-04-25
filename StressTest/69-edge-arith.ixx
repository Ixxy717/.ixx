function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

assert "int division exact", 10 / 2, 5
assert "float division", type(10 / 3), "number"
assert "string concat", "hello" + " world", "hello world"
assert "string plus number", "x=" + text(42), "x=42"
assert "negative", -5 + 3, -2
assert "multiply", 4 * 3, 12

try
- bad = 1, 2 - 1
catch
- assert "list minus caught", YES, YES

try
- bad = nothing + 1
catch
- assert "nothing plus caught", YES, YES

try
- bad = "hello" + nothing
catch
- assert "text plus nothing caught", YES, YES

try
- bad = 1, 2 * 2
catch
- assert "list times caught", YES, YES
