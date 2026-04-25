use "Modules/asserts.ixx"
use "Modules/Mega/string-tools.ixx"

say color("cyan", "hard 42 generated text 2")
base = "zulu,echo,bravo,alpha,item2"
sorted = csv_sort(base)
assert "generated csv sort type 2", type(sorted), "text"

has_alpha = NO
if sorted contains "alpha"
- has_alpha = YES
assert "generated sorted has alpha 2", has_alpha, YES

slug = slugify(" Test Item 2 " )
assert "generated slug 2", slug, "test-item-2"
say color("green", "hard 42 complete")
