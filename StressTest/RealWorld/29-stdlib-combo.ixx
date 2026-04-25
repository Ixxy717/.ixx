# Use std "time" and "date" together with real logic

use std "time"
use std "date"

say "=== TIME MODULE ==="
say time_greeting(6)
say time_greeting(9)
say time_greeting(13)
say time_greeting(19)
say time_greeting(22)

say "minutes_to_hours(60)  = " + minutes_to_hours(60)
say "minutes_to_hours(90)  = " + minutes_to_hours(90)
say "minutes_to_hours(150) = " + minutes_to_hours(150)
say "seconds_to_minutes(120) = " + seconds_to_minutes(120)

say "=== DATE MODULE ==="
say "is_leap_year(2000) = " + text(is_leap_year(2000))
say "is_leap_year(1900) = " + text(is_leap_year(1900))
say "is_leap_year(2024) = " + text(is_leap_year(2024))
say "is_leap_year(2023) = " + text(is_leap_year(2023))

say "days_in_february(2024) = " + days_in_february(2024)
say "days_in_february(2023) = " + days_in_february(2023)

say "is_valid_month(1)  = " + text(is_valid_month(1))
say "is_valid_month(12) = " + text(is_valid_month(12))
say "is_valid_month(13) = " + text(is_valid_month(13))
say "is_valid_month(0)  = " + text(is_valid_month(0))

say "=== COMBINED LOGIC ==="
hrs = minutes_to_hours(750)
say "750 minutes -> " + hrs

feb_days = days_in_february(2024)
say "Feb 2024 has " + feb_days + " days"

morning_greeting = time_greeting(8)
say "Morning greeting: " + morning_greeting

leap_count = 0
years = 2000, 2001, 2004, 2100, 2400, 2024
loop each yr in years
- if is_leap_year(yr)
-- leap_count = leap_count + 1
say "Leap years in test set: " + leap_count