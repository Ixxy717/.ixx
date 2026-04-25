# Every builtin called with every valid type combination that should succeed

say "=== TEXT BUILTINS ==="
say upper("hello world")
say lower("HELLO WORLD")
say trim("  padded  ")
say replace("hello world", "world", "IXX")
wds = split("a b c d e")
say count(wds)
say join(wds, "-")
say join(wds)
say join(wds, "")

say "=== NUMERIC BUILTINS ==="
say round(3.14159, 2)
say round(3.7)
say round(-2.5, 1)
say abs(-42)
say abs(42)
say abs(0)
say min(10, 5, 8, 3, 7)
say max(10, 5, 8, 3, 7)
nums = 3, 1, 4, 1, 5, 9, 2, 6, 5
say min(nums)
say max(nums)

say "=== LIST BUILTINS ==="
data = 5, 2, 8, 1, 9, 3, 7, 4, 6
say first(data)
say last(data)
sorted = sort(data)
say first(sorted)
say last(sorted)
rev = reverse(data)
say first(rev)
say count(data)

say "=== TYPE AND CONVERSION ==="
say type(42)
say type("hello")
say type(YES)
say type(nothing)
say type(data)
say text(42)
say text(3.14)
say text(YES)
say text(NO)
say text(nothing)
say number("42")
say number("3.14")
say number(42)
say number(3.14)
say count("hello")
say count(data)

say "=== FILE BUILTINS ==="
write "StressTest/tmp/rw-27-test.txt", "hello world"
say exists("StressTest/tmp/rw-27-test.txt")
say read("StressTest/tmp/rw-27-test.txt")
append "StressTest/tmp/rw-27-test.txt", " appended"
say read("StressTest/tmp/rw-27-test.txt")
lines = readlines("StressTest/tmp/rw-27-test.txt")
say count(lines)

say "=== COLOR ==="
say color("red", "red text")
say color("green", "green text")
say color("cyan", "cyan text")
say color("yellow", "yellow text")
say color("bold", "bold text")
