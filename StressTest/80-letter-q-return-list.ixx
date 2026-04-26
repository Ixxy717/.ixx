say color("cyan", "80 letter-q return list literal")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
- else
-- say color("red", "FAIL " + name + " => got: " + text(got) + " expected: " + text(expected))

# Q1: function returns number list literal
function get_nums
- return 1, 2, 3

nums = get_nums()
assert "count-number-list", count(nums), 3
assert "first-number-list", first(nums), 1
assert "last-number-list",  last(nums),  3

# Q1: function returns text list literal
function names
- return "Ixxy", "Lune"

n = names()
assert "count-text-list",   count(n),   2
assert "first-text-list",   first(n),   "Ixxy"
assert "last-text-list",    last(n),    "Lune"

# Q1: function returns mixed list literal
function mixed
- return YES, NO, nothing, "done"

m = mixed()
assert "count-mixed",       count(m),   4

# Q1: loop each over returned list
total = 0
loop each x in get_nums()
- total = total + x

assert "loop-each-total",   total,      6

# Q1: return function call with comma args still works as single call
parts = "a", "b", "c"

function joined
- return join(parts, ", ")

assert "return-join-call",  joined(),   "a, b, c"

# Q1: return single value still works
function give_five
- return 5

assert "return-single-num", give_five(), 5

# Q1: return list variable still works
function get_list
- items = 10, 20, 30
- return items

gl = get_list()
assert "return-list-var",   count(gl),  3

# Q1: two-item list
function pair
- return 7, 8

assert "count-pair",        count(pair()), 2

say color("green", "80 letter-q done")
