say color("cyan", "30 realistic mini app")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

function grade score
- if score at least 90
-- return "A"
- if score at least 80
-- return "B"
- if score at least 70
-- return "C"
- if score at least 60
-- return "D"
- return "F"

function status gradevalue
- if gradevalue is "A"
-- return "excellent"
- if gradevalue is "B"
-- return "good"
- if gradevalue is "C"
-- return "passing"
- return "needs work"

scores = 92, 81, 70, 59
best = max(scores)
worst = min(scores)
assert "best score", best, 92
assert "worst score", worst, 59

g1 = grade(92)
g2 = grade(81)
g3 = grade(70)
g4 = grade(59)

assert "grade A", g1, "A"
assert "grade B", g2, "B"
assert "grade C", g3, "C"
assert "grade F", g4, "F"

s1 = status(g1)
s4 = status(g4)
assert "status A", s1, "excellent"
assert "status F", s4, "needs work"

report = "Best=" + best + ", Worst=" + worst + ", Top=" + g1
write "StressTest/tmp/mini-report.txt", report
readback = read("StressTest/tmp/mini-report.txt")
assert "report roundtrip", readback, "Best=92, Worst=59, Top=A"

say color("green", "30 realistic mini app complete")
