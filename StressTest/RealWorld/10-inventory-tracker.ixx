# Inventory tracker using loop each and running totals

function item_report name, qty, unit_price
- line_total = qty * unit_price
- say "  " + name + ": qty=" + qty + "  @$" + unit_price + "  = $" + line_total
- return line_total

say "=== INVENTORY REPORT ==="

laptop_total   = item_report("Laptop",    5,  899)
mouse_total    = item_report("Mouse",    15,   29)
keyboard_total = item_report("Keyboard", 12,   79)
monitor_total  = item_report("Monitor",   8,  399)
headset_total  = item_report("Headset",  20,  149)
cable_total    = item_report("USB Cable",50,    9)

grand_total = laptop_total + mouse_total + keyboard_total + monitor_total + headset_total + cable_total

say "---"
say "Grand Total: $" + grand_total

totals = laptop_total, mouse_total, keyboard_total, monitor_total, headset_total, cable_total
say "Line items: " + count(totals)
say "Highest line item: $" + max(totals)
say "Lowest line item:  $" + min(totals)

# Running total verification
check = 0
loop each t in totals
- check = check + t

if check is grand_total
- say "PASS: running total matches grand total"
