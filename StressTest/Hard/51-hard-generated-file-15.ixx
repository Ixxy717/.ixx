use "Modules/asserts.ixx"

say color("cyan", "hard 51 generated file 15")
path = "StressTest/tmp/hard-generated-file-15.txt"
write path, "start"
n = 15
loop n more than 0
- append path, "|x"
- n = n - 1

content = read(path)
assert "generated file exists 15", exists(path), YES

large = NO
if count(content) more than 15
- large = YES
assert "generated file grew 15", large, YES

append path, "|done"
final = read(path)
has_done = NO
if final contains "done"
- has_done = YES
assert "generated file done 15", has_done, YES
say color("green", "hard 51 complete")
