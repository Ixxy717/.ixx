use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 22 generated sum 50")
assert "generated sum_to 50", sum_to(50), 1275

manual = 0
x = 50
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 50", manual, 1275
assert "module equals manual 50", sum_to(50), manual
say color("green", "hard 22 complete")
