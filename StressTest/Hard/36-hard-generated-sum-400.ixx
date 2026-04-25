use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 36 generated sum 400")
assert "generated sum_to 400", sum_to(400), 80200

manual = 0
x = 400
loop x more than 0
- manual = manual + x
- x = x - 1

assert "manual sum 400", manual, 80200
assert "module equals manual 400", sum_to(400), manual
say color("green", "hard 36 complete")
