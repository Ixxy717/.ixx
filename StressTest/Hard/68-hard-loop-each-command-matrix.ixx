use "Modules/asserts.ixx"

say color("cyan", "hard 68 loop each command matrix")
commands = "ram used", "cpu info", "disk space"
counted = 0
combined = ""

loop each cmd in commands
- out = do(cmd)
- if count(out) more than 0
-- counted = counted + 1
- combined = combined + out

assert "all do commands returned text", counted, 3
assert "combined type", type(combined), "text"

long = NO
if count(combined) more than 20
- long = YES
assert "combined command output long", long, YES
say color("green", "hard 68 complete")
