use "pipeline-b.ixx"

function pipeline_c_summary
- return pipeline_b() + "|score=" + pipeline_b_score()

function pipeline_c_file path
- summary = pipeline_c_summary()
- write path, summary
- return read(path)
