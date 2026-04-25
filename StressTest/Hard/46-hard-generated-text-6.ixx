use "Modules/asserts.ixx"
use "Modules/Mega/string-tools.ixx"

say color("cyan", "hard 46 generated text 6")
base = "zulu,echo,bravo,alpha,item6"
sorted = csv_sort(base)
assert "generated csv sort type 6", type(sorted), "text"

has_alpha = NO
if sorted contains "alpha"
- has_alpha = YES
assert "generated sorted has alpha 6", has_alpha, YES

slug = slugify(" Test Item 6 " )
assert "generated slug 6", slug, "test-item-6"
say color("green", "hard 46 complete")
