say "IXX Function Stress Test"
say "------------------------"

base_name = "Ixxy"
global_score = 10

function divider
- say "------------------------"

function greet name
- say "Hello, {name}"

function add a, b
- return a + b

function multiply a, b
- return a * b

function bonus score
- extra = multiply(score, 2)
- total = add(score, extra)
- return total

function grade score
- if score at least 90
-- return "A"
- if score at least 80
-- return "B"
- if score at least 70
-- return "C"
- if score at least 60
-- return "D"
- return "F"

function factorial n
- if n at most 1
-- return 1
- previous = factorial(n - 1)
- result = n * previous
- return result

function countdown n
- loop n more than 0
-- say "Countdown: {n}"
-- n = n - 1
- return "done"

function local_scope_test
- base_name = "Inside function"
- global_score = 999
- say "Local name: {base_name}"
- say "Local score: {global_score}"

function no_return
- say "This function returns nothing"

function list_check items
- amount = count(items)
- say "List count: {amount}"
- if items contains "ixx"
-- return "IXX found"
- return "IXX missing"

function nested_math x
- first = add(x, 5)
- second = multiply(first, 3)
- third = bonus(second)
- return third

function identity_number value
- return value

function identity_text value
- return value

function return_list
- items = "alpha", "beta", "ixx"
- return items

function use_returned_list
- returned = return_list()
- amount = count(returned)
- return amount

divider
greet base_name

score = add(40, 45)
say "Score: {score}"

letter = grade(score)
say "Grade: {letter}"

boosted = bonus(global_score)
say "Boosted global score: {boosted}"

fact5 = factorial(5)
say "Factorial 5: {fact5}"

fact7 = factorial(7)
say "Factorial 7: {fact7}"

done = countdown(3)
say "Countdown result: {done}"

local_scope_test
say "Global name still: {base_name}"
say "Global score still: {global_score}"

empty = no_return()
say "No return result: {empty}"

langs = "python", "rust", "ixx", "go"
result = list_check(langs)
say result

stress = nested_math(4)
say "Nested math result: {stress}"

id_num = identity_number(123)
say "Identity number: {id_num}"

id_text = identity_text("Ixxy")
say "Identity text: {id_text}"

list_amount = use_returned_list()
say "Returned list count: {list_amount}"

text_score = text(score)
say "Text score: {text_score}"

number_score = number("123")
say "Number score: {number_score}"

score_type = type(score)
list_type = type(langs)
nothing_type = type(empty)

say "Score type: {score_type}"
say "List type: {list_type}"
say "Nothing type: {nothing_type}"

divider
say "Function stress test complete"