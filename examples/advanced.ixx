# IXX advanced example — language features

# --- variables and string interpolation ---
name = "Ixxy"
say "Hello, {name}"

# --- conditions ---
score = 92

if score at least 90
- say "Grade: A"
else
- say "Grade: not A"

# --- is / is not ---
status = "active"

if status is "active"
- say "Account is active"

if status is not "banned"
- say "Account is allowed"

# --- loop ---
count = 3

loop count more than 0
- say "Countdown: {count}"
- count = count - 1

say "Blast off!"

# --- nested blocks ---
lives = 2
bomb = YES

if lives at most 2
- say "Low on lives"
- if bomb is YES
-- say "And the bomb went off!"
-- lives = lives - 1

say "Lives remaining: {lives}"

# --- lists ---
fruits = "apple", "banana", "grape"

if fruits contains "grape"
- say "Grapes are in the list"

# --- math ---
bonus = score + 8
say "Score with bonus: {bonus}"

half = 100 / 2
say "Half of 100 is {half}"

negative = -10
say "Negative number: {negative}"

# --- logic ---
ready = YES
logged_in = YES

if ready and logged_in
- say "Good to go"

if not bomb
- say "No bomb active"
else
- say "Bomb is active"
