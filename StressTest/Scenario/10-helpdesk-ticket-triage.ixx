use "Modules/asserts.ixx"
use "Modules/tickets.ixx"
use "Modules/reports.ixx"

section "scenario 10 helpdesk ticket triage"

path = "StressTest/tmp/scenario-10-ticket-triage.txt"
report_start "Ticket Triage", path

p1 = ticket_priority(9, 8)
p2 = ticket_priority(7, 6)
p3 = ticket_priority(5, 4)
p4 = ticket_priority(2, 2)

sla1 = ticket_sla(p1)
sla2 = ticket_sla(p2)
sla3 = ticket_sla(p3)
sla4 = ticket_sla(p4)

line1 = ticket_line("TCK-100", p1, "Ixxy")
line2 = ticket_line("TCK-101", p2, "Ops")
line3 = ticket_line("TCK-102", p3, "Refurb")
line4 = ticket_line("TCK-103", p4, "Later")

report_add path, "ticket1", line1 + " / " + sla1
report_add path, "ticket2", line2 + " / " + sla2
report_add path, "ticket3", line3 + " / " + sla3
report_add path, "ticket4", line4 + " / " + sla4
final = report_finish(path)

assert "priority p1", p1, "P1"
assert "priority p2", p2, "P2"
assert "priority p3", p3, "P3"
assert "priority p4", p4, "P4"
assert "sla p1", sla1, "1 hour"
assert "sla p4", sla4, "3 days"
assert "report contains ticket", contains_line(final, "TCK-100"), YES

done "scenario 10 complete"
