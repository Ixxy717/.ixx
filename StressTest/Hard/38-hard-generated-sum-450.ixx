use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 38 generated sum 450")
assert "generated sum_to 450", sum_to(450), 101475

manual = 0
x = 450
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 450", manual, 101475
assert "module equals manual 450", sum_to(450), manual
say color("green", "hard 38 complete")
