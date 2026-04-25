# Loop each over the result of a function that returns a list

function get_primes
- result = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
- return result

function get_squares
- result = 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
- return result

function get_fibonacci
- result = 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
- return result

primes = get_primes()
squares = get_squares()
fibs = get_fibonacci()

prime_sum = 0
loop each p in primes
- prime_sum = prime_sum + p
say "Prime sum: " + prime_sum

sq_sum = 0
loop each s in squares
- sq_sum = sq_sum + s
say "Squares sum: " + sq_sum

fib_sum = 0
loop each f in fibs
- fib_sum = fib_sum + f
say "Fibonacci sum: " + fib_sum

# Nested loop over two function results
cross_count = 0
loop each p in primes
- loop each s in squares
-- if s more than p
--- cross_count = cross_count + 1

say "Squares greater than each prime (cross count): " + cross_count

# Chain: loop over sorted result
sorted_primes = sort(get_primes())
say "Sorted primes first: " + first(sorted_primes)
say "Sorted primes last:  " + last(sorted_primes)
