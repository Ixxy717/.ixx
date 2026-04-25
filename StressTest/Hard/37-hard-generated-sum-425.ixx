use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 37 generated sum 425")
assert "generated sum_to 425", sum_to(425), 90525

manual = 0
x = 425
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 425", manual, 90525
assert "module equals manual 425", sum_to(425), manual
say color("green", "hard 37 complete")
