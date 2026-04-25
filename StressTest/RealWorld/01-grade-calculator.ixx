# Grade calculator — averages a list of scores and assigns a letter grade

scores = 85, 92, 78, 88, 95, 70, 91, 83, 76, 89

total = 0
loop each s in scores
- total = total + s

avg = total / count(scores)
avg_rounded = round(avg, 1)

grade = "F"
if avg_rounded at least 90
- grade = "A"
if avg_rounded at least 80 and avg_rounded less than 90
- grade = "B"
if avg_rounded at least 70 and avg_rounded less than 80
- grade = "C"
if avg_rounded at least 60 and avg_rounded less than 70
- grade = "D"

say "Scores: " + join(scores, ", ")
say "Average: " + avg_rounded
say "Grade: " + grade
say "Students: " + count(scores)
