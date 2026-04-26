# INTENTIONALLY BROKEN — do not expect this to run successfully.
#
# This example demonstrates the error raised when `return` is used
# outside of a function. IXX only allows `return` inside a function body.
#
# Expected error (runtime):
#   'return' can only be used inside a function.
#
# Expected error (ixx check):
#   'return' can only be used inside a function.

return "bad"
