# Write a multi-line file, process line by line with readlines

data_path = "StressTest/tmp/rw-32-data.txt"

write data_path, "Alice,90,85,92\n"
append data_path, "Bob,70,75,80\n"
append data_path, "Carol,95,98,91\n"
append data_path, "David,60,55,65\n"
append data_path, "Eve,88,82,90\n"

lines = readlines(data_path)
say "Records: " + count(lines)

name_count = 0
loop each line in lines
- if count(line) more than 0
-- parts = split(line, ",")
-- name = first(parts)
-- name_count = name_count + 1
-- say "Student " + name_count + ": " + name

say "Total students: " + name_count
say "First line: " + first(lines)
say "Last line:  " + last(lines)
