say color("cyan", "81 letter-t T1 builtin shadow warning")

# T1: assigning to builtin name should still work at runtime
count = 5
say count

# T1: builtin still works after NOT shadowing it
items = "a", "b", "c"
say count(items)

# T1: normal assignment is fine
score = 42
say score
