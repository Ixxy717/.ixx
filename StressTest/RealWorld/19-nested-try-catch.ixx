# Nested try/catch — try inside catch, catch inside try

outer_caught = NO
inner_caught = NO

try
- x = number("not a number")
catch
- outer_caught = YES
- say "Outer catch: " + error
- try
-- y = number("also not a number")
- catch
-- inner_caught = YES
-- say "Inner catch: " + error
-- say "Nested error handling works"

say "Outer caught: " + text(outer_caught)
say "Inner caught: " + text(inner_caught)

# Pattern 2: outer succeeds, inner catches something inside the try body
outer2_ran = NO
inner2_ran = NO

try
- outer2_ran = YES
- try
-- bad = read("StressTest/tmp/rw-19-definitely-missing-xyz.txt")
- catch
-- inner2_ran = YES
-- say "Inner2 caught missing file: " + error
catch
- say "UNEXPECTED: outer2 catch should not fire"

say "Outer2 ran: " + text(outer2_ran)
say "Inner2 ran: " + text(inner2_ran)

# Pattern 3: double nesting
depth1 = NO
depth2 = NO
depth3 = NO

try
- depth1 = YES
- try
-- depth2 = YES
-- try
--- depth3 = YES
--- bad = number("deep failure")
-- catch
--- say "Depth 3 caught"
- catch
-- say "UNEXPECTED: depth2 catch should not fire"
catch
- say "UNEXPECTED: depth1 catch should not fire"

say "depth1=" + text(depth1) + " depth2=" + text(depth2) + " depth3=" + text(depth3)
