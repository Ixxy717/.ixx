use "Modules/asserts.ixx"
use "Modules/Mega/string-tools.ixx"

say color("cyan", "hard 50 generated text 10")
base = "zulu,echo,bravo,alpha,item10"
sorted = csv_sort(base)
assert "generated csv sort type 10", type(sorted), "text"

has_alpha = NO
if sorted contains "alpha"
- has_alpha = YES
assert "generated sorted has alpha 10", has_alpha, YES

slug = slugify(" Test Item 10 " )
assert "generated slug 10", slug, "test-item-10"
say color("green", "hard 50 complete")
