use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 40 generated sum 500")
assert "generated sum_to 500", sum_to(500), 125250

manual = 0
x = 500
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 500", manual, 125250
assert "module equals manual 500", sum_to(500), manual
say color("green", "hard 40 complete")
