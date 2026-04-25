use "Modules/asserts.ixx"
use "Modules/ops.ixx"
use "Modules/reports.ixx"

section "scenario 06 network site report"

path = "StressTest/tmp/scenario-06-network-site.txt"
report_start "Network Site Report", path

network = network_snapshot()
ports = do("ports")
ip = do("ip local")
wifi = do("wifi ip")

report_add path, "network", network
report_add path, "ports", ports
report_add path, "ip", ip
report_add path, "wifi", wifi
final = report_finish(path)

asserttext "network snapshot", network
asserttext "ports", ports
asserttext "ip", ip
assert "report exists", exists(path), YES
assert "report has ip field", contains_line(final, "ip"), YES

done "scenario 06 complete"
