use "Modules/asserts.ixx"
use "Modules/reports.ixx"

section "scenario 12 backup manifest builder"

manifest = "StressTest/tmp/scenario-12-manifest.txt"
report_start "Backup Manifest", manifest

src1 = "inventory.db"
src2 = "labels/"
src3 = "reports/"
src4 = "uploads/"

size1 = 240
size2 = 85
size3 = 128
size4 = 512

total = size1 + size2 + size3 + size4
status = "ok"
if total more than 1000
- status = "large"

report_add manifest, src1, size1
report_add manifest, src2, size2
report_add manifest, src3, size3
report_add manifest, src4, size4
report_add manifest, "total_mb", total
report_add manifest, "status", status
final = report_finish(manifest)

assert "total mb", total, 965
assert "status", status, "ok"
assert "manifest exists", exists(manifest), YES
assert "manifest has uploads", contains_line(final, "uploads/"), YES

done "scenario 12 complete"
