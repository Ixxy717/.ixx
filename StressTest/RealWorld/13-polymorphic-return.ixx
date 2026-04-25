# Function returns different types depending on input

function describe x
- t = type(x)
- if t is "number"
-- if x more than 0
--- return "positive number"
-- if x is 0
--- return 0
-- return "negative number"
- if t is "text"
-- if count(x) is 0
--- return nothing
-- return upper(x)
- if t is "bool"
-- if x
--- return 1
-- return 0
- if t is "list"
-- return count(x)
- return nothing

say describe(42)
say describe(-5)
say describe(0)
say describe("hello")
say describe("")
say describe(YES)
say describe(NO)

my_list = "a", "b", "c", "d"
say describe(my_list)

say describe(nothing)

# Verify return types
say type(describe(42))
say type(describe("hi"))
say type(describe(YES))
say type(describe(my_list))
