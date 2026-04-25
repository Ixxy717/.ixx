# Countdown string builder via recursion

function countdown n
- if n is 0
-- return "blastoff"
- return text(n) + "..." + countdown(n - 1)

result = countdown(20)
say result
say "Length: " + count(result)

if result contains "blastoff"
- say "PASS: contains blastoff"
if result contains "20..."
- say "PASS: starts with 20"

# Count how many "..." separators
parts = split(result, "...")
say "Parts: " + count(parts)
