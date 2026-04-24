say color("cyan", "14 nested blocks")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

score = 0
outer = 3

loop outer more than 0
- if outer at least 2
-- score = score + 10
-- inner = 2
-- loop inner more than 0
--- score = score + inner
--- inner = inner - 1
- else
-- score = score + 1
- outer = outer - 1

assert "nested loop if score", score, 27

label = "unset"
if score at least 20
- if score at most 30
-- label = "middle"
- else
-- label = "too high"
else
- label = "too low"

assert "nested if else", label, "middle"

say color("green", "14 nested blocks complete")
