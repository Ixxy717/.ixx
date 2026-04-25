# Statistical operations on a dataset

dataset = 45, 67, 23, 89, 34, 56, 78, 12, 90, 43, 65, 38, 72, 29, 81

total = 0
loop each x in dataset
- total = total + x

n = count(dataset)
avg = round(total / n, 2)
minimum = min(dataset)
maximum = max(dataset)
data_range = maximum - minimum
sorted_data = sort(dataset)

say "Dataset: " + join(dataset, ", ")
say "Count:   " + n
say "Sum:     " + total
say "Average: " + avg
say "Min:     " + minimum
say "Max:     " + maximum
say "Range:   " + data_range
say "Sorted:  " + join(sorted_data, ", ")

above_avg = 0
loop each x in dataset
- if x more than avg
-- above_avg = above_avg + 1

say "Above average: " + above_avg + " of " + n

if minimum is 12
- say "PASS: min=12"
if maximum is 90
- say "PASS: max=90"
