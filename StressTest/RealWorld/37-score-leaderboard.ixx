# Score leaderboard — sort scores, find top performers

scores_raw = 88, 92, 75, 99, 83, 67, 95, 78, 90, 85, 71, 96, 82, 74, 88

say "=== SCORE LEADERBOARD ==="
say "All scores: " + join(scores_raw, ", ")
say "Total players: " + count(scores_raw)

sorted_asc  = sort(scores_raw)
sorted_desc = reverse(sorted_asc)

say "Ranked high to low: " + join(sorted_desc, ", ")
say "Top score:    " + first(sorted_desc)
say "Lowest score: " + last(sorted_desc)

total = 0
loop each s in scores_raw
- total = total + s

avg = round(total / count(scores_raw), 1)
say "Average: " + avg

above_avg = 0
loop each s in scores_raw
- if s more than avg
-- above_avg = above_avg + 1

say "Above average: " + above_avg
say "At or below:   " + (count(scores_raw) - above_avg)

if first(sorted_desc) is 99
- say "PASS: top score = 99"
if last(sorted_asc) is 99
- say "PASS: sort ascending verified"
