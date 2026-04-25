function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

assert "text(42)", text(42), "42"
assert "text(3.14)", text(3.14), "3.14"
assert "text(YES)", text(YES), "YES"
assert "text(NO)", text(NO), "NO"
assert "text(nothing)", text(nothing), "nothing"

assert "type(42)", type(42), "number"
assert "type('hi')", type("hi"), "text"
assert "type(YES)", type(YES), "bool"
assert "type(nothing)", type(nothing), "nothing"

mylist = 1, 2
assert "type(list)", type(mylist), "list"

assert "number('42')", number("42"), 42
assert "number('3.14')", number("3.14"), 3.14
assert "number(10)", number(10), 10

assert "count text", count("hello"), 5
mylist3 = 1, 2, 3
assert "count list", count(mylist3), 3

try
- x = number("abc")
catch
- assert "number bad text caught", YES, YES

try
- y = number(YES)
catch
- assert "number bool caught", YES, YES

try
- z = number(nothing)
catch
- assert "number nothing caught", YES, YES

try
- w = count(42)
catch
- assert "count number caught", YES, YES
