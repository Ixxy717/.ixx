function hard_square x
- return x * x

function hard_cube x
- return x * x * x

function hard_add3 a, b, c
- return a + b + c

function hard_weighted a, b
- return (a * 3) + (b * 2)

function hard_factorial n
- if n at most 1
-- return 1
- return n * hard_factorial(n - 1)
