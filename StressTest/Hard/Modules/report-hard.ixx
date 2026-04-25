use "math-hard.ixx"

function hard_report name, path
- ram = do("ram used")
- cpu = do("cpu info")
- score = hard_weighted(6, 12)
- write path, "Report for {name}"
- append path, " | score="
- append path, score
- append path, " | ram="
- append path, ram
- append path, " | cpu="
- append path, cpu
- return read(path)

function hard_report_score
- return hard_weighted(6, 12)
