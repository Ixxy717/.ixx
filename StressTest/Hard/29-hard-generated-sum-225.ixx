use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 29 generated sum 225")
assert "generated sum_to 225", sum_to(225), 25425

manual = 0
x = 225
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 225", manual, 25425
assert "module equals manual 225", sum_to(225), manual
say color("green", "hard 29 complete")
