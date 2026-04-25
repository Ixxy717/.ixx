use "Modules/asserts.ixx"

say color("cyan", "hard 55 generated file 75")
path = "StressTest/tmp/hard-generated-file-75.txt"
write path, "start"
n = 75
loop n more than 0
- append path, "|x"
- n = n - 1

content = read(path)
assert "generated file exists 75", exists(path), YES

large = NO
if count(content) more than 75
- large = YES
assert "generated file grew 75", large, YES

append path, "|done"
final = read(path)
has_done = NO
if final contains "done"
- has_done = YES
assert "generated file done 75", has_done, YES
say color("green", "hard 55 complete")
