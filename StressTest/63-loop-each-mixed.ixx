say color("cyan", "63 loop each mixed")

use "Modules/helpers.ixx"

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

names = "Ixxy", "Lune", "Zach"
greetings_count = 0
loop each name in names
- msg = greet(name)
- greetings_count = greetings_count + 1

assert "greet count via import", greetings_count, 3
assert "last greeting", greet("IXX"), "Hello, IXX!"

nums = 2, 3, 4
doubled_sum = 0
loop each n in nums
- doubled_sum = doubled_sum + double(n)

assert "doubled sum via import", doubled_sum, 18

countdown = 3
total = 0
loop countdown more than 0
- total = total + countdown
- countdown = countdown - 1

assert "while loop after each loop", total, 6

mixed_data = 1, 2, 3
n = 0
loop each item in mixed_data
- n = n + item

loop n more than 0
- n = n - 1

assert "each loop then while loop ends at 0", n, 0

say color("green", "63 loop each mixed complete")
