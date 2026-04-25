use "Modules/asserts.ixx"
use "Modules/report-hard.ixx"

say color("cyan", "hard 14 module file do combo")
path = "StressTest/tmp/hard-module-report.txt"
report = hard_report("Ixxy", path)

assert "hard report score", hard_report_score(), 42
assert "hard report type", type(report), "text"

has_name = NO
if report contains "Ixxy"
- has_name = YES
assert "hard report contains name", has_name, YES

has_score = NO
if report contains "score=42"
- has_score = YES
assert "hard report contains score", has_score, YES

say color("green", "hard 14 complete")
