function sum_to n
- total = 0
- loop n more than 0
-- total = total + n
-- n = n - 1
- return total

function triangular n
- return sum_to(n)

function clamp_low value, low
- if value less than low
-- return low
- return value

function clamp_high value, high
- if value more than high
-- return high
- return value

function between value, low, high
- v = clamp_low(value, low)
- return clamp_high(v, high)
