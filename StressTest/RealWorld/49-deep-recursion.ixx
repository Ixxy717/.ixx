# Recursion countdown — 99 deep, then verify sum

function deep_count n
- if n is 0
-- return "done"
- return deep_count(n - 1)

say deep_count(99)
say deep_count(50)
say deep_count(1)

function accumulate n
- if n is 0
-- return 0
- return n + accumulate(n - 1)

sum99 = accumulate(99)
say "accumulate(99) = " + sum99

expected = 99 * 100 / 2
if sum99 is expected
- say "PASS: sum 1..99 = " + expected

sum50 = accumulate(50)
say "accumulate(50) = " + sum50
if sum50 is 1275
- say "PASS: sum 1..50 = 1275"
