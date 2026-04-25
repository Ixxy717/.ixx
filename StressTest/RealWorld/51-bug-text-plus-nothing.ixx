# BUG PROBE: "text" + nothing behavior
# Under v0.6.6.1: silently produces "hellonothing" (wrong)
# Under v0.6.7: should raise IXXRuntimeError (fix planned)

result = "no-run"
caught = NO

try
- result = "hello" + nothing
- caught = NO
catch
- caught = YES
- result = "error-caught"

say "text + nothing result: " + result
say "Error caught: " + text(caught)

if caught
- say "STATUS: v0.6.7 behavior (error raised)"
else
- say "STATUS: v0.6.6.x behavior (silent coercion, result='" + result + "')"
