use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 35 generated sum 375")
assert "generated sum_to 375", sum_to(375), 70500

manual = 0
x = 375
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 375", manual, 70500
assert "module equals manual 375", sum_to(375), manual
say color("green", "hard 35 complete")
