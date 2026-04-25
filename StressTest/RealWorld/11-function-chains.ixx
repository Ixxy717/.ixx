# 10+ functions calling each other in non-trivial chains

function add a, b
- return a + b

function subtract a, b
- return a - b

function multiply a, b
- return a * b

function square x
- return multiply(x, x)

function cube x
- return multiply(square(x), x)

function power4 x
- return multiply(square(x), square(x))

function sum_of_squares a, b
- return add(square(a), square(b))

function distance_1d a, b
- diff = subtract(a, b)
- if diff less than 0
-- return multiply(diff, -1)
- return diff

function clamp val, lo, hi
- if val less than lo
-- return lo
- if val more than hi
-- return hi
- return val

function in_range val, lo, hi
- if val at least lo and val at most hi
-- return YES
- return NO

function normalize val, lo, hi
- span = subtract(hi, lo)
- if span is 0
-- return 0
- return subtract(val, lo) / span

say "square(7) = " + square(7)
say "cube(3) = " + cube(3)
say "power4(2) = " + power4(2)
say "sum_of_squares(3,4) = " + sum_of_squares(3, 4)
say "distance(10, 3) = " + distance_1d(10, 3)
say "distance(3, 10) = " + distance_1d(3, 10)
say "clamp(15, 0, 10) = " + clamp(15, 0, 10)
say "clamp(-5, 0, 10) = " + clamp(-5, 0, 10)
say "in_range(5, 0, 10) = " + text(in_range(5, 0, 10))
say "in_range(15, 0, 10) = " + text(in_range(15, 0, 10))
say "normalize(5, 0, 10) = " + normalize(5, 0, 10)
say "normalize(0, 0, 10) = " + normalize(0, 0, 10)
say "normalize(10, 0, 10) = " + normalize(10, 0, 10)
