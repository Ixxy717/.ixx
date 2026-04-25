use "Modules/asserts.ixx"

say color("cyan", "hard 13 interpolation display file")
path = "StressTest/tmp/hard-interpolation-display.txt"
items = "red", "green", "blue"

# IXX interpolation resolves variables, not raw literals or expressions.
yesval = YES
noval = NO
nothingval = nothing
mathval = 3 + 4

write path, "bools {yesval} {noval}"
append path, " | nothing {nothingval}"
append path, " | list {items}"
append path, " | math {mathval}"

content = read(path)

has_yes = NO
if content contains "YES"
- has_yes = YES
assert "interpolated YES", has_yes, YES

has_no = NO
if content contains "NO"
- has_no = YES
assert "interpolated NO", has_no, YES

has_nothing = NO
if content contains "nothing"
- has_nothing = YES
assert "interpolated nothing", has_nothing, YES

has_list = NO
if content contains "red, green, blue"
- has_list = YES
assert "interpolated list", has_list, YES

has_math = NO
if content contains "7"
- has_math = YES
assert "interpolated math", has_math, YES

say color("green", "hard 13 complete")
