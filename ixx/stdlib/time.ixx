# IXX standard library: time utilities
# Pure IXX functions — no built-ins required.

function time_greeting hour
- if hour less than 12
-- return "Good morning"
- if hour less than 18
-- return "Good afternoon"
- return "Good evening"

function minutes_to_hours mins
- hours = round(mins / 60, 1)
- return hours

function seconds_to_minutes secs
- mins = round(secs / 60, 1)
- return mins
