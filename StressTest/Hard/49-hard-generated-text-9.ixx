use "Modules/asserts.ixx"
use "Modules/Mega/string-tools.ixx"

say color("cyan", "hard 49 generated text 9")
base = "zulu,echo,bravo,alpha,item9"
sorted = csv_sort(base)
assert "generated csv sort type 9", type(sorted), "text"

has_alpha = NO
if sorted contains "alpha"
- has_alpha = YES
assert "generated sorted has alpha 9", has_alpha, YES

slug = slugify(" Test Item 9 " )
assert "generated slug 9", slug, "test-item-9"
say color("green", "hard 49 complete")
