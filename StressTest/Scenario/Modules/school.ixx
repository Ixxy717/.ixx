function weighted_score exams, homework, projects
- return round((exams * 0.5) + (homework * 0.25) + (projects * 0.25), 1)

function letter_grade score
- if score at least 90
-- return "A"
- if score at least 80
-- return "B"
- if score at least 70
-- return "C"
- if score at least 60
-- return "D"
- return "F"

function pass_status score
- if score at least 60
-- return "passing"
- return "not passing"
