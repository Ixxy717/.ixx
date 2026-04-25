use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 27 generated sum 175")
assert "generated sum_to 175", sum_to(175), 15400

manual = 0
x = 175
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 175", manual, 15400
assert "module equals manual 175", sum_to(175), manual
say color("green", "hard 27 complete")
