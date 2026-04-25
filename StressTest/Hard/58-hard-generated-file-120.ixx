use "Modules/asserts.ixx"

say color("cyan", "hard 58 generated file 120")
path = "StressTest/tmp/hard-generated-file-120.txt"
write path, "start"
n = 120
loop n more than 0
- append path, "|x"
- n = n - 1

content = read(path)
assert "generated file exists 120", exists(path), YES

large = NO
if count(content) more than 120
- large = YES
assert "generated file grew 120", large, YES

append path, "|done"
final = read(path)
has_done = NO
if final contains "done"
- has_done = YES
assert "generated file done 120", has_done, YES
say color("green", "hard 58 complete")
