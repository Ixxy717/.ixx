use "Modules/asserts.ixx"

say color("cyan", "hard 05 file roundtrip")
path = "StressTest/tmp/hard-file-roundtrip.txt"
write path, "start"

n = 40
loop n more than 0
- append path, "|"
- append path, n
- n = n - 1

content = read(path)
assert "file content type", type(content), "text"

long_enough = NO
if count(content) more than 80
- long_enough = YES
assert "file got large enough", long_enough, YES

append path, "|"
append path, YES
append path, "|"
append path, nothing

final = read(path)
has_yes = NO
if final contains "YES"
- has_yes = YES
assert "file contains YES display", has_yes, YES

has_nothing = NO
if final contains "nothing"
- has_nothing = YES
assert "file contains nothing display", has_nothing, YES

say color("green", "hard 05 complete")
