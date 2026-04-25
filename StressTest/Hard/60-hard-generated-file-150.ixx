use "Modules/asserts.ixx"

say color("cyan", "hard 60 generated file 150")
path = "StressTest/tmp/hard-generated-file-150.txt"
write path, "start"
n = 150
loop n more than 0
- append path, "|x"
- n = n - 1

content = read(path)
assert "generated file exists 150", exists(path), YES

large = NO
if count(content) more than 150
- large = YES
assert "generated file grew 150", large, YES

append path, "|done"
final = read(path)
has_done = NO
if final contains "done"
- has_done = YES
assert "generated file done 150", has_done, YES
say color("green", "hard 60 complete")
