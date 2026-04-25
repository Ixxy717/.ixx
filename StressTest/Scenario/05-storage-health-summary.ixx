use "Modules/asserts.ixx"
use "Modules/ops.ixx"
use "Modules/reports.ixx"

section "scenario 05 storage health summary"

path = "StressTest/tmp/scenario-05-storage-health.txt"
report_start "Storage Health", path

root_used = 62
data_used = 81
backup_used = 74
external_used = 91

root_state = short_health(root_used)
data_state = short_health(data_used)
backup_state = short_health(backup_used)
external_state = short_health(external_used)

watch_count = 0
critical_count = 0
if root_state is "watch"
- watch_count = watch_count + 1
if data_state is "watch"
- watch_count = watch_count + 1
if backup_state is "watch"
- watch_count = watch_count + 1
if external_state is "watch"
- watch_count = watch_count + 1
if external_state is "critical"
- critical_count = critical_count + 1

snapshot = system_snapshot()

report_add path, "root", root_state
report_add path, "data", data_state
report_add path, "backup", backup_state
report_add path, "external", external_state
report_add path, "watch_count", watch_count
report_add path, "critical_count", critical_count
report_add path, "snapshot", snapshot
final = report_finish(path)

assert "root ok", root_state, "ok"
assert "data watch", data_state, "watch"
assert "backup ok", backup_state, "ok"
assert "external critical", external_state, "critical"
assert "watch count", watch_count, 1
assert "critical count", critical_count, 1
assert "snapshot text", type(snapshot), "text"
assert "report saved", exists(path), YES

done "scenario 05 complete"
