use "Modules/asserts.ixx"
use "Modules/Mega/string-tools.ixx"

say color("cyan", "hard 47 generated text 7")
base = "zulu,echo,bravo,alpha,item7"
sorted = csv_sort(base)
assert "generated csv sort type 7", type(sorted), "text"

has_alpha = NO
if sorted contains "alpha"
- has_alpha = YES
assert "generated sorted has alpha 7", has_alpha, YES

slug = slugify(" Test Item 7 " )
assert "generated slug 7", slug, "test-item-7"
say color("green", "hard 47 complete")
