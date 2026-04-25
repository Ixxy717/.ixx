use "Modules/asserts.ixx"

say color("cyan", "hard 54 generated file 60")
path = "StressTest/tmp/hard-generated-file-60.txt"
write path, "start"
n = 60
loop n more than 0
- append path, "|x"
- n = n - 1

content = read(path)
assert "generated file exists 60", exists(path), YES

large = NO
if count(content) more than 60
- large = YES
assert "generated file grew 60", large, YES

append path, "|done"
final = read(path)
has_done = NO
if final contains "done"
- has_done = YES
assert "generated file done 60", has_done, YES
say color("green", "hard 54 complete")
