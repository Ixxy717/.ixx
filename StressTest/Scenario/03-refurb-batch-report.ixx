use "Modules/asserts.ixx"
use "Modules/business.ixx"
use "Modules/reports.ixx"

section "scenario 03 refurb batch report"

path = "StressTest/tmp/scenario-03-refurb-batch.txt"
report_start "Refurb Batch", path

batch = "RB-2026-04-25"
total = 30
passed = 22
needs_driver = 4
failed = 3
missing_drive = 1

pass_rate = pct(passed, total)
fail_rate = pct(failed, total)

ready_for_listing = passed
needs_attention = needs_driver + failed + missing_drive

report_add path, "batch", batch
report_add path, "total", total
report_add path, "passed", passed
report_add path, "needs_driver", needs_driver
report_add path, "failed", failed
report_add path, "missing_drive", missing_drive
report_add path, "pass_rate", pass_rate
report_add path, "fail_rate", fail_rate
report_add path, "needs_attention", needs_attention

status = "ok"
if pass_rate less than 70
- status = "review"
if needs_attention more than 10
- status = "review"

report_add path, "status", status
final = report_finish(path)

assert "pass rate", pass_rate, 73.3
assert "fail rate", fail_rate, 10
assert "needs attention", needs_attention, 8
assert "status ok", status, "ok"
assert "report has batch", contains_line(final, batch), YES

done "scenario 03 complete"
