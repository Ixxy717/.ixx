use "Modules/asserts.ixx"

say color("cyan", "hard 59 generated file 135")
path = "StressTest/tmp/hard-generated-file-135.txt"
write path, "start"
n = 135
loop n more than 0
- append path, "|x"
- n = n - 1

content = read(path)
assert "generated file exists 135", exists(path), YES

large = NO
if count(content) more than 135
- large = YES
assert "generated file grew 135", large, YES

append path, "|done"
final = read(path)
has_done = NO
if final contains "done"
- has_done = YES
assert "generated file done 135", has_done, YES
say color("green", "hard 59 complete")
