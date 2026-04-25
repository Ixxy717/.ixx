# CSV simulation — write, parse, aggregate

csv_path = "StressTest/tmp/rw-46-data.csv"

write csv_path, "Name,Score,Grade\n"
append csv_path, "Alice,95,A\n"
append csv_path, "Bob,82,B\n"
append csv_path, "Carol,74,C\n"
append csv_path, "David,91,A\n"
append csv_path, "Eve,68,D\n"
append csv_path, "Frank,88,B\n"
append csv_path, "Grace,77,C\n"

lines = readlines(csv_path)
say "Header: " + first(lines)
say "Rows: " + (count(lines) - 1)

a_grades = 0
b_grades = 0
student_count = 0

loop each line in lines
- if line contains ","
-- parts = split(line, ",")
-- name = first(parts)
-- if name is not "Name"
--- student_count = student_count + 1
--- grade = last(parts)
--- if grade is "A"
---- a_grades = a_grades + 1
--- if grade is "B"
---- b_grades = b_grades + 1

say "Students: " + student_count
say "A grades: " + a_grades
say "B grades: " + b_grades

if a_grades is 2
- say "PASS: 2 A grades"
if b_grades is 2
- say "PASS: 2 B grades"
