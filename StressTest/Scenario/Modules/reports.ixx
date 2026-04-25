function report_start title, path
- write path, "== " + title + " =="
- append path, "\n"
- return path

function report_add path, label, value
- append path, label
- append path, ": "
- append path, value
- append path, "\n"
- return read(path)

function report_add_blank path
- append path, "\n"
- return read(path)

function report_finish path
- append path, "-- end --"
- append path, "\n"
- return read(path)

function contains_line content, needle
- if content contains needle
-- return YES
- return NO

function save_status path, name, status
- write path, name
- append path, "="
- append path, status
- return read(path)
