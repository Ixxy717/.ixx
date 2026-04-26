# stdlib.ixx - IXX built-in functions demo
# Run with: ixx examples\stdlib.ixx

say color("bold", "IXX Built-in Functions")
say "-------------------------------------------"
say ""

# -------------------------------------------
# Text
# -------------------------------------------

say color("cyan", "Text")
say ""

name = "  Ixxy  "
clean = trim(name)
say "Trimmed:   {clean}"

shout = upper(clean)
say "Shouted:   {shout}"

whisper = lower(shout)
say "Whispered: {whisper}"

sentence = "The quick brown fox"
fixed = replace(sentence, "fox", "dog")
say "Replaced:  {fixed}"

csv = "apple,banana,grape"
fruits = split(csv, ",")
say "Split CSV: {fruits}"

joined = join(fruits, " | ")
say "Joined:    {joined}"

say ""

# -------------------------------------------
# Numbers
# -------------------------------------------

say color("cyan", "Numbers")
say ""

price = 14.7583
rounded = round(price, 2)
say "Price:     {price}"
say "Rounded:   {rounded}"

temp = -12
positive = abs(temp)
say "Temp:      {temp}"
say "Absolute:  {positive}"

low = min(18, 5)
high = max(18, 5)
say "Min of 18, 5:  {low}"
say "Max of 18, 5:  {high}"

scores = 88, 72, 95, 61, 84
best = max(scores)
worst = min(scores)
say "Best score:    {best}"
say "Worst score:   {worst}"

say ""

# -------------------------------------------
# Lists
# -------------------------------------------

say color("cyan", "Lists")
say ""

items = "banana", "apple", "grape", "cherry"
say "Original:  {items}"

sorted_items = sort(items)
say "Sorted:    {sorted_items}"

flipped = reverse(sorted_items)
say "Reversed:  {flipped}"

top = first(sorted_items)
bottom = last(sorted_items)
say "First:     {top}"
say "Last:      {bottom}"

say ""

# -------------------------------------------
# Color output
# -------------------------------------------

say color("cyan", "Colors")
say ""

say color("green",  "Everything looks good")
say color("yellow", "Worth double checking")
say color("red",    "Something went wrong")
say color("bold",   "Important message")
say color("dim",    "Background note")

say ""
say color("bold", "Done.")
