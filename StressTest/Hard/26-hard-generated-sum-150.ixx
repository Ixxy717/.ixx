use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 26 generated sum 150")
assert "generated sum_to 150", sum_to(150), 11325

manual = 0
x = 150
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 150", manual, 11325
assert "module equals manual 150", sum_to(150), manual
say color("green", "hard 26 complete")
