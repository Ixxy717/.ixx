say color("cyan", "03 builtins text")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

messy = "  hello IXX  "
clean = trim(messy)
assert "trim", clean, "hello IXX"

uppered = upper(clean)
assert "upper", uppered, "HELLO IXX"

lowered = lower(uppered)
assert "lower", lowered, "hello ixx"

replaced = replace(lowered, "ixx", "computer")
assert "replace", replaced, "hello computer"

parts = split("alpha,beta,gamma", ",")
joined = join(parts, " | ")
assert "split join sep", joined, "alpha | beta | gamma"

parts2 = split("one two three")
joined2 = join(parts2)
assert "split default join default", joined2, "one, two, three"

astext = text(YES)
assert "text yes", astext, "YES"

astext = text(nothing)
assert "text nothing", astext, "nothing"

charcount = count("hello")
assert "count text", charcount, 5

concat = "I" + "XX"
assert "string plus string", concat, "IXX"

concat2 = "Score: " + 42
assert "string plus number", concat2, "Score: 42"

say color("green", "03 builtins text complete")
