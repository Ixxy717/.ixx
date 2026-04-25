use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 34 generated sum 350")
assert "generated sum_to 350", sum_to(350), 61425

manual = 0
x = 350
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 350", manual, 61425
assert "module equals manual 350", sum_to(350), manual
say color("green", "hard 34 complete")
