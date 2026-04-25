use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 23 generated sum 75")
assert "generated sum_to 75", sum_to(75), 2850

manual = 0
x = 75
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 75", manual, 2850
assert "module equals manual 75", sum_to(75), manual
say color("green", "hard 23 complete")
