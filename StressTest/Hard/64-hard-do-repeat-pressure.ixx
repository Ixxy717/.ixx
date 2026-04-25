use "Modules/asserts.ixx"

say color("cyan", "hard 64 do repeat pressure")
n = 8
combined = ""
loop n more than 0
- ram = do("ram used")
- combined = combined + "|" + ram
- n = n - 1

assert "combined type", type(combined), "text"
long = NO
if count(combined) more than 20
- long = YES
assert "combined long", long, YES
say color("green", "hard 64 complete")
