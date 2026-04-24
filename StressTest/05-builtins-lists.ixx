say color("cyan", "05 builtins lists")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

items = "banana", "apple", "grape", "ixx"
amount = count(items)
assert "count list", amount, 4

firstitem = first(items)
assert "first", firstitem, "banana"

lastitem = last(items)
assert "last", lastitem, "ixx"

sorteditems = sort(items)
sortedtext = join(sorteditems, " | ")
assert "sort text", sortedtext, "apple | banana | grape | ixx"

reverseditems = reverse(sorteditems)
reversedtext = join(reverseditems, " | ")
assert "reverse text", reversedtext, "ixx | grape | banana | apple"

joineddefault = join(sorteditems)
assert "join default", joineddefault, "apple, banana, grape, ixx"

hasixx = NO
if items contains "ixx"
- hasixx = YES
assert "contains list", hasixx, YES

listtype = type(items)
assert "type list", listtype, "list"

nums = 42, 7, 13, 1
sortednums = sort(nums)
sortednumstext = join(sortednums, ", ")
assert "sort numbers", sortednumstext, "1, 7, 13, 42"

say color("green", "05 builtins lists complete")
