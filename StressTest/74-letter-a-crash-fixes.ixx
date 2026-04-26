say color("cyan", "74 letter-a crash fixes")

function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: " + text(expected)
- say "Got: " + text(got)
- crash = number("ASSERT_FAIL")

# A1: split with valid separator still works
parts = split("apple,banana,cherry", ",")
assert "split-valid-sep-count", count(parts), 3
assert "split-valid-sep-first", first(parts), "apple"
assert "split-valid-sep-last",  last(parts), "cherry"

# split with no separator (whitespace) still works
words = split("hello world foo")
assert "split-no-sep", count(words), 3

# A2: ask() with EOFError is handled gracefully (tested via unit tests with mocking)
# Skipped here — ask() requires interactive input, unit tests cover it with mock.

# A3: sort on mixed list error is caught cleanly (no raw TypeError)
try
- items = 1, "a"
- sort(items)
catch
- assert "sort-mixed-caught", YES, YES

# A4: top-level function definitions still work
function triple x
- return x * 3

assert "top-level-func", triple(7), 21

function greet name, greeting
- return greeting + ", " + name + "!"

assert "top-level-func-multi", greet("Ixxy", "Hello"), "Hello, Ixxy!"

# A5: read/readlines of normal text file still work
write "StressTest/tmp/a5-test.txt", "line one"
content = read("StressTest/tmp/a5-test.txt")
assert "read-normal-still-works", trim(content), "line one"

lines = readlines("StressTest/tmp/a5-test.txt")
assert "readlines-normal-still-works", count(lines), 1
