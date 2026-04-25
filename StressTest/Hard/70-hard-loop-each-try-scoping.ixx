use "Modules/asserts.ixx"

say color("cyan", "hard 70 loop each try scoping")
values = "10", "bad", "20", "nope", "30"
last_raw = ""
total = 0
fail_count = 0

loop each last_raw in values
- try
-- total = total + number(last_raw)
- catch
-- fail_count = fail_count + 1

assert "try total", total, 60
assert "try fail count", fail_count, 2
assert "predeclared loop var last value", last_raw, "30"

safe = "outer"
letters = "a", "b"
loop each item in letters
- safe = item

assert "body can update outer", safe, "b"
say color("green", "hard 70 complete")
