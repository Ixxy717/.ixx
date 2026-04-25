use "Modules/asserts.ixx"
use std "time"
use std "date"

say color("cyan", "hard 08 stdlib composition")
assert "morning greeting", time_greeting(6), "Good morning"
assert "afternoon greeting", time_greeting(12), "Good afternoon"
assert "evening greeting", time_greeting(21), "Good evening"

# time.ixx intentionally rounds these helpers to 1 decimal place.
assert "seconds to minutes rounded", seconds_to_minutes(75), 1.2
assert "minutes to hours rounded", minutes_to_hours(90), 1.5

assert "leap year 2024", is_leap_year(2024), YES
assert "leap year 1900 false", is_leap_year(1900), NO
assert "feb 2024", days_in_february(2024), 29
assert "valid month 0 false", is_valid_month(0), NO
say color("green", "hard 08 complete")
