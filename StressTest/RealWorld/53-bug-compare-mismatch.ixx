# BUG PROBE: ordered comparison with type mismatch
# Under v0.6.6.1: "abc" more than 1 raises Python TypeError that escapes try/catch
# Under v0.6.7: should be caught as IXXRuntimeError
#
# This test will FAIL under v0.6.6.1 with an uncaught TypeError.

result = "not-caught"
try
- if "abc" more than 1
-- result = "string-bigger"
- else
-- result = "number-bigger"
catch
- result = "caught"
- say "compare mismatch: " + error

say "Type mismatch compare: " + result

result2 = "not-caught"
try
- if 5 less than "two"
-- result2 = "5 < 'two'"
catch
- result2 = "caught"
- say "compare2 error: " + error

say "Type mismatch compare2: " + result2

if result is "caught" and result2 is "caught"
- say "PASS: comparison errors caught (v0.6.7+ behavior)"
else
- say "FAIL: TypeError escaped try/catch (known v0.6.6.x bug)"
