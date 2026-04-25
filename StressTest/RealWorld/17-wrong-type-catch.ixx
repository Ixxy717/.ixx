# Wrong type builtins caught and recovered

result1 = "not set"
try
- result1 = upper(42)
catch
- result1 = upper(text(42))
- say "Caught upper(number), recovered: " + result1

result2 = "not set"
try
- result2 = count(YES)
catch
- say "Caught count(bool): " + error
- result2 = "count-failed"

result3 = "not set"
try
- result3 = first("not a list")
catch
- say "Caught first(text): " + error
- result3 = "first-failed"

result4 = "not set"
try
- result4 = round("abc")
catch
- say "Caught round(text): " + error
- result4 = "round-failed"

result5 = "not set"
try
- result5 = abs("hello")
catch
- say "Caught abs(text): " + error
- result5 = "abs-failed"

say "Results: " + result1 + " | " + result2 + " | " + result3 + " | " + result4 + " | " + result5
say "All 5 type errors caught and handled."
