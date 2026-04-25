say color("cyan", "46 import stdlib basic")

function assert name, got, expected
- if got is expected
-- say color("green", "PASS " + name)
-- return
- say color("red", "FAIL " + name)
- say "Expected: {expected}"
- say "Got: {got}"
- crash = number("ASSERT_FAIL")

use std "time"
use std "date"

assert "time_greeting morning", time_greeting(9), "Good morning"
assert "time_greeting afternoon", time_greeting(15), "Good afternoon"
assert "time_greeting evening", time_greeting(20), "Good evening"

assert "is_leap_year 2024", is_leap_year(2024), YES
assert "is_leap_year 2023", is_leap_year(2023), NO
assert "is_leap_year 2000", is_leap_year(2000), YES
assert "is_leap_year 1900", is_leap_year(1900), NO

assert "days_in_february leap", days_in_february(2024), 29
assert "days_in_february non-leap", days_in_february(2023), 28

assert "is_valid_month 1", is_valid_month(1), YES
assert "is_valid_month 12", is_valid_month(12), YES
assert "is_valid_month 0", is_valid_month(0), NO
assert "is_valid_month 13", is_valid_month(13), NO
