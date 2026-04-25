use "Modules/asserts.ixx"
use "Modules/inventory.ixx"
use "Modules/ops.ixx"
use "Modules/reports.ixx"
use "Modules/tickets.ixx"
use std "date"
use std "time"

section "scenario 15 full company snapshot"

path = "StressTest/tmp/scenario-15-company-snapshot.txt"
report_start "Full Company Snapshot", path

assets_total = 48
assets_resale = 31
assets_repair = 9
assets_scrap = 8
resale_rate = pct(assets_resale, assets_total)

gl_value = gaylord_value(1200, 0.18)
ticket_priority_main = ticket_priority(8, 7)
ticket_sla_main = ticket_sla(ticket_priority_main)
system = system_snapshot()
greeting = time_greeting(10)
feb = days_in_february(2024)

status = "normal"
if resale_rate less than 50
- status = "inventory review"
if ticket_priority_main is "P1"
- status = "urgent ops"

report_add path, "assets_total", assets_total
report_add path, "assets_resale", assets_resale
report_add path, "resale_rate", resale_rate
report_add path, "gaylord_value", gl_value
report_add path, "ticket_priority", ticket_priority_main
report_add path, "ticket_sla", ticket_sla_main
report_add path, "greeting", greeting
report_add path, "february_days", feb
report_add path, "system", system
report_add path, "status", status
final = report_finish(path)

assert "resale rate", resale_rate, 64.6
assert "gaylord value", gl_value, 216
assert "ticket priority", ticket_priority_main, "P2"
assert "ticket sla", ticket_sla_main, "4 hours"
assert "greeting", greeting, "Good morning"
assert "feb days", feb, 29
assert "status", status, "normal"
assert "system text", type(system), "text"
assert "snapshot exists", exists(path), YES
assert "snapshot has status", contains_line(final, "status"), YES

done "scenario 15 complete"
