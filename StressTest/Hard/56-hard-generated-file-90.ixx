use "Modules/asserts.ixx"

say color("cyan", "hard 56 generated file 90")
path = "StressTest/tmp/hard-generated-file-90.txt"
write path, "start"
n = 90
loop n more than 0
- append path, "|x"
- n = n - 1

content = read(path)
assert "generated file exists 90", exists(path), YES

large = NO
if count(content) more than 90
- large = YES
assert "generated file grew 90", large, YES

append path, "|done"
final = read(path)
has_done = NO
if final contains "done"
- has_done = YES
assert "generated file done 90", has_done, YES
say color("green", "hard 56 complete")
