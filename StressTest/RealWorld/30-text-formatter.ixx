# Text formatter pipeline

function normalize raw
- return trim(lower(raw))

function tag_it txt, tag
- return "[" + tag + "] " + txt

function censor txt, bad_word
- return replace(txt, bad_word, "***")

function word_wrap txt, max_len
- if count(txt) at most max_len
-- return txt
- return txt + " [truncated]"

sample = "  Hello World IXX Language  "
say "Original: '" + sample + "'"
say "Normalized: '" + normalize(sample) + "'"
say "Upper: '" + upper(trim(sample)) + "'"

messages = "This is fine", "This badword is flagged", "Another goodword message here"
loop each msg in messages
- cleaned = censor(msg, "badword")
- tagged = tag_it(cleaned, "LOG")
- wrapped = word_wrap(tagged, 40)
- say wrapped

say "---"
long_text = "  extra   whitespace   all   over   the   place   "
trimmed = trim(long_text)
say "Trimmed: '" + trimmed + "'"
say "Words: " + count(split(trimmed))
say "Upper word count: " + count(split(upper(trimmed)))
