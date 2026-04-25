# IXX standard library: date utilities
# Pure IXX functions — no built-ins required.

function is_leap_year year
- if year / 400 is round(year / 400)
-- return YES
- if year / 100 is round(year / 100)
-- return NO
- if year / 4 is round(year / 4)
-- return YES
- return NO

function days_in_february year
- if is_leap_year(year)
-- return 29
- return 28

function is_valid_month month
- if month less than 1
-- return NO
- if month more than 12
-- return NO
- return YES
