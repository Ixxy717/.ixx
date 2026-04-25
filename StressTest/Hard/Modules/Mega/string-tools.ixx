function slugify textvalue
- cleaned = lower(trim(textvalue))
- cleaned = replace(cleaned, " ", "-")
- cleaned = replace(cleaned, "_", "-")
- return cleaned

function surround value, left, right
- return left + value + right

function csv_sort line
- parts = split(line, ",")
- sorted = sort(parts)
- return join(sorted, ",")

function titleish value
- cleaned = trim(value)
- return upper(first(split(cleaned))) + " " + lower(last(split(cleaned)))
