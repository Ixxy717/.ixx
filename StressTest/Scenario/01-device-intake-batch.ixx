use "Modules/asserts.ixx"
use "Modules/inventory.ixx"
use "Modules/reports.ixx"

section "scenario 01 device intake batch"

path = "StressTest/tmp/scenario-01-device-intake.txt"
report_start "Device Intake Batch", path

id1 = asset_id("LAP", 1001)
id2 = asset_id("LAP", 1002)
id3 = asset_id("DESK", 2001)
id4 = asset_id("TAB", 3001)

grade1 = grade_asset(95, 95, 90, 90)
grade2 = grade_asset(80, 80, 75, 70)
grade3 = grade_asset(70, 45, 60, 55)
grade4 = grade_asset(40, 30, 30, 20)

status1 = intake_status(grade1, YES)
status2 = intake_status(grade2, YES)
status3 = intake_status(grade3, NO)
status4 = intake_status(grade4, YES)

report_add path, id1, grade1 + " / " + status1
report_add path, id2, grade2 + " / " + status2
report_add path, id3, grade3 + " / " + status3
report_add path, id4, grade4 + " / " + status4

resale_count = 0
repair_count = 0
scrap_count = 0
hold_count = 0

if status1 is "resale"
- resale_count = resale_count + 1
if status2 is "resale"
- resale_count = resale_count + 1
if status3 is "repair"
- repair_count = repair_count + 1
if status3 is "hold-wipe"
- hold_count = hold_count + 1
if status4 is "scrap"
- scrap_count = scrap_count + 1

report_add path, "resale_count", resale_count
report_add path, "repair_count", repair_count
report_add path, "scrap_count", scrap_count
report_add path, "hold_count", hold_count
final = report_finish(path)

assert "id1 grade", grade1, "A"
assert "id2 grade", grade2, "B"
assert "id3 held for wipe", status3, "hold-wipe"
assert "id4 scrap", status4, "scrap"
assert "resale count", resale_count, 2
assert "hold count", hold_count, 1
assert "report exists", exists(path), YES
assert "report has id", contains_line(final, "LAP-1001"), YES

done "scenario 01 complete"
