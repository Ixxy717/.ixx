say color("cyan", "75 letter-b display fixes")

function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: " + text(expected)
- say "Got: " + text(got)
- crash = number("ASSERT_FAIL")

# B1: join displays IXX values
vals = YES, NO, nothing
joined = join(vals, " ")
assert "join-yes-no-nothing", joined, "YES NO nothing"

nums = 1, 2, 3
assert "join-numbers", join(nums, "-"), "1-2-3"

words = "a", "b", "c"
assert "join-default-sep", join(words), "a, b, c"

# B2: replace replacement uses IXX display
assert "replace-yes",     replace("x is here", "here", YES),     "x is YES"
assert "replace-no",      replace("x is here", "here", NO),      "x is NO"
assert "replace-nothing", replace("x is here", "here", nothing), "x is nothing"
assert "replace-normal",  replace("hello world", "world", "IXX"), "hello IXX"

# B4: number() error uses IXX display (message tested in unit tests)
try
- say number(nothing)
catch
- assert "number-nothing-caught", YES, YES

# B5: contains uses IXX display for rhs
r1 = "nothing here" contains nothing
assert "contains-nothing-yes", r1, YES

r2 = "YES value" contains YES
assert "contains-yes-yes", r2, YES

r3 = "NO value" contains NO
assert "contains-no-yes", r3, YES

r4 = "True value" contains YES
assert "contains-true-no", r4, NO

r5 = "None value" contains nothing
assert "contains-none-no", r5, NO

items = 1, 2, 3
r6 = items contains 2
assert "contains-list", r6, YES

# B6: min/max with valid numbers still work
assert "min-numbers", min(3, 7), 3
assert "max-numbers", max(3, 7), 7
items = 3, 1, 4, 1, 5
assert "min-list",    min(items), 1
assert "max-list",    max(items), 5

# B6: min/max reject booleans
try
- say min(YES, 2)
catch
- assert "min-bool-caught", YES, YES

try
- say max(NO, 2)
catch
- assert "max-bool-caught", YES, YES

# B7: round with valid args still works
assert "round-decimals", round(3.14159, 2), 3.14
assert "round-default",  round(3.7),        4

# B7: round rejects bool digits
try
- say round(3.14, YES)
catch
- assert "round-bool-digits-caught", YES, YES

# B8: list arithmetic caught
try
- a = 1, 2, 3
- b = 4, 5, 6
- say a + b
catch
- assert "list-plus-list-caught", YES, YES

try
- a = 1, 2, 3
- say a * 3
catch
- assert "list-times-num-caught", YES, YES

# Normal arithmetic still works
assert "text-plus-num",    "count: " + 5, "count: 5"
assert "num-plus-text",    5 + " items",  "5 items"
assert "num-arithmetic",   3 + 4,         7
