use "Modules/asserts.ixx"
use "Modules/Mega/string-tools.ixx"

say color("cyan", "hard 43 generated text 3")
base = "zulu,echo,bravo,alpha,item3"
sorted = csv_sort(base)
assert "generated csv sort type 3", type(sorted), "text"

has_alpha = NO
if sorted contains "alpha"
- has_alpha = YES
assert "generated sorted has alpha 3", has_alpha, YES

slug = slugify(" Test Item 3 " )
assert "generated slug 3", slug, "test-item-3"
say color("green", "hard 43 complete")
