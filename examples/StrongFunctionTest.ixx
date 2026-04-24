say "Manual function stress test"

name = "Outside"

function divider
- say "----------------"

function greet who
- say "Hello, {who}"

function add a, b
- return a + b

function grade score
- if score at least 90
-- return "A"
- if score at least 80
-- return "B"
- return "F"

function no_return
- say "Inside no_return"

function scope_test
- name = "Inside"
- say name

function factorial n
- if n at most 1
-- return 1
- previous = factorial(n - 1)
- return n * previous

divider
greet "Ixxy"

total = add(12, 8)
say "Total: {total}"

g = grade(85)
say "Grade: {g}"

empty = no_return()
say "Empty: {empty}"

scope_test
say name

fact = factorial(5)
say "5 factorial: {fact}"

items = "apple", "banana", "ixx"
amount = count(items)
kind = type(items)
say "Count: {amount}"
say "Type: {kind}"

num = number("42")
txt = text(num)
say "Number: {num}"
say "Text: {txt}"

say "Missing variable test: {ghost}"