use "Modules/asserts.ixx"
use "Modules/loop-each-hard-utils.ixx"

say color("cyan", "hard 66 loop each weighted")
values = 3, 5, 7, 11, 13, 17

# Weighted formula:
# 3*1 + 5*2 + 7*3 + 11*4 + 13*5 + 17*6 = 245
assert "weighted total", weighted_total(values), 245

manual = 0
weight = 1
loop each value in values
- manual = manual + value * weight
- weight = weight + 1

assert "manual weighted total", manual, 245
assert "weight survived", weight, 7

# Extra sanity check so this test is still actually meaningful.
plain_total = 0
loop each value in values
- plain_total = plain_total + value

assert "plain total", plain_total, 56
say color("green", "hard 66 complete")
