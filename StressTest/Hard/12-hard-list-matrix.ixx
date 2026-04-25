use "Modules/asserts.ixx"

say color("cyan", "hard 12 list matrix")
numbers = 9, 4, 7, 1, 3, 8, 2, 6, 5
assert "number count", count(numbers), 9
assert "number min", min(numbers), 1
assert "number max", max(numbers), 9
assert "first unsorted", first(numbers), 9
assert "last unsorted", last(numbers), 5

sorted_nums = sort(numbers)
assert "first sorted", first(sorted_nums), 1
assert "last sorted", last(sorted_nums), 9

words = "zulu", "echo", "bravo", "alpha"
assert "word min", first(sort(words)), "alpha"
assert "word reverse first", first(reverse(sort(words))), "zulu"
assert "word join", join(sort(words), ","), "alpha,bravo,echo,zulu"
say color("green", "hard 12 complete")
