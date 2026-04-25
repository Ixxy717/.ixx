use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 39 generated sum 475")
assert "generated sum_to 475", sum_to(475), 113050

manual = 0
x = 475
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 475", manual, 113050
assert "module equals manual 475", sum_to(475), manual
say color("green", "hard 39 complete")
