use "Modules/asserts.ixx"
use "Modules/side-effect.ixx"

say color("cyan", "hard 07 import side effects")
marker = "StressTest/tmp/hard-import-side-effect-should-not-exist.txt"
assert "import top-level write blocked", exists(marker), NO
assert "imported safe function works", side_effect_safe(), "SAFE"
say color("green", "hard 07 complete")
