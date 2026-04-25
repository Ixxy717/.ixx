use "Modules/asserts.ixx"
use "Modules/Mega/string-tools.ixx"

say color("cyan", "hard 16 mega string tools")
assert "slugify spaces", slugify("  Hello World Test  "), "hello-world-test"
assert "slugify underscores", slugify("HELLO_WORLD"), "hello-world"
assert "surround", surround("core", "[", "]"), "[core]"
assert "csv sort", csv_sort("delta,alpha,charlie,bravo"), "alpha,bravo,charlie,delta"
say color("green", "hard 16 complete")
