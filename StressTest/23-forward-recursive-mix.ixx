say color("cyan", "23 forward recursive mix")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

result = startcalc(5)
assert "forward recursive mix", result, 15

function startcalc n
- return sumdown(n)

function sumdown n
- if n at most 0
-- return 0
- rest = sumdown(n - 1)
- return n + rest

result2 = wrapper(4)
assert "forward wrapper", result2, 24

function wrapper n
- return factoriallater(n)

function factoriallater n
- if n at most 1
-- return 1
- previous = factoriallater(n - 1)
- return n * previous

say color("green", "23 forward recursive mix complete")
