# Building strings character by character via split/join

# Build a word from individual letters
letters = "H", "e", "l", "l", "o", ",", " ", "W", "o", "r", "l", "d"
result = ""
loop each ch in letters
- result = result + ch
say "Built: " + result
say "Length: " + count(result)

# Build a number string from digits
digits = "3", "1", "4", "1", "5", "9", "2", "6"
num_str = ""
loop each d in digits
- num_str = num_str + d
say "Digit string: " + num_str
say "As number: " + number(num_str)

# Build a sentence from words
words = "IXX", "is", "a", "readable", "scripting", "language"
built = ""
first_w = YES
loop each w in words
- if first_w
-- built = w
-- first_w = NO
- else
-- built = built + " " + w
say "Sentence: " + built
say "Word count: " + count(split(built))

# Verify join does same thing
joined_ver = join(words, " ")
if built is joined_ver
- say "PASS: manual build matches join()"
