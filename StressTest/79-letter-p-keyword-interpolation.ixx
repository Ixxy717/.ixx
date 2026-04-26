say color("cyan", "79 letter-p keyword interpolation")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
- else
-- say color("red", "FAIL " + name + " => got: " + text(got) + " expected: " + text(expected))

# Basic keyword literals
yes_text = "{YES}"
assert "yes-as-text", yes_text, "YES"

no_text = "{NO}"
assert "no-as-text", no_text, "NO"

nothing_text = "{nothing}"
assert "nothing-as-text", nothing_text, "nothing"

# Inline in a sentence
active_msg = "Active: {YES}"
assert "yes-in-sentence", active_msg, "Active: YES"

status_msg = "Status: {NO}"
assert "no-in-sentence", status_msg, "Status: NO"

value_msg = "Value: {nothing}"
assert "nothing-in-sentence", value_msg, "Value: nothing"

# Lowercase aliases (yes / no)
yes_lower = "{yes}"
assert "yes-lowercase", yes_lower, "YES"

no_lower = "{no}"
assert "no-lowercase", no_lower, "NO"

# Normal variable interpolation still works
name = "Ixxy"
greeting = "Hello, {name}"
assert "normal-var-interp", greeting, "Hello, Ixxy"

# Multiple keywords in one string
combo = "{YES} or {NO}"
assert "yes-and-no-combo", combo, "YES or NO"
