# Function calls itself 99 times (one under the 100-call depth limit)

function count_down n
- if n is 0
-- return "reached-zero"
- return count_down(n - 1)

result = count_down(99)
say "count_down(99): " + result

if result is "reached-zero"
- say "PASS: 99-deep recursion completed"

# Also verify 50-deep
result2 = count_down(50)
say "count_down(50): " + result2

# A function that accumulates over 99 recursive calls
function sum_down n
- if n is 0
-- return 0
- return n + sum_down(n - 1)

total = sum_down(99)
say "sum_down(99) = " + total

expected = 99 * 100 / 2
if total is expected
- say "PASS: sum_down(99) = " + expected
