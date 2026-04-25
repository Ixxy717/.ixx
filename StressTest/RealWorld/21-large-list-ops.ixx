# Large list operations — predefined 90-item list, sort, reverse, join

nums = 50, 23, 87, 12, 65, 34, 91, 7, 78, 45, 19, 62, 38, 74, 3, 56, 29, 83, 47, 96, 15, 68, 31, 85, 42, 9, 71, 26, 58, 94, 21, 64, 37, 80, 11, 53, 28, 76, 43, 89, 6, 59, 32, 77, 48, 13, 70, 25, 82, 39, 95, 18, 61, 36, 79, 44, 8, 55, 30, 84, 41, 97, 16, 69, 33, 75, 49, 10, 57, 24, 81, 40, 93, 20, 63, 35, 72, 46, 17, 60, 27, 73, 4, 90, 5, 52, 22, 67, 14, 86

say "Total items: " + count(nums)

sorted_asc  = sort(nums)
sorted_desc = reverse(sorted_asc)

say "Sorted ascending first: " + first(sorted_asc)
say "Sorted ascending last:  " + last(sorted_asc)
say "Reversed first:         " + first(sorted_desc)

joined = join(sorted_asc, ",")
say "Joined length (chars): " + count(joined)

original_count = count(nums)
sorted_count   = count(sorted_asc)
say "Count preserved: " + text(original_count is sorted_count)

# Verify min/max match sort order
min_val = min(nums)
max_val = max(nums)
say "Min: " + min_val + "  Max: " + max_val

if first(sorted_asc) is min_val
- say "PASS: sorted first = min"
if last(sorted_asc) is max_val
- say "PASS: sorted last = max"
