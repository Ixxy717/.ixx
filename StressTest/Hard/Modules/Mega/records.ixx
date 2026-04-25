use "string-tools.ixx"
use "numbers.ixx"

function make_record name, score
- clean = slugify(name)
- safe = between(score, 0, 100)
- return clean + ":" + safe

function record_status score
- if score at least 90
-- return "excellent"
- if score at least 70
-- return "good"
- if score at least 50
-- return "ok"
- return "low"

function make_report_line name, score
- return make_record(name, score) + ":" + record_status(score)
