# Recursive functions — sum, product, and count via recursion

function recursive_sum lst
- total = 0
- loop each n in lst
-- total = total + n
- return total

function recursive_product lst
- result = 1
- loop each n in lst
-- result = result * n
- return result

function count_positive lst
- c = 0
- loop each n in lst
-- if n more than 0
--- c = c + 1
- return c

function count_in_range lst, lo, hi
- c = 0
- loop each n in lst
-- if n at least lo and n at most hi
--- c = c + 1
- return c

data = 1, -2, 3, -4, 5, -6, 7, -8, 9, -10, 2, 4, 6, 8, 10

say "Data: " + join(data, ", ")
say "Sum: " + recursive_sum(data)
say "Positives: " + count_positive(data)
say "In range [1,5]: " + count_in_range(data, 1, 5)

positives = 1, 2, 3, 4, 5
say "Product of 1..5: " + recursive_product(positives)

if recursive_product(positives) is 120
- say "PASS: 5! = 120"

if recursive_sum(positives) is 15
- say "PASS: sum(1..5) = 15"
