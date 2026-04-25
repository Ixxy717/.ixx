say color("cyan", "59 loop each basic")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

nums = 1, 2, 3, 4, 5
total = 0
loop each n in nums
- total = total + n

assert "sum 1..5", total, 15

words = "hello", "world", "ixx"
result = ""
loop each w in words
- result = result + w + " "

trimmed = trim(result)
assert "word concat", trimmed, "hello world ixx"

items = YES, NO, YES
trues = 0
loop each flag in items
- if flag
-- trues = trues + 1

assert "count trues", trues, 2

pair = 10, 20
pair_sum = 0
loop each v in pair
- pair_sum = pair_sum + v

assert "two-item list sum", pair_sum, 30

nested = 5, 10, 15
subtracted = 0
loop each x in nested
- subtracted = subtracted + x

assert "nested values sum", subtracted, 30

say color("green", "59 loop each basic complete")
