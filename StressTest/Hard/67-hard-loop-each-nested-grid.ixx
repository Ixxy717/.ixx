use "Modules/asserts.ixx"

say color("cyan", "hard 67 loop each nested grid")
xs = 1, 2, 3, 4, 5
ys = 10, 20, 30, 40
total = 0
cells = 0

loop each x in xs
- loop each y in ys
-- total = total + x * y
-- cells = cells + 1

assert "grid cells", cells, 20
assert "grid total", total, 1500

diagonalish = 0
loop each x in xs
- loop each y in ys
-- if x is 3
--- diagonalish = diagonalish + y

assert "conditional nested row", diagonalish, 100
say color("green", "hard 67 complete")
