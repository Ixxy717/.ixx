function sum_items values
- total = 0
- loop each value in values
-- total = total + value
- return total

function join_items values, sep
- result = ""
- first_item = YES
- loop each value in values
-- if first_item
--- result = value
--- first_item = NO
-- else
--- result = result + sep + value
- return result

function count_contains values, needle
- total = 0
- loop each value in values
-- if value contains needle
--- total = total + 1
- return total

function first_match values, needle
- loop each value in values
-- if value contains needle
--- return value
- return nothing
