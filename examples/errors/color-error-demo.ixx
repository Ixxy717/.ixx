# INTENTIONALLY BROKEN — do not expect this to run successfully.
#
# This example demonstrates what an IXX runtime error looks like in the
# terminal, specifically the red color used for error output.
#
# Run this file with IXX_COLOR=1 to see the error message in red:
#
#   --- PowerShell ---
#   $env:IXX_COLOR = "1"; ixx examples\errors\color-error-demo.ixx; Remove-Item Env:\IXX_COLOR
#
#   --- CMD ---
#   set IXX_COLOR=1 && ixx examples\errors\color-error-demo.ixx && set IXX_COLOR=
#
# Expected error (runtime):
#   Cannot convert 'not-a-number' to a number.
#
# See examples/colors.ixx for the full color-support demo.

say "Triggering an intentional runtime error..."
say "The error message below should appear in red (if colors are enabled)."
say ""

x = number("not-a-number")
