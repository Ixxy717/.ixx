# files.ixx
# Demonstrates IXX v0.6 file I/O built-ins and try/catch error handling.
#
# NOTE: This script creates two files in the current directory:
#   ixx-demo.txt  -- used for write/read/append demonstrations
#   ixx-log.txt   -- used for the try/catch log example
# Both are listed in .gitignore and can be deleted freely.

say "IXX v0.6 -- File I/O and Error Handling"
say "-------------------------------------------"
say ""

# -- Write and read ------------------------------------------------------------

say "Writing and reading"
say ""

write "ixx-demo.txt", "Hello from IXX!"
content = read("ixx-demo.txt")
say "  Wrote and read back: {content}"

append "ixx-demo.txt", " More."
content = read("ixx-demo.txt")
say "  After append:        {content}"

# -- readlines -----------------------------------------------------------------

lines = readlines("ixx-demo.txt")
n = count(lines)
say "  Lines in file: {n}"

# -- Checking existence --------------------------------------------------------

say ""
say "Checking existence"
say ""

if exists("ixx-demo.txt")
- say "  ixx-demo.txt    exists: YES"

if exists("no-such-file.txt") is NO
- say "  no-such-file.txt exists: NO"

# -- Error handling ------------------------------------------------------------

say ""
say "Error handling"
say ""

# Catch a missing file gracefully
try
- content = read("missing-file.txt")
catch
- say "  Caught: {error}"

# Pre-declare a variable before try to use its value outside the block
log = nothing
try
- write "ixx-log.txt", "session started"
- log = read("ixx-log.txt")
catch
- say "  Log failed: {error}"

if log is not nothing
- say "  Log: {log}"

# try without catch swallows the error silently
try
- x = read("also-missing.txt")
say "  Continues after silent try"

# nothing is a valid value -- use it as a default before a try block
status = nothing
status_type = type(status)
say "  Type of nothing:   {status_type}"

# -- Done ----------------------------------------------------------------------

say ""
say "Done."
say "(ixx-demo.txt and ixx-log.txt were created in the current directory.)"
