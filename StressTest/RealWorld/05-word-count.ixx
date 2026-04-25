# Word count approximator

function word_stats text_input
- words = split(text_input)
- wc = count(words)
- say "Text: '" + text_input + "'"
- say "  Words: " + wc + "  Chars: " + count(text_input)
- say "  First: " + first(words) + "  Last: " + last(words)
- return wc

t1 = "The quick brown fox jumps over the lazy dog"
t2 = "IXX is a readable language designed for real humans"
t3 = "  extra   spaces   everywhere   "
t4 = "one"

wc1 = word_stats(t1)
wc2 = word_stats(t2)
wc3 = word_stats(trim(t3))
wc4 = word_stats(t4)

say "---"
say "Total words across all texts: " + (wc1 + wc2 + wc3 + wc4)

sorted_words = sort(split(t1))
say "Alphabetically first word: " + first(sorted_words)
say "Alphabetically last word:  " + last(sorted_words)
