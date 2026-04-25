use "Modules/asserts.ixx"

say color("cyan", "hard 61 try catch heavy")
caught = 0
n = 30
loop n more than 0
- try
-- bad = number("loop-bad-number")
- catch
-- caught = caught + 1
- n = n - 1

assert "caught 30 errors", caught, 30

safe = "ok"
if NO
- bad = number("branch-bad-number")

assert "branch skipped stays ok", safe, "ok"
say color("green", "hard 61 complete")
