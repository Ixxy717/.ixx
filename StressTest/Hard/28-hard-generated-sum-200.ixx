use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 28 generated sum 200")
assert "generated sum_to 200", sum_to(200), 20100

manual = 0
x = 200
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 200", manual, 20100
assert "module equals manual 200", sum_to(200), manual
say color("green", "hard 28 complete")
