use "Modules/asserts.ixx"
use "Modules/reports.ixx"
use "Modules/school.ixx"
use "Modules/tickets.ixx"
use "Modules/ops.ixx"
use std "date"
use std "time"

section "scenario 20 all features loop each workflow"

path = "StressTest/tmp/scenario-20-all-features.txt"
report_start "All Features Workflow", path

# imports + stdlib
feb = days_in_february(2024)
greeting = time_greeting(10)

# loop each + math + school module
scores = 91, 84, 77, 88
total = 0
loop each score in scores
- total = total + score

average = round(total / count(scores), 1)
letter = letter_grade(average)

# loop each + try/catch
raw_values = "5", "bad", "10", "nope", "15"
parsed_total = 0
parse_errors = 0
loop each raw in raw_values
- try
-- parsed_total = parsed_total + number(raw)
- catch
-- parse_errors = parse_errors + 1

# do() + reports + file I/O
system = system_snapshot()
priority = ticket_priority(8, 7)
sla = ticket_sla(priority)

report_add path, "feb", feb
report_add path, "greeting", greeting
report_add path, "average", average
report_add path, "letter", letter
report_add path, "parsed_total", parsed_total
report_add path, "parse_errors", parse_errors
report_add path, "priority", priority
report_add path, "sla", sla
report_add path, "system", system

final = report_finish(path)

assert "feb", feb, 29
assert "greeting", greeting, "Good morning"
assert "average", average, 85
assert "letter", letter, "B"
assert "parsed total", parsed_total, 30
assert "parse errors", parse_errors, 2
assert "priority", priority, "P2"
assert "sla", sla, "4 hours"
assert "system type", type(system), "text"
assert "file exists", exists(path), YES
assert "final has parsed", contains_line(final, "parsed_total"), YES

done "scenario 20 complete"
