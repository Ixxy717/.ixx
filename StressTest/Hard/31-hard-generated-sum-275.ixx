use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 31 generated sum 275")
assert "generated sum_to 275", sum_to(275), 37950

manual = 0
x = 275
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 275", manual, 37950
assert "module equals manual 275", sum_to(275), manual
say color("green", "hard 31 complete")
