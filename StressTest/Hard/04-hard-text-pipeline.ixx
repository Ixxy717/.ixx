use "Modules/asserts.ixx"

say color("cyan", "hard 04 text pipeline")
raw = "delta,alpha,charlie,bravo"
parts = split(raw, ",")
sorted = sort(parts)
joined = join(sorted, "|")
assert "sorted csv", joined, "alpha|bravo|charlie|delta"

rev = reverse(sorted)
revjoined = join(rev, " -> ")
assert "reverse joined", revjoined, "delta -> charlie -> bravo -> alpha"

uppered = upper(joined)
assert "upper pipeline", uppered, "ALPHA|BRAVO|CHARLIE|DELTA"

replaced = replace(uppered, "|", ", ")
assert "replace pipeline", replaced, "ALPHA, BRAVO, CHARLIE, DELTA"

messy = "    keep this clean    "
assert "trim pipeline", trim(messy), "keep this clean"
say color("green", "hard 04 complete")
