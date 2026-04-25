use "Modules/asserts.ixx"
use "Modules/Mega/string-tools.ixx"

say color("cyan", "hard 44 generated text 4")
base = "zulu,echo,bravo,alpha,item4"
sorted = csv_sort(base)
assert "generated csv sort type 4", type(sorted), "text"

has_alpha = NO
if sorted contains "alpha"
- has_alpha = YES
assert "generated sorted has alpha 4", has_alpha, YES

slug = slugify(" Test Item 4 " )
assert "generated slug 4", slug, "test-item-4"
say color("green", "hard 44 complete")
