# Shadow global variables inside a function — globals unchanged after

global_name = "GlobalValue"
global_count = 100
global_flag = YES
global_list = 1, 2, 3

function shadow_test
- global_name = "LocalValue"
- global_count = 999
- global_flag = NO
- global_list = 10, 20, 30
- say "Inside: name=" + global_name + " count=" + global_count + " flag=" + text(global_flag)
- return global_count

result = shadow_test()

say "After call:"
say "  name  = " + global_name
say "  count = " + global_count
say "  flag  = " + text(global_flag)
say "  list  = " + join(global_list, ",")
say "  returned = " + result

if global_name is "GlobalValue"
- say "PASS: global_name unchanged"
if global_count is 100
- say "PASS: global_count unchanged"
if global_flag is YES
- say "PASS: global_flag unchanged"
if first(global_list) is 1
- say "PASS: global_list unchanged"
