# Boolean logic matrix — all combinations, truthy/falsy values

function logic_test a, b
- and_result = a and b
- or_result = a or b
- say "  " + text(a) + " AND " + text(b) + " = " + text(and_result)
- say "  " + text(a) + " OR  " + text(b) + " = " + text(or_result)

say "=== BOOLEAN LOGIC MATRIX ==="
say "YES, YES:"
logic_test YES, YES
say "YES, NO:"
logic_test YES, NO
say "NO, YES:"
logic_test NO, YES
say "NO, NO:"
logic_test NO, NO

say "=== NOT ==="
say "not YES = " + text(not YES)
say "not NO  = " + text(not NO)

say "=== TRUTHY / FALSY ==="
if 1
- say "1 is truthy"
zero_val = 0
if zero_val
- say "0 is truthy"
else
- say "0 is falsy"
if "hello"
- say "'hello' is truthy"
empty_str = ""
if empty_str
- say "'' is truthy"
else
- say "'' is falsy"
nothing_val = nothing
if nothing_val
- say "nothing is truthy"
else
- say "nothing is falsy"

say "=== CHAINED CONDITIONS ==="
x = 5
if x more than 0 and x less than 10
- say "5 is between 0 and 10"
if x less than 0 or x more than 3
- say "5 is < 0 or > 3"
not_big = not (x more than 10)
if not_big
- say "5 is not > 10"
