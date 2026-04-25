use "Modules/asserts.ixx"
use "Modules/Mega/pipeline-c.ixx"

say color("cyan", "hard 20 mega pipeline file")
path = "StressTest/tmp/hard-mega-pipeline-file.txt"
content = pipeline_c_file(path)

assert "pipeline file exists", exists(path), YES
assert "pipeline file roundtrip", read(path), content

# The pipeline output is real but not huge; threshold should prove non-trivial size, not arbitrary bloat.
long = NO
if count(content) more than 60
- long = YES
assert "pipeline file long", long, YES

say color("green", "hard 20 complete")
