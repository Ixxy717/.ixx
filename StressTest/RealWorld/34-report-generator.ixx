# Build a formatted text report, write to file and read back

report_path = "StressTest/tmp/rw-34-report.txt"

function divider
- return "================================"

function section title
- return divider() + "\n" + upper(title) + "\n" + divider()

write report_path, section("IXX System Report") + "\n"
append report_path, "Version: 0.6.7\n"
append report_path, "Status: Running\n"
append report_path, "\n"
append report_path, section("Department Summary") + "\n"
append report_path, "Engineering:  25 staff\n"
append report_path, "Marketing:    12 staff\n"
append report_path, "Sales:        18 staff\n"
append report_path, "Support:       8 staff\n"
append report_path, "\n"
append report_path, section("End of Report") + "\n"

report_text = read(report_path)
lines = readlines(report_path)

say "Report written successfully"
say "Lines: " + count(lines)
say "Characters: " + count(report_text)
say "First line: " + first(lines)

# Verify content
if report_text contains "Engineering"
- say "PASS: department found in report"
if report_text contains "IXX"
- say "PASS: header found"
