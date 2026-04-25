use "Modules/asserts.ixx"
use "Modules/school.ixx"
use "Modules/reports.ixx"

section "scenario 09 student grade tracker"

path = "StressTest/tmp/scenario-09-grade-tracker.txt"
report_start "Grade Tracker", path

exam_avg = 82
homework_avg = 94
project_avg = 88

score = weighted_score(exam_avg, homework_avg, project_avg)
letter = letter_grade(score)
status = pass_status(score)

needed_for_a = 90 - score
if needed_for_a less than 0
- needed_for_a = 0

report_add path, "exam_avg", exam_avg
report_add path, "homework_avg", homework_avg
report_add path, "project_avg", project_avg
report_add path, "weighted_score", score
report_add path, "letter", letter
report_add path, "status", status
report_add path, "needed_for_a", needed_for_a
final = report_finish(path)

assert "weighted score", score, 86.5
assert "letter", letter, "B"
assert "status", status, "passing"
assert "needed for a", needed_for_a, 3.5
assert "report has letter", contains_line(final, "letter"), YES

done "scenario 09 complete"
