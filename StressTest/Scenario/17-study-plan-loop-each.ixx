use "Modules/asserts.ixx"
use "Modules/reports.ixx"
use "Modules/school.ixx"
use std "time"

section "scenario 17 study plan loop each"

path = "StressTest/tmp/scenario-17-study-plan.txt"
report_start "Study Plan", path

scores = 88, 92, 76, 84
total = 0
loop each score in scores
- total = total + score

average = round(total / count(scores), 1)
letter = letter_grade(average)
status = pass_status(average)

tasks = "review notes", "practice problems", "submit lab", "sleep"
task_count = 0
loop each task in tasks
- report_add path, "task", task
- task_count = task_count + 1

greeting = time_greeting(9)
report_add path, "average", average
report_add path, "letter", letter
report_add path, "status", status
report_add path, "greeting", greeting
final = report_finish(path)

assert "average", average, 85
assert "letter", letter, "B"
assert "status", status, "passing"
assert "task count", task_count, 4
assert "greeting", greeting, "Good morning"
assert "report has sleep", contains_line(final, "sleep"), YES

done "scenario 17 complete"
