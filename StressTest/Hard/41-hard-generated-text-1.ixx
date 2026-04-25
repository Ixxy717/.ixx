use "Modules/asserts.ixx"
use "Modules/Mega/string-tools.ixx"

say color("cyan", "hard 41 generated text 1")
base = "zulu,echo,bravo,alpha,item1"
sorted = csv_sort(base)
assert "generated csv sort type 1", type(sorted), "text"

has_alpha = NO
if sorted contains "alpha"
- has_alpha = YES
assert "generated sorted has alpha 1", has_alpha, YES

slug = slugify(" Test Item 1 " )
assert "generated slug 1", slug, "test-item-1"
say color("green", "hard 41 complete")
