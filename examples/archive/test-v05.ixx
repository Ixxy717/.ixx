# ARCHIVED — IXX v0.5 syntax example
#
# This file uses the old v0.5 calling style where built-in arguments did not
# require quotes around string values, e.g.:
#   say trim(  clean me  )
#   say color(green, pass color works)
#
# That syntax was removed in v0.6. This file no longer parses.
# It is kept here as a historical reference for the v0.5 language design.
# Do NOT run this file — it will produce a syntax error.
#
# For working examples of these built-ins, see:
#   examples/functions.ixx
#   examples/lists.ixx
#   examples/colors.ixx

say upper(hello)
say lower(WORLD)
say trim(  clean me  )
say replace(the cat sat, cat, dog)

words = split(one,two,three, ,)
say count(words)
say first(words)
say last(words)
say join(words,   )

nums = 9, 3, 7, 1
say min(nums)
say max(nums)
say sort(nums)
say reverse(nums)

say round(3.14159, 2)
say abs(-99)

say color(green, pass color works)
say color(red,    this is red)
say color(yellow, this is yellow)
say color(bold,   this is bold)
