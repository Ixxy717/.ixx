use "Modules/asserts.ixx"

say color("cyan", "hard 03 recursion and forward")

assert "forward call before definition", call_later(20), 42
assert "factorial 8", fact(8), 40320
assert "fib 10", fib(10), 55

function call_later x
- return add_twenty_two(x)

function add_twenty_two x
- return x + 22

function fact n
- if n at most 1
-- return 1
- return n * fact(n - 1)

function fib n
- if n at most 1
-- return n
- return fib(n - 1) + fib(n - 2)

say color("green", "hard 03 complete")
