use "Modules/asserts.ixx"
use "Modules/Mega/pipeline-c.ixx"
use std "date"

say color("cyan", "hard 65 final composite")
path = "StressTest/tmp/hard-final-composite.txt"
summary = pipeline_c_file(path)
month = is_valid_month(12)
ram = do("ram used")

write path, summary
append path, "|month="
append path, month
append path, "|ram="
append path, ram

final = read(path)
assert "final file exists", exists(path), YES
assert "final month true", month, YES

has_score = NO
if final contains "score=210"
- has_score = YES
assert "final has score", has_score, YES

has_ram = NO
if count(ram) more than 0
- has_ram = YES
assert "final ram nonempty", has_ram, YES
say color("green", "hard 65 complete")
