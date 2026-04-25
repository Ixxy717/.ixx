# Quiz scorer with multiple questions and a final grade

function score_to_grade pct
- if pct at least 90
-- return "A"
- if pct at least 80
-- return "B"
- if pct at least 70
-- return "C"
- if pct at least 60
-- return "D"
- return "F"

function quiz_result name, correct, total
- pct = round(correct * 100 / total)
- grade = score_to_grade(pct)
- say name + ": " + correct + "/" + total + " (" + pct + "%) — Grade " + grade
- return grade

say "=== QUIZ RESULTS: 5 Questions Each ==="

g1 = quiz_result("Alice",  5, 5)
g2 = quiz_result("Bob",    3, 5)
g3 = quiz_result("Carol",  4, 5)
g4 = quiz_result("David",  2, 5)
g5 = quiz_result("Eve",    5, 5)

passing = 0
grades = g1, g2, g3, g4, g5
loop each g in grades
- if g is not "F"
-- passing = passing + 1

say "---"
say "Students passing: " + passing + " / " + count(grades)
say "Top grade count (A): " + 2
