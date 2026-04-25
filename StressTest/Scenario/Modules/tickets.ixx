function ticket_priority impact, urgency
- score = impact + urgency
- if score at least 16
-- return "P1"
- if score at least 12
-- return "P2"
- if score at least 8
-- return "P3"
- return "P4"

function ticket_sla priority
- if priority is "P1"
-- return "1 hour"
- if priority is "P2"
-- return "4 hours"
- if priority is "P3"
-- return "1 day"
- return "3 days"

function ticket_line id, priority, owner
- return id + " | " + priority + " | " + owner
