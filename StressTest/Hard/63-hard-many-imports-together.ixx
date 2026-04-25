use "Modules/asserts.ixx"
use "Modules/Mega/records.ixx"
use std "time"
use std "date"

say color("cyan", "hard 63 many imports together")

# records.ixx already imports string-tools.ixx and numbers.ixx transitively.
# Do not import those directly here, because IXX correctly treats duplicate exported
# function names as an error.
assert "slug via transitive import", slugify("A B C"), "a-b-c"
assert "record", make_record("A B", 101), "a-b:100"
assert "greeting", time_greeting(17), "Good afternoon"
assert "month", is_valid_month(11), YES
assert "status", record_status(91), "excellent"

say color("green", "hard 63 complete")
