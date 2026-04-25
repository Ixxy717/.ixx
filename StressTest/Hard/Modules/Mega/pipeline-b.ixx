use "pipeline-a.ixx"

function pipeline_b
- a = pipeline_a("Alpha User", 92)
- b = pipeline_a("Beta User", 75)
- c = pipeline_a("Gamma User", 48)
- return a + "|" + b + "|" + c

function pipeline_b_score
- return pipeline_a_score(20)
