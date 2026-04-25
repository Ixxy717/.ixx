use "Modules/asserts.ixx"
use "Modules/reports.ixx"
use "Modules/tickets.ixx"
use std "date"
use std "time"

section "scenario 16 release readiness loop each"

path = "StressTest/tmp/scenario-16-release-readiness.txt"
report_start "Release Readiness", path

checks = "unit tests", "normal stress", "hard stress", "scenario stress", "docs", "package"
statuses = "pass", "pass", "pass", "pass", "review", "pass"

pass_count = 0
review_count = 0
index = 1

loop each status in statuses
- if status is "pass"
-- pass_count = pass_count + 1
- if status is "review"
-- review_count = review_count + 1
- report_add path, "check " + index, status
- index = index + 1

priority = ticket_priority(6, 5)
sla = ticket_sla(priority)
greeting = time_greeting(14)
feb = days_in_february(2024)

report_add path, "priority", priority
report_add path, "sla", sla
report_add path, "greeting", greeting
report_add path, "feb", feb
final = report_finish(path)

assert "pass count", pass_count, 5
assert "review count", review_count, 1
assert "priority", priority, "P3"
assert "sla", sla, "1 day"
assert "greeting", greeting, "Good afternoon"
assert "feb days", feb, 29
assert "report has check", contains_line(final, "check 5"), YES

done "scenario 16 complete"
