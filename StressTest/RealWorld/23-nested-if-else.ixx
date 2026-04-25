# Deeply nested if/else — 8+ levels of nesting

function classify x
- if x more than 1000
-- if x more than 10000
--- if x more than 100000
---- if x more than 1000000
----- return "astronomical"
---- return "huge"
--- return "very large"
-- return "large"
- if x more than 100
-- if x more than 500
--- return "medium-high"
-- return "medium"
- if x more than 10
-- if x more than 50
--- return "small-high"
-- return "small"
- if x more than 0
-- return "tiny"
- if x is 0
-- return "zero"
- if x more than -100
-- return "small negative"
- return "large negative"

values = 0, 5, 15, 55, 150, 600, 5000, 50000, 500000, 5000000, -1, -200

loop each v in values
- say text(v) + " -> " + classify(v)

if classify(5000000) is "astronomical"
- say "PASS: deep nest correctly reached leaf"

if classify(0) is "zero"
- say "PASS: zero case"
