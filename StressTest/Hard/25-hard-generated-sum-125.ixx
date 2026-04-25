use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 25 generated sum 125")
assert "generated sum_to 125", sum_to(125), 7875

manual = 0
x = 125
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 125", manual, 7875
assert "module equals manual 125", sum_to(125), manual
say color("green", "hard 25 complete")
