use "Modules/asserts.ixx"

say color("cyan", "hard 53 generated file 45")
path = "StressTest/tmp/hard-generated-file-45.txt"
write path, "start"
n = 45
loop n more than 0
- append path, "|x"
- n = n - 1

content = read(path)
assert "generated file exists 45", exists(path), YES

large = NO
if count(content) more than 45
- large = YES
assert "generated file grew 45", large, YES

append path, "|done"
final = read(path)
has_done = NO
if final contains "done"
- has_done = YES
assert "generated file done 45", has_done, YES
say color("green", "hard 53 complete")
