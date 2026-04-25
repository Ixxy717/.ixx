use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 24 generated sum 100")
assert "generated sum_to 100", sum_to(100), 5050

manual = 0
x = 100
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 100", manual, 5050
assert "module equals manual 100", sum_to(100), manual
say color("green", "hard 24 complete")
