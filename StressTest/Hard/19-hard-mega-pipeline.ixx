use "Modules/asserts.ixx"
use "Modules/Mega/pipeline-c.ixx"

say color("cyan", "hard 19 mega pipeline")
summary = pipeline_c_summary()
assert "pipeline score", pipeline_b_score(), 210

has_alpha = NO
if summary contains "alpha-user:92:excellent"
- has_alpha = YES
assert "pipeline alpha", has_alpha, YES

has_score = NO
if summary contains "score=210"
- has_score = YES
assert "pipeline score text", has_score, YES
say color("green", "hard 19 complete")
