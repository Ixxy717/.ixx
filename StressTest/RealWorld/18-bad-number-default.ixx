# Bad number conversion caught, substituted with default

function safe_number raw, default_val
- result = default_val
- try
-- result = number(raw)
- catch
-- say "  Could not convert '" + raw + "', using default: " + default_val
- return result

inputs = "42", "3.14", "abc", "100", "99.9", "not a number", "7", "  ", "0"

say "Processing inputs:"
total = 0
valid = 0

loop each inp in inputs
- val = safe_number(inp, 0)
- total = total + val
- if val is not 0
-- valid = valid + 1

say "Processed: " + count(inputs) + " inputs"
say "Valid (non-zero): " + valid
say "Sum: " + total

# Also test safe_number with a non-zero default
fallback = safe_number("oops", -1)
say "Fallback value: " + fallback
