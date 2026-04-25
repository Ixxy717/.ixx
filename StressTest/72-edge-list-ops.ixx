function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

nums = 3, 1, 4, 1, 5, 9, 2, 6
assert "sort ascending first", first(sort(nums)), 1
assert "sort ascending last", last(sort(nums)), 9

words = "banana", "apple", "cherry"
sorted_words = sort(words)
assert "sort text first", first(sorted_words), "apple"

assert "reverse last becomes first", first(reverse(sort(nums))), 9

joined = join(nums)
assert "join default", joined, "3, 1, 4, 1, 5, 9, 2, 6"

parts = "a", "b", "c"
assert "join custom sep", join(parts, "-"), "a-b-c"

csv = split("a,b,c", ",")
assert "split count", count(csv), 3
assert "split first", first(csv), "a"
assert "split last", last(csv), "c"

assert "min of nums", min(nums), 1
assert "max of nums", max(nums), 9

try
- x = first("notalist")
catch
- assert "first on text caught", YES, YES

try
- y = sort(42)
catch
- assert "sort on number caught", YES, YES

try
- z = reverse(nothing)
catch
- assert "reverse on nothing caught", YES, YES
