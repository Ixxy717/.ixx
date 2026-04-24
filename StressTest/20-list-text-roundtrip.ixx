say color("cyan", "20 list text roundtrip")
function assert name, got, expected
- if got is expected
-- say "PASS " + name
-- return
- say "FAIL " + name
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

csv = "delta,alpha,charlie,bravo"
items = split(csv, ",")
sorteditems = sort(items)
joined = join(sorteditems, ",")
assert "csv sort roundtrip", joined, "alpha,bravo,charlie,delta"

words = split("one two three four")
reversed = reverse(words)
sentence = join(reversed, " ")
assert "word reverse sentence", sentence, "four three two one"

withspaces = "  red | green | blue  "
clean = trim(withspaces)
parts = split(clean, "|")
firstpart = trim(first(parts))
lastpart = trim(last(parts))
assert "trim split first", firstpart, "red"
assert "trim split last", lastpart, "blue"

say color("green", "20 list text roundtrip complete")
