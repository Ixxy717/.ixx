use "Modules/asserts.ixx"
use "Modules/Mega/string-tools.ixx"

say color("cyan", "hard 48 generated text 8")
base = "zulu,echo,bravo,alpha,item8"
sorted = csv_sort(base)
assert "generated csv sort type 8", type(sorted), "text"

has_alpha = NO
if sorted contains "alpha"
- has_alpha = YES
assert "generated sorted has alpha 8", has_alpha, YES

slug = slugify(" Test Item 8 " )
assert "generated slug 8", slug, "test-item-8"
say color("green", "hard 48 complete")
