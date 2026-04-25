# loop-each.ixx
# Demonstrates the loop each construct for iterating over lists.

# Basic iteration over a list of names
names = "Ixxy", "Lune", "Zach"

loop each name in names
- say "Hello, {name}!"

say "---"

# Sum a list of numbers
numbers = 1, 2, 3, 4, 5
total = 0

loop each n in numbers
- total = total + n

say "Total: {total}"

say "---"

# Build a sentence from words
words = "IXX", "is", "a", "readable", "language"
sentence = ""

loop each word in words
- if sentence is ""
-- sentence = word
- else
-- sentence = sentence + " " + word

say sentence

say "---"

# Nested loop each: multiplication table rows
rows = 1, 2, 3
cols = 1, 2, 3

loop each r in rows
- row_text = ""
- loop each c in cols
-- product = r * c
-- row_text = row_text + product + "  "
- say row_text

say "---"

# loop each inside a function
function max_item lst
- best = nothing
- loop each item in lst
-- if best is nothing
--- best = item
-- else
--- if item more than best
---- best = item
- return best

scores = 42, 91, 17, 88, 63
say "Top score: " + max_item(scores)

say "---"

# try/catch inside loop each
raw_values = "10", "abc", "30", "xyz"
parsed_sum = 0
bad_count = 0

loop each raw in raw_values
- try
-- parsed_sum = parsed_sum + number(raw)
- catch
-- bad_count = bad_count + 1

say "Parsed sum: {parsed_sum}"
say "Bad values: {bad_count}"
