# List partition — separate positives, negatives, and zeros

numbers = 5, -3, 8, -1, 0, 7, -9, 2, -4, 6, -2, 3, 0, -7, 11

pos_sum = 0
neg_sum = 0
pos_count = 0
neg_count = 0
zero_count = 0

loop each n in numbers
- if n more than 0
-- pos_sum = pos_sum + n
-- pos_count = pos_count + 1
- if n less than 0
-- neg_sum = neg_sum + n
-- neg_count = neg_count + 1
- if n is 0
-- zero_count = zero_count + 1

say "Dataset: " + join(numbers, ", ")
say "Total: " + count(numbers)
say "Positives: " + pos_count + " (sum=" + pos_sum + ")"
say "Negatives: " + neg_count + " (sum=" + neg_sum + ")"
say "Zeros:     " + zero_count
say "Net sum:   " + (pos_sum + neg_sum)

if pos_count + neg_count + zero_count is count(numbers)
- say "PASS: counts add up"
