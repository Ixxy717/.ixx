use "Modules/asserts.ixx"
use "Modules/Mega/numbers.ixx"

say color("cyan", "hard 17 mega numbers")
assert "sum to 100", sum_to(100), 5050
assert "triangular 50", triangular(50), 1275
assert "between low", between(-5, 0, 10), 0
assert "between high", between(999, 0, 10), 10
assert "between middle", between(7, 0, 10), 7
say color("green", "hard 17 complete")
