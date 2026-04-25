# Running sum, product, and max using loop each

primes = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29

running_sum = 0
running_product = 1
running_max = 0
above_10 = 0

loop each n in primes
- running_sum = running_sum + n
- running_product = running_product * n
- if n more than running_max
-- running_max = n
- if n more than 10
-- above_10 = above_10 + 1

say "Sum of first 10 primes:     " + running_sum
say "Product of first 10 primes: " + running_product
say "Max prime in set:           " + running_max
say "Primes above 10:            " + above_10

if running_sum is 129
- say "PASS: sum = 129"
if running_max is 29
- say "PASS: max = 29"

say "---"
say "Cumulative sums:"
cumulative = 0
loop each n in primes
- cumulative = cumulative + n
- say "  +" + n + " -> " + cumulative
