say color("cyan", "02 functions")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

globalname = "IXX"
globalnumber = 10

function divider
- say color("dim", "-----")

function announce text
- say "Announcement: {text}"

function identity value
- return value

function add a, b
- return a + b

function double x
- return x * 2

function nothingmaker
- return

function implicitnothing
- say "This returns nothing implicitly"

function readglobal
- return globalname

function shadow
- globalname = "local"
- return globalname

function factorial n
- if n at most 1
-- return 1
- previous = factorial(n - 1)
- return n * previous

function fib n
- if n at most 0
-- return 0
- if n at most 1
-- return 1
- a = fib(n - 1)
- b = fib(n - 2)
- return a + b

function fibloop n
- if n at most 0
-- return 0
- a = 0
- b = 1
- loop n more than 1
-- nextvalue = a + b
-- a = b
-- b = nextvalue
-- n = n - 1
- return b

function assignfromparam value
- copyvalue = value
- return copyvalue

function assignfromlocal
- avalue = 123
- bvalue = avalue
- return bvalue

function forwardcaller
- value = definedlater(7)
- return value

function definedlater x
- return x * 11

divider
announce "statement call works"

assert "identity number", identity(42), 42
assert "identity text", identity("hello"), "hello"
assert "add", add(5, 7), 12
assert "double", double(21), 42
assert "bare return nothing", type(nothingmaker()), "nothing"
assert "implicit nothing", type(implicitnothing()), "nothing"
assert "read global", readglobal(), "IXX"
assert "shadow returns local", shadow(), "local"
assert "global unchanged", globalname, "IXX"
assert "factorial 6", factorial(6), 720
assert "fib 8 recursive", fib(8), 21
assert "fib 7 iterative", fibloop(7), 13
assert "assign from param", assignfromparam(55), 55
assert "assign from local", assignfromlocal(), 123
assert "forward call", forwardcaller(), 77

say color("green", "02 functions complete")
