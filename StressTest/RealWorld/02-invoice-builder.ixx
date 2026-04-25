# Invoice builder — totals line items and formats output

function cents_to_dollars cents
- d = cents / 100
- return "$" + round(d, 2)

item1_name = "Widget A"
item2_name = "Widget B"
item3_name = "Gadget C"
item4_name = "Service D"

item1_price = 2999
item2_price = 4999
item3_price = 1499
item4_price = 14900

subtotal = item1_price + item2_price + item3_price + item4_price
tax = round(subtotal * 8 / 100)
total = subtotal + tax

say "=== INVOICE ==="
say item1_name + ":  " + cents_to_dollars(item1_price)
say item2_name + ":  " + cents_to_dollars(item2_price)
say item3_name + ": " + cents_to_dollars(item3_price)
say item4_name + ": " + cents_to_dollars(item4_price)
say "---"
say "Subtotal: " + cents_to_dollars(subtotal)
say "Tax (8%): " + cents_to_dollars(tax)
say "TOTAL:    " + cents_to_dollars(total)
say "Items: " + 4
