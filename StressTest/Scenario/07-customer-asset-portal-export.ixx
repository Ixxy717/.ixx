use "Modules/asserts.ixx"
use "Modules/inventory.ixx"
use "Modules/reports.ixx"

section "scenario 07 customer asset portal export"

path = "StressTest/tmp/scenario-07-customer-export.txt"
report_start "Customer Asset Export", path

customer = "Acme Medical"
customer_slug = normalize_name(customer)

asset1 = asset_id("ACME-LAP", 1)
asset2 = asset_id("ACME-LAP", 2)
asset3 = asset_id("ACME-DESK", 3)

wipe1 = YES
wipe2 = YES
wipe3 = NO

grade1 = grade_asset(90, 80, 80, 75)
grade2 = grade_asset(75, 70, 70, 65)
grade3 = grade_asset(55, 45, 50, 40)

status1 = intake_status(grade1, wipe1)
status2 = intake_status(grade2, wipe2)
status3 = intake_status(grade3, wipe3)

report_add path, "customer", customer_slug
report_add path, asset1, status1
report_add path, asset2, status2
report_add path, asset3, status3
final = report_finish(path)

assert "customer slug", customer_slug, "acme-medical"
assert "asset1 status", status1, "resale"
assert "asset2 status", status2, "repair"
assert "asset3 status", status3, "hold-wipe"
assert "export has customer", contains_line(final, "acme-medical"), YES
assert "export has asset", contains_line(final, "ACME-LAP-1"), YES

done "scenario 07 complete"
