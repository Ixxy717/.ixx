say color("cyan", "76 letter-c string escapes")

function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: " + text(expected)
- say "Got: " + text(got)
- crash = number("ASSERT_FAIL")

# \n: write multi-line content and read it back
write "StressTest/tmp/c-escape-nl.txt", "one\ntwo\nthree"
lines = readlines("StressTest/tmp/c-escape-nl.txt")
assert "newline-line-count", count(lines), 3
assert "newline-first-line", first(lines), "one"
assert "newline-last-line",  last(lines), "three"

# \n: each line written separately still produces separate lines
write "StressTest/tmp/c-escape-sep.txt", "alpha\nbeta"
sep_lines = readlines("StressTest/tmp/c-escape-sep.txt")
assert "newline-sep-count", count(sep_lines), 2
assert "newline-sep-first", first(sep_lines), "alpha"

# \t: split on tab separator
parts = split("col1\tcol2\tcol3", "\t")
assert "tab-split-count", count(parts), 3
assert "tab-split-first", first(parts), "col1"
assert "tab-split-last",  last(parts), "col3"

# \\: single backslash round-trip
path_str = "C:\\Temp\\data"
assert "backslash-length-c-temp", count(path_str), 12

# interpolation + newline escape
name = "IXX"
write "StressTest/tmp/c-escape-interp.txt", "Hello\n{name}"
interp_lines = readlines("StressTest/tmp/c-escape-interp.txt")
assert "interp-line-count", count(interp_lines), 2
assert "interp-first",      first(interp_lines), "Hello"
assert "interp-second",     last(interp_lines), "IXX"

# Normal strings unaffected
assert "normal-string", "hello world", "hello world"
assert "string-concat", "hello" + " world", "hello world"

# Unknown escape passes through as-is
unknown = "a\qb"
assert "unknown-escape-length", count(unknown), 4
