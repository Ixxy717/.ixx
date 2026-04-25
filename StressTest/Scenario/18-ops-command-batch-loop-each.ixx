use "Modules/asserts.ixx"
use "Modules/reports.ixx"
use "Modules/ops.ixx"

section "scenario 18 ops command batch loop each"

path = "StressTest/tmp/scenario-18-ops-command-batch.txt"
report_start "Ops Command Batch", path

commands = "ram used", "cpu info", "disk space"
success = 0
combined = ""

loop each cmd in commands
- try
-- output = do(cmd)
-- asserttext "command output " + cmd, output
-- report_add path, cmd, output
-- combined = combined + output
-- success = success + 1
- catch
-- report_add path, cmd, "failed"

health = short_health(72)
snapshot = system_snapshot()
report_add path, "health", health
report_add path, "snapshot", snapshot
final = report_finish(path)

assert "success count", success, 3
assert "health ok", health, "ok"
assert "snapshot type", type(snapshot), "text"

long = NO
if count(combined) more than 20
- long = YES
assert "combined output long", long, YES
assert "report exists", exists(path), YES
assert "report has ram", contains_line(final, "ram used"), YES

done "scenario 18 complete"
