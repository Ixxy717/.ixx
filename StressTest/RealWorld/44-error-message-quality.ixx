# Trigger runtime errors and verify error messages are caught cleanly

errors_caught = 0

# 1. Bad number conversion
try
- bad = number("definitely not a number")
catch
- errors_caught = errors_caught + 1
- say "1. number() error: " + error

# 2. Missing file read
try
- bad = read("StressTest/tmp/rw-44-missing-xyz-abc.txt")
catch
- errors_caught = errors_caught + 1
- say "2. read() error: " + error

# 3. first() on non-list
try
- bad = first("I am text")
catch
- errors_caught = errors_caught + 1
- say "3. first(text) error: " + error

# 4. count() on wrong type
try
- bad = count(YES)
catch
- errors_caught = errors_caught + 1
- say "4. count(bool) error: " + error

# 5. upper() on number
try
- bad = upper(42)
catch
- errors_caught = errors_caught + 1
- say "5. upper(number) error: " + error

# 6. round() on text
try
- bad = round("abc")
catch
- errors_caught = errors_caught + 1
- say "6. round(text) error: " + error

# 7. Division by zero
try
- bad = 10 / 0
catch
- errors_caught = errors_caught + 1
- say "7. divide-by-zero error: " + error

# 8. loop each on non-list
try
- bad_iter = "I am text"
- loop each x in bad_iter
-- say x
catch
- errors_caught = errors_caught + 1
- say "8. loop each non-list: " + error

say "---"
say "Total errors caught: " + errors_caught + "/8"

if errors_caught is 8
- say "PASS: all 8 errors caught"
