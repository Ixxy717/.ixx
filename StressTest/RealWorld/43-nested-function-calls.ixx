# Function call chain 6 levels deep, then a pipeline

function level6 x
- return x + 1

function level5 x
- return level6(x) + 1

function level4 x
- return level5(x) + 1

function level3 x
- return level4(x) + 1

function level2 x
- return level3(x) + 1

function level1 x
- return level2(x) + 1

result = level1(0)
say "6-level chain from 0: " + result

if result is 6
- say "PASS: each level added 1"

# Pipeline that calls multiple levels
function pipeline_a x
- a = level1(x)
- b = level3(a)
- c = level6(b)
- return c

say "pipeline_a(10) = " + pipeline_a(10)

# Verify with accumulation
total = 0
inputs = 0, 1, 2, 3, 4, 5
loop each n in inputs
- total = total + level1(n)
say "Sum of level1(0..5): " + total
