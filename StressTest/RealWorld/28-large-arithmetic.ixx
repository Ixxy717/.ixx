# Large integer arithmetic: factorials and powers via recursive multiplication

function factorial n
- if n at most 1
-- return 1
- return n * factorial(n - 1)

function power base, exp
- if exp is 0
-- return 1
- if exp is 1
-- return base
- return base * power(base, exp - 1)

say "Factorials:"
say "5!  = " + factorial(5)
say "10! = " + factorial(10)
say "15! = " + factorial(15)
say "20! = " + factorial(20)

say "Powers:"
say "2^10  = " + power(2, 10)
say "2^20  = " + power(2, 20)
say "2^30  = " + power(2, 30)
say "3^10  = " + power(3, 10)
say "10^10 = " + power(10, 10)

if factorial(5) is 120
- say "PASS: 5! = 120"
if factorial(10) is 3628800
- say "PASS: 10! = 3628800"
if power(2, 10) is 1024
- say "PASS: 2^10 = 1024"
if power(10, 10) is 10000000000
- say "PASS: 10^10 = 10000000000"

# Large value arithmetic
big = power(2, 40)
say "2^40 = " + big
say "Digits in 2^40: " + count(text(big))
