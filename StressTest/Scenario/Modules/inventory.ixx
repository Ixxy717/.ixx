use "business.ixx"

function asset_id prefix, n
- return prefix + "-" + n

function location_code zone, rack, shelf
- return zone + "-" + rack + "-" + shelf

function intake_status grade, wiped
- if wiped is NO
-- return "hold-wipe"
- return disposition(grade)

function gaylord_value pounds, rate
- return round(pounds * rate, 2)

function needs_review value, threshold
- if value at least threshold
-- return YES
- return NO

function container_label id, contents, pounds
- return id + " | " + contents + " | " + pounds + " lb"
