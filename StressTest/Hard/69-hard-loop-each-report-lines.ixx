use "Modules/asserts.ixx"

say color("cyan", "hard 69 loop each report lines")
path = "StressTest/tmp/hard-69-loop-report.txt"
lines = "alpha", "beta", "gamma", "delta", "epsilon"

write path, "report:"
loop each line in lines
- append path, "|"
- append path, upper(line)

content = read(path)
assert "report content", content, "report:|ALPHA|BETA|GAMMA|DELTA|EPSILON"

parts = split(content, "|")
assert "report parts count", count(parts), 6
assert "last report part", last(parts), "EPSILON"
say color("green", "hard 69 complete")
