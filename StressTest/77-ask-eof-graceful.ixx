say color("cyan", "77 ask eof graceful")

function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

# ask() with no stdin available raises a catchable IXXRuntimeError.
# The error message should mention "cancelled" or "stdin".
was_caught = NO
caught_msg = ""

try
- name = ask("Enter name: ")
catch
- was_caught = YES
- caught_msg = error

assert "ask eof raises error", was_caught, YES

msg_ok = caught_msg contains "cancelled" or caught_msg contains "stdin"
assert "ask eof friendly message", msg_ok, YES

say color("green", "77 ask eof graceful complete")
