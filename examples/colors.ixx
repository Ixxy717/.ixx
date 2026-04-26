# colors.ixx  -  Visual check for IXX terminal color support
#
# --- PowerShell ---
#
# Run normally (auto-detect):
#   ixx examples\colors.ixx
#
# Force colors OFF:
#   $env:IXX_COLOR = "0"; ixx examples\colors.ixx; Remove-Item Env:\IXX_COLOR
#
# Force colors ON:
#   $env:IXX_COLOR = "1"; ixx examples\colors.ixx; Remove-Item Env:\IXX_COLOR
#
# Standard no-color flag (https://no-color.org):
#   $env:NO_COLOR = "1"; ixx examples\colors.ixx; Remove-Item Env:\NO_COLOR
#
# --- CMD ---
#
# Force colors OFF:
#   set IXX_COLOR=0 && ixx examples\colors.ixx && set IXX_COLOR=
#
# Force colors ON:
#   set IXX_COLOR=1 && ixx examples\colors.ixx && set IXX_COLOR=
#
# Standard no-color flag:
#   set NO_COLOR=1 && ixx examples\colors.ixx && set NO_COLOR=

say "IXX Color Test"
say "--------------------"
say ""
say "Normal say output has no color - it is always plain text."
say "Colors are applied by the IXX runtime to:"
say "  - error messages  (red)"
say "  - ixx shell hints (cyan, dim, yellow)"
say ""
say "Color env vars:"
say "  IXX_COLOR=1   force colors on"
say "  IXX_COLOR=0   force colors off"
say "  NO_COLOR=<any>  standard disable flag"
say ""

say "--- type check ---"
say type(42)
say type("hello")
say type(YES)
say type(NO)

items = 1, 2, 3
say type(items)

function nothing_fn
- return

say type(nothing_fn())

say ""
say "--- built-ins ---"
say count("hello")
say count(items)
say text(100)
say number("99")

say ""
say "--- function return ---"

function label value
- return text(value) + " [" + type(value) + "]"

say label(42)
say label("ixx")
say label(YES)
say label(items)

say ""
say "--------------------"
say "The intentional error demo has been moved to:"
say "  examples/errors/color-error-demo.ixx"
say "Run that file to see the red error output."
say "--------------------"
