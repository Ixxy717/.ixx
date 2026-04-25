# Fibonacci sequence generator up to N terms

function fib_sequence n
- a = 0
- b = 1
- i = 0
- loop i less than n
-- say a
-- temp = a + b
-- a = b
-- b = temp
-- i = i + 1

say "First 10 Fibonacci numbers:"
fib_sequence(10)
say "---"
say "15th term onwards (terms 10-14):"
fib_sequence(15)
say "---"

# Verify known values using iterative approach
a = 0
b = 1
i = 0
loop i less than 10
- temp = a + b
- a = b
- b = temp
- i = i + 1

say "10th fibonacci (0-indexed): " + a
if a is 55
- say "PASS: fib(10) = 55"
