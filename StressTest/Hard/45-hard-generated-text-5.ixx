use "Modules/asserts.ixx"
use "Modules/Mega/string-tools.ixx"

say color("cyan", "hard 45 generated text 5")
base = "zulu,echo,bravo,alpha,item5"
sorted = csv_sort(base)
assert "generated csv sort type 5", type(sorted), "text"

has_alpha = NO
if sorted contains "alpha"
- has_alpha = YES
assert "generated sorted has alpha 5", has_alpha, YES

slug = slugify(" Test Item 5 " )
assert "generated slug 5", slug, "test-item-5"
say color("green", "hard 45 complete")
