use "Modules/asserts.ixx"
use "Modules/business.ixx"
use "Modules/reports.ixx"

section "scenario 04 ebay sales day"

path = "StressTest/tmp/scenario-04-ebay-sales.txt"
report_start "eBay Sales Day", path

sale1 = 129.99
sale2 = 89.50
sale3 = 249.00
sale4 = 34.25
sale5 = 420.00

ship1 = 12.10
ship2 = 9.25
ship3 = 18.50
ship4 = 6.00
ship5 = 22.00

revenue = sale1 + sale2 + sale3 + sale4 + sale5
shipping = ship1 + ship2 + ship3 + ship4 + ship5
fees = round(revenue * 0.13, 2)
cost = 355.00
profit = round(revenue - shipping - fees - cost, 2)
margin = gross_margin(revenue, shipping + fees + cost)

report_add path, "revenue", revenue
report_add path, "shipping", shipping
report_add path, "fees", fees
report_add path, "cost", cost
report_add path, "profit", profit
report_add path, "margin", margin

status = "good"
if profit less than 100
- status = "low"
if margin more than 40
- status = "excellent"

report_add path, "status", status
final = report_finish(path)

assert "revenue", revenue, 922.74
assert "shipping", shipping, 67.85
assert "fees", fees, 119.96
assert "profit", profit, 379.93
assert "status", status, "excellent"
assert "report has profit", contains_line(final, "profit"), YES

done "scenario 04 complete"
