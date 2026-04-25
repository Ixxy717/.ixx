use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 30 generated sum 250")
assert "generated sum_to 250", sum_to(250), 31375

manual = 0
x = 250
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 250", manual, 31375
assert "module equals manual 250", sum_to(250), manual
say color("green", "hard 30 complete")
