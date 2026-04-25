use "Modules/asserts.ixx"
use "Modules/chain-c.ixx"

say color("cyan", "hard 06 import deep chain")
assert "deep chain answer", chain_c_answer(), 42
assert "deep chain mix", chain_c_mix(), 42
assert "transitive hard factorial", hard_factorial(6), 720
say color("green", "hard 06 complete")
