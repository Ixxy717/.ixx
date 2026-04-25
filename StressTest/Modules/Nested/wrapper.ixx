use "math-core.ixx"

function nested_quad x
- return nested_double(nested_double(x))

function nested_sum_then_double a, b
- total = nested_plus(a, b)
- return nested_double(total)
