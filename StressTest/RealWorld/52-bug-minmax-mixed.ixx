# BUG PROBE: min/max with mixed types
# Under v0.6.6.1: min(1, "a") raises Python TypeError that escapes try/catch
# Under v0.6.7: should be caught as IXXRuntimeError
#
# This test will FAIL under v0.6.6.1 with an uncaught TypeError.
# It is expected to pass after v0.6.7 fixes min/max TypeError wrapping.

result = "not-caught"
try
- result = min(1, "a")
catch
- result = "caught"
- say "min(1,'a') error: " + error

say "min mixed types: " + result

result2 = "not-caught"
try
- result2 = max(1, "a")
catch
- result2 = "caught"
- say "max(1,'a') error: " + error

say "max mixed types: " + result2

if result is "caught" and result2 is "caught"
- say "PASS: both errors caught (v0.6.7+ behavior)"
else
- say "FAIL: TypeError escaped try/catch (known v0.6.6.x bug)"
