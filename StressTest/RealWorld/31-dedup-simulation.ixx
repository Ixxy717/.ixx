# Simulate deduplication — detect and count unique items

function count_unique lst
- unique_count = 0
- seen = ","
- loop each item in lst
-- key = "," + text(item) + ","
-- if seen contains key
--- say "  Duplicate: " + item
-- else
--- seen = seen + text(item) + ","
--- unique_count = unique_count + 1
- return unique_count

data1 = 5, 3, 8, 3, 5, 9, 1, 8, 2, 5, 7
say "Data: " + join(data1, ", ")
say "Total: " + count(data1)
u1 = count_unique(data1)
say "Unique: " + u1

data2 = "apple", "banana", "apple", "cherry", "banana", "date"
say "---"
say "Words: " + join(data2, ", ")
u2 = count_unique(data2)
say "Unique words: " + u2
