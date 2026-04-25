use "Modules/asserts.ixx"

say color("cyan", "hard 01 loop pressure")
n = 1000
sum = 0
loop n more than 0
- sum = sum + n
- n = n - 1

assert "sum 1..1000", sum, 500500
assert "loop ended at zero", n, 0

m = 250
productish = 0
loop m more than 0
- productish = productish + 3
- m = m - 1

assert "repeated add", productish, 750
say color("green", "hard 01 complete")
