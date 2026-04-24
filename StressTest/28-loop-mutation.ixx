say color("cyan", "28 loop mutation")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

n = 5
product = 1
loop n more than 0
- product = product * n
- n = n - 1

assert "loop factorial", product, 120

text = ""
i = 3
loop i more than 0
- text = text + "x"
- i = i - 1

assert "loop string build", text, "xxx"

sum = 0
outer = 3
loop outer more than 0
- inner = outer
- loop inner more than 0
-- sum = sum + 1
-- inner = inner - 1
- outer = outer - 1

assert "nested loop count", sum, 6

say color("green", "28 loop mutation complete")
