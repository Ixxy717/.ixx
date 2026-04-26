# INTENTIONALLY BROKEN — do not expect this to run successfully.
#
# This example demonstrates the error raised when a function is called
# with the wrong number of arguments.
#
# `add` expects 2 arguments (a, b), but is called with only 1 (5).
#
# Expected error (ixx check / runtime):
#   'add' expects 2 argument(s), got 1. Parameters: a, b

function add a, b
- return a + b

result = add(5)
say result
