function pct part, whole
- if whole is 0
-- return 0
- return round((part / whole) * 100, 1)

function add_money a, b
- return round(a + b, 2)

function gross_margin revenue, cost
- profit = revenue - cost
- return pct(profit, revenue)

function grade_asset cpu, ram, storage, battery
- score = cpu + ram + storage + battery
- if score at least 360
-- return "A"
- if score at least 300
-- return "B"
- if score at least 220
-- return "C"
- return "D"

function disposition grade
- if grade is "A"
-- return "resale"
- if grade is "B"
-- return "resale"
- if grade is "C"
-- return "repair"
- return "scrap"

function risk_level score
- if score at least 80
-- return "high"
- if score at least 50
-- return "medium"
- return "low"

function normalize_name value
- clean = lower(trim(value))
- clean = replace(clean, " ", "-")
- clean = replace(clean, "_", "-")
- return clean

function make_line label, value
- return label + ": " + value
