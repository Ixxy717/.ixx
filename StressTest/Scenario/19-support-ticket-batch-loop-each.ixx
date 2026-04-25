use "Modules/asserts.ixx"
use "Modules/reports.ixx"
use "Modules/tickets.ixx"

section "scenario 19 support ticket batch loop each"

path = "StressTest/tmp/scenario-19-support-ticket-batch.txt"
report_start "Support Ticket Batch", path

impacts = 9, 7, 5, 2
urgencies = 8, 6, 4, 2
ids = "TCK-201", "TCK-202", "TCK-203", "TCK-204"

# IXX does not have indexing yet, so this scenario checks list iteration behavior
# with separate priority groups and report generation.
p1 = ticket_priority(9, 8)
p2 = ticket_priority(7, 6)
p3 = ticket_priority(5, 4)
p4 = ticket_priority(2, 2)

priorities = p1, p2, p3, p4
p1_count = 0
p2_count = 0
p3_count = 0
p4_count = 0

loop each p in priorities
- if p is "P1"
-- p1_count = p1_count + 1
- if p is "P2"
-- p2_count = p2_count + 1
- if p is "P3"
-- p3_count = p3_count + 1
- if p is "P4"
-- p4_count = p4_count + 1
- report_add path, "priority", p + " / " + ticket_sla(p)

final = report_finish(path)

assert "p1 count", p1_count, 1
assert "p2 count", p2_count, 1
assert "p3 count", p3_count, 1
assert "p4 count", p4_count, 1
assert "p1 sla", ticket_sla(p1), "1 hour"
assert "p4 sla", ticket_sla(p4), "3 days"
assert "report has priority", contains_line(final, "priority"), YES

done "scenario 19 complete"
