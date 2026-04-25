use "Modules/asserts.ixx"

say color("cyan", "hard 57 generated file 105")
path = "StressTest/tmp/hard-generated-file-105.txt"
write path, "start"
n = 105
loop n more than 0
- append path, "|x"
- n = n - 1

content = read(path)
assert "generated file exists 105", exists(path), YES

large = NO
if count(content) more than 105
- large = YES
assert "generated file grew 105", large, YES

append path, "|done"
final = read(path)
has_done = NO
if final contains "done"
- has_done = YES
assert "generated file done 105", has_done, YES
say color("green", "hard 57 complete")
