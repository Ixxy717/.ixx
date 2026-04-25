# Batch file rename planner — builds new names, writes a report

report_path = "StressTest/tmp/rw-07-rename-report.txt"

old_names = "IMG_001.jpg", "IMG_002.jpg", "IMG_003.jpg", "IMG_004.jpg", "IMG_005.jpg"
prefix = "vacation_2024_"
counter = 1

write report_path, "RENAME PLAN\n"
append report_path, "===========\n"

loop each old in old_names
- new_name = prefix + counter + ".jpg"
- line = old + " -> " + new_name + "\n"
- append report_path, line
- counter = counter + 1

append report_path, "===========\n"
append report_path, "Total: " + count(old_names) + " files\n"

lines = readlines(report_path)
say "Report written: " + count(lines) + " lines"
loop each line in lines
- say line
