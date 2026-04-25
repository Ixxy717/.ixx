function weighted_total values
- total = 0
- weight = 1
- loop each value in values
-- total = total + value * weight
-- weight = weight + 1
- return total

function pipe_join values
- result = ""
- loop each value in values
-- result = result + value + "|"
- return result

function count_numbers values
- total = 0
- errors = 0
- loop each value in values
-- try
--- total = total + number(value)
-- catch
--- errors = errors + 1
- return total + errors
