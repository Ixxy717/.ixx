use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 21 generated sum 25")
assert "generated sum_to 25", sum_to(25), 325

manual = 0
x = 25
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 25", manual, 325
assert "module equals manual 25", sum_to(25), manual
say color("green", "hard 21 complete")
