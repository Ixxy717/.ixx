use "Modules/asserts.ixx"
use "Modules/reports.ixx"

section "scenario 11 log file analyzer"

logpath = "StressTest/tmp/scenario-11-app.log"
report = "StressTest/tmp/scenario-11-log-report.txt"

write logpath, "INFO boot|WARN disk high|INFO user login|ERROR failed job|WARN retrying|INFO done"

content = read(logpath)
events = split(content, "|")

info_count = 0
warn_count = 0
error_count = 0

if content contains "INFO boot"
- info_count = info_count + 1
if content contains "INFO user login"
- info_count = info_count + 1
if content contains "INFO done"
- info_count = info_count + 1
if content contains "WARN disk high"
- warn_count = warn_count + 1
if content contains "WARN retrying"
- warn_count = warn_count + 1
if content contains "ERROR failed job"
- error_count = error_count + 1

report_start "Log Analysis", report
report_add report, "events", count(events)
report_add report, "info", info_count
report_add report, "warn", warn_count
report_add report, "error", error_count
final = report_finish(report)

assert "event count", count(events), 6
assert "first event", first(events), "INFO boot"
assert "last event", last(events), "INFO done"
assert "info count", info_count, 3
assert "warn count", warn_count, 2
assert "error count", error_count, 1
assert "report contains warn", contains_line(final, "warn"), YES

done "scenario 11 complete"
