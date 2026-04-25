use "Modules/asserts.ixx"
use "Modules/Mega/pipeline-c.ixx"

say color("cyan", "hard 62 import plus try heavy")
ok = pipeline_b_score()
assert "pipeline before errors", ok, 210

caught = NO
try
- x = read("StressTest/tmp/does-not-exist-hard-62.txt")
catch
- caught = YES

assert "caught missing read", caught, YES
assert "pipeline after errors", pipeline_b_score(), 210
say color("green", "hard 62 complete")
