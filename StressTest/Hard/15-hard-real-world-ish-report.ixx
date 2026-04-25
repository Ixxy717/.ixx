use "Modules/asserts.ixx"
use "Modules/chain-c.ixx"
use std "date"
use std "time"

say color("cyan", "hard 15 real world-ish report")
score = chain_c_answer()
month_ok = is_valid_month(4)
greeting = time_greeting(9)
ram = do("ram used")

path = "StressTest/tmp/hard-real-world-report.txt"
write path, "IXX HARD REPORT"
append path, " | score="
append path, score
append path, " | month_ok="
append path, month_ok
append path, " | greeting="
append path, greeting
append path, " | ram="
append path, ram

content = read(path)

assert "score from import chain", score, 42
assert "month ok", month_ok, YES
assert "greeting", greeting, "Good morning"

long_report = NO
if count(content) more than 70
- long_report = YES
assert "real report length", long_report, YES

has_score = NO
if content contains "score=42"
- has_score = YES
assert "real report has score", has_score, YES

say color("green", "hard 15 complete")
