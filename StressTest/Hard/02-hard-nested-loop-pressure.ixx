use "Modules/asserts.ixx"

say color("cyan", "hard 02 nested loop pressure")
outer = 30
counted = 0
weighted = 0

loop outer more than 0
- inner = 30
- loop inner more than 0
-- counted = counted + 1
-- weighted = weighted + outer
-- inner = inner - 1
- outer = outer - 1

assert "30 by 30 count", counted, 900
assert "nested weighted sum", weighted, 13950
say color("green", "hard 02 complete")
