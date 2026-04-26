# INTENTIONALLY BROKEN — do not expect this to run successfully.
#
# This example demonstrates a syntax error: an `if` condition that is
# incomplete (missing the right-hand side of the comparison).
#
# `if age less than` is not valid IXX — a value is required after `less than`.
#
# Expected error (syntax):
#   Syntax error — check the syntax around the marked position.

say "Broken IXX Test"

age = 19

if age less than
- say "This should not run"

say "Done"
