# Name formatter — trim, upper, lower on messy input

names = "  alice  ", "BOB SMITH  ", "carol JONES", "  DAVID brown  ", "Eve Anderson", "  frank MILLER  "

say "=== NAME FORMATTING ==="
clean_count = 0
loop each name in names
- trimmed = trim(name)
- lowered = lower(trimmed)
- say "'" + trimmed + "' -> lower: '" + lowered + "'"
- clean_count = clean_count + 1

say "Processed: " + clean_count + " names"
say "---"

# Sort by trimmed name
trimmed_names = "alice", "BOB SMITH", "carol JONES", "DAVID brown", "Eve Anderson", "frank MILLER"
sorted = sort(trimmed_names)
say "Sorted first: " + first(sorted)
say "Sorted last:  " + last(sorted)

say "---"
say "Uppercase versions:"
clean = "Alice", "Bob", "Carol", "David", "Eve", "Frank"
loop each n in clean
- say upper(n) + " has " + count(n) + " chars"
