use "Modules/asserts.ixx"
use "Modules/inventory.ixx"
use "Modules/reports.ixx"

section "scenario 02 inventory location audit"

path = "StressTest/tmp/scenario-02-location-audit.txt"
report_start "Location Audit", path

loc_a = location_code("A", "01", "TOP")
loc_b = location_code("A", "01", "MID")
loc_c = location_code("B", "04", "LOW")
loc_d = location_code("SCRAP", "GL", "07")

expected_a = 12
actual_a = 12
expected_b = 8
actual_b = 7
expected_c = 15
actual_c = 17
expected_d = 1
actual_d = 1

missing = 0
extra = 0
if actual_b less than expected_b
- missing = missing + (expected_b - actual_b)
if actual_c more than expected_c
- extra = extra + (actual_c - expected_c)

accuracy_a = pct(actual_a, expected_a)
accuracy_b = pct(actual_b, expected_b)
accuracy_d = pct(actual_d, expected_d)

report_add path, loc_a, actual_a
report_add path, loc_b, actual_b
report_add path, loc_c, actual_c
report_add path, loc_d, actual_d
report_add path, "missing", missing
report_add path, "extra", extra
report_add path, "accuracy_a", accuracy_a
report_add path, "accuracy_b", accuracy_b
report_add path, "accuracy_d", accuracy_d
final = report_finish(path)

assert "location A", loc_a, "A-01-TOP"
assert "missing count", missing, 1
assert "extra count", extra, 2
assert "accuracy exact", accuracy_a, 100
assert "accuracy one off", accuracy_b, 87.5
assert "report has location", contains_line(final, "SCRAP-GL-07"), YES

done "scenario 02 complete"
