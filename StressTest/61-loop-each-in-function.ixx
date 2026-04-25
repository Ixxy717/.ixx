say color("cyan", "61 loop each in function")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

function sum_list lst
- total = 0
- loop each n in lst
-- total = total + n
- return total

function first_positive lst
- loop each n in lst
-- if n more than 0
--- return n
- return nothing

function join_words lst, sep
- result = ""
- first_flag = YES
- loop each w in lst
-- if first_flag
--- result = w
--- first_flag = NO
-- else
--- result = result + sep + w
- return result

nums = 1, 2, 3, 4, 5
assert "sum_list", sum_list(nums), 15

mixed = -3, -1, 0, 4, 7
assert "first_positive", first_positive(mixed), 4

greetings = "Hello", "World", "IXX"
assert "join_words", join_words(greetings, ", "), "Hello, World, IXX"

two_items = 7, 13
assert "sum two items", sum_list(two_items), 20

say color("green", "61 loop each in function complete")
