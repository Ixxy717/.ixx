# ----------------------------------------
# IXX try-it script
# Run with:  ixx examples/try-it.ixx
# ----------------------------------------

say "Welcome to IXX"
say "---------------"

# --- Variables ---

name = "World"
say "Hello, {name}!"

score = 42
say "Your score is {score}"

# --- Conditions ---

say ""
say "Checking score..."

if score more than 50
- say "High score!"
else
- say "Not bad, keep going"

# --- Comparisons ---

age = 20

if age less than 18
- say "Too young"

if age is 20
- say "Exactly 20"

if age at least 18
- say "Old enough"

# --- Booleans ---

say ""
ready = YES
done = NO

if ready is YES
- say "Ready to go"

if done is NO
- say "Not done yet"

# --- Loops ---

say ""
say "Counting up:"

count = 1

loop count less than 4
- say "  count is {count}"
- count = count + 1

# --- Lists ---

say ""
say "Checking list membership:"

langs = "python,rust,ixx,go"

if langs contains "ixx"
- say "  ixx is in the list"

if langs contains "java"
- say "  java is in the list"
else
- say "  java is not in the list"

# --- Nested blocks ---

say ""
say "Nested check:"

x = 10

if x more than 5
- say "  x is more than 5"
- if x less than 20
-- say "  x is also less than 20"

# --- Done ---

say ""
say "That is IXX."
