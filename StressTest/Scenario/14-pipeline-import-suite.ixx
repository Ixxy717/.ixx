use "Modules/asserts.ixx"
use "Modules/inventory.ixx"
use "Modules/reports.ixx"
use "Modules/ops.ixx"

section "scenario 14 pipeline import suite"

path = "StressTest/tmp/scenario-14-pipeline-suite.txt"
report_start "Pipeline Suite", path

grade = grade_asset(85, 85, 80, 80)
status = intake_status(grade, YES)
loc = location_code("R", "02", "BENCH")
sys = system_snapshot()

report_add path, "grade", grade
report_add path, "status", status
report_add path, "location", loc
report_add path, "system", sys
report_add path, "margin", gross_margin(500, 275)
final = report_finish(path)

assert "grade", grade, "B"
assert "status", status, "resale"
assert "loc", loc, "R-02-BENCH"
assert "sys text", type(sys), "text"
assert "margin", gross_margin(500, 275), 45
assert "report has location", contains_line(final, "R-02-BENCH"), YES

done "scenario 14 complete"
