use "Modules/asserts.ixx"

say color("cyan", "hard 10 checker conservative errors")

function dangerous_if_called
- return number("FUNCTION_RUNTIME_ERROR")

caught = NO
try
- x = number("TRY_RUNTIME_ERROR")
catch
- caught = YES

assert "try bad number catchable", caught, YES

caught_file = NO
try
- y = read("StressTest/tmp/hard-missing-runtime-file.txt")
catch
- caught_file = YES

assert "try missing read catchable", caught_file, YES

still_ok = "yes"
if NO
- impossible = number("BRANCH_RUNTIME_ERROR")

assert "branch not executed", still_ok, "yes"

say color("green", "hard 10 complete")
