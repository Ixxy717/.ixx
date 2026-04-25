use "Modules/asserts.ixx"

say color("cyan", "hard 52 generated file 30")
path = "StressTest/tmp/hard-generated-file-30.txt"
write path, "start"
n = 30
loop n more than 0
- append path, "|x"
- n = n - 1

content = read(path)
assert "generated file exists 30", exists(path), YES

large = NO
if count(content) more than 30
- large = YES
assert "generated file grew 30", large, YES

append path, "|done"
final = read(path)
has_done = NO
if final contains "done"
- has_done = YES
assert "generated file done 30", has_done, YES
say color("green", "hard 52 complete")
