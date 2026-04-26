say color("cyan", "82 letter-v checker quality")

# V1: string literals should parse and work normally
greeting = "hello"
say greeting

# V3: blank lines should not affect execution

name = "Ixxy"

say "Hello, {name}"

# V1: interpolation in variables works
msg = "Result: {greeting}"
say msg
