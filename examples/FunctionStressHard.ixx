say "IXX Hard Function Stress Test"
say "-----------------------------"

title = "global title"
seed = 4

function line
- say "-----------------------------"

function make_list
- items = "ixx", "python", "rust", "go", "ixx"
- return items

function list_count
- items = make_list()
- amount = count(items)
- return amount

function find_ixx
- items = make_list()
- if items contains "ixx"
-- return "found ixx"
- return "missing ixx"

function shadow_test value
- title = "local title"
- seed = 999
- say "Inside title: {title}"
- say "Inside seed: {seed}"
- return value

function add a, b
- return a + b

function sub a, b
- return a - b

function mul a, b
- return a * b

function calc_chain x
- a = add(x, 10)
- b = mul(a, 2)
- c = sub(b, 5)
- return c

function classify n
- if n at most 0
-- return "zero-or-less"
- if n at most 3
-- return "small"
- if n at most 10
-- return "medium"
- return "large"

function factorial n
- if n at most 1
-- return 1
- prev = factorial(n - 1)
- return n * prev

function fib n
- if n at most 0
-- return 0
- if n is 1
-- return 1
- a = fib(n - 1)
- b = fib(n - 2)
- return a + b

function no_return
- say "No-return function ran"

function nothing_check
- empty = no_return()
- if empty
-- return "bad"
- if not empty
-- return "nothing is falsy"
- return "bad fallback"

function forward_call_test
- result = defined_later(7)
- return result

function defined_later x
- return x * 11

function nested_returns n
- if n at least 10
-- if n at least 20
--- return "twenty-plus"
-- return "ten-plus"
- return "under-ten"

function loop_sum n
- total = 0
- loop n more than 0
-- total = total + n
-- n = n - 1
- return total

line
say "Start"

counted = list_count()
say "List count: {counted}"

found = find_ixx()
say "Find result: {found}"

shadow = shadow_test(123)
say "Shadow return: {shadow}"
say "Outside title: {title}"
say "Outside seed: {seed}"

chain = calc_chain(seed)
say "Calc chain: {chain}"

class1 = classify(0)
class2 = classify(3)
class3 = classify(8)
class4 = classify(99)
say "Class 0: {class1}"
say "Class 3: {class2}"
say "Class 8: {class3}"
say "Class 99: {class4}"

fact6 = factorial(6)
say "Factorial 6: {fact6}"

fib8 = fib(8)
say "Fib 8: {fib8}"

nothing_result = nothing_check()
say "Nothing check: {nothing_result}"

forward = forward_call_test()
say "Forward call: {forward}"

nested1 = nested_returns(5)
nested2 = nested_returns(15)
nested3 = nested_returns(25)
say "Nested 5: {nested1}"
say "Nested 15: {nested2}"
say "Nested 25: {nested3}"

summed = loop_sum(10)
say "Loop sum 10: {summed}"

num = number("256")
txt = text(num)
kind_num = type(num)
kind_txt = type(txt)
kind_list = type(make_list())
kind_nothing = type(no_return())

say "Number converted: {num}"
say "Text converted: {txt}"
say "Kind num: {kind_num}"
say "Kind text: {kind_txt}"
say "Kind list: {kind_list}"
say "Kind nothing: {kind_nothing}"

line
say "Hard stress test complete"