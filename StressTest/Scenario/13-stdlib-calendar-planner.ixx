use "Modules/asserts.ixx"
use std "date"
use std "time"
use "Modules/reports.ixx"

section "scenario 13 stdlib calendar planner"

path = "StressTest/tmp/scenario-13-calendar-planner.txt"
report_start "Calendar Planner", path

feb_2024 = days_in_february(2024)
feb_2025 = days_in_february(2025)

morning = time_greeting(8)
afternoon = time_greeting(15)
evening = time_greeting(21)

valid = is_valid_month(12)
invalid = is_valid_month(99)

report_add path, "feb_2024", feb_2024
report_add path, "feb_2025", feb_2025
report_add path, "morning", morning
report_add path, "afternoon", afternoon
report_add path, "evening", evening
report_add path, "valid", valid
report_add path, "invalid", invalid
final = report_finish(path)

assert "feb leap", feb_2024, 29
assert "feb normal", feb_2025, 28
assert "morning", morning, "Good morning"
assert "afternoon", afternoon, "Good afternoon"
assert "evening", evening, "Good evening"
assert "valid month", valid, YES
assert "invalid month", invalid, NO
assert "report has feb", contains_line(final, "feb_2024"), YES

done "scenario 13 complete"
