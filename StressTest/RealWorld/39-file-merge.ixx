# File merge — write two files, merge by combining both

file1  = "StressTest/tmp/rw-39-part1.txt"
file2  = "StressTest/tmp/rw-39-part2.txt"
merged = "StressTest/tmp/rw-39-merged.txt"

write file1, "--- Part 1 ---\nLine A1\nLine A2\nLine A3\n"
write file2, "--- Part 2 ---\nLine B1\nLine B2\nLine B3\n"

c1 = read(file1)
c2 = read(file2)

write merged, c1
append merged, c2

merged_text = read(merged)
merged_lines = readlines(merged)

say "Part 1 lines: " + count(readlines(file1))
say "Part 2 lines: " + count(readlines(file2))
say "Merged lines: " + count(merged_lines)

if merged_text contains "Part 1"
- say "PASS: part 1 content in merged"
if merged_text contains "Part 2"
- say "PASS: part 2 content in merged"
if merged_text contains "Line B3"
- say "PASS: last line present"

loop each line in merged_lines
- say line
