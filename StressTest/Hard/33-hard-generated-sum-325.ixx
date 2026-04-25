use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 33 generated sum 325")
assert "generated sum_to 325", sum_to(325), 52975

manual = 0
x = 325
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 325", manual, 52975
assert "module equals manual 325", sum_to(325), manual
say color("green", "hard 33 complete")
