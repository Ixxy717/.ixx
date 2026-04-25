use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 32 generated sum 300")
assert "generated sum_to 300", sum_to(300), 45150

manual = 0
x = 300
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 300", manual, 45150
assert "module equals manual 300", sum_to(300), manual
say color("green", "hard 32 complete")
