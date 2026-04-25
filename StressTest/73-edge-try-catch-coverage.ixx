function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

caught_file = NO
try
- x = read("StressTest/tmp/does-not-exist-73.txt")
catch
- caught_file = YES
assert "read missing file caught", caught_file, YES

caught_num = NO
try
- bad = number("not-a-number")
catch
- caught_num = YES
assert "bad number caught", caught_num, YES

caught_compare = NO
try
- result = "abc" more than 1
catch
- caught_compare = YES
assert "type compare caught", caught_compare, YES

caught_div = NO
try
- result = 10 / 0
catch
- caught_div = YES
assert "divide by zero caught", caught_div, YES

caught_loop_each = NO
try
- loop each x in "not-a-list"
-- say x
catch
- caught_loop_each = YES
assert "loop each non-list caught", caught_loop_each, YES

caught_arith = NO
try
- bad = "hello" + nothing
catch
- caught_arith = YES
assert "text plus nothing caught", caught_arith, YES

caught_list_arith = NO
try
- mylist = 1, 2, 3
- bad = mylist - 1
catch
- caught_list_arith = YES
assert "list minus caught", caught_list_arith, YES

caught_min = NO
try
- bad = min(1, "a")
catch
- caught_min = YES
assert "min mixed types caught", caught_min, YES
