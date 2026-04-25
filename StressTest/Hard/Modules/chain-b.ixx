use "chain-a.ixx"

function chain_b_value
- return chain_a_value() + 10

function chain_b_mix x
- return chain_a_plus(x) + chain_a_value()
