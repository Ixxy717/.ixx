# Mutual recursion — is_even and is_odd calling each other deeply

function is_even n
- if n is 0
-- return YES
- return is_odd(n - 1)

function is_odd n
- if n is 0
-- return NO
- return is_even(n - 1)

say "is_even(0) = " + text(is_even(0))
say "is_even(1) = " + text(is_even(1))
say "is_even(40) = " + text(is_even(40))
say "is_odd(41) = " + text(is_odd(41))
say "is_odd(0) = " + text(is_odd(0))
say "is_odd(1) = " + text(is_odd(1))

# Verify a batch
evens = 0, 2, 4, 6, 8, 10, 20, 30, 40
all_even = YES
loop each n in evens
- if is_even(n) is NO
-- all_even = NO

odds = 1, 3, 5, 7, 9, 11, 21, 31, 41
all_odd = YES
loop each n in odds
- if is_odd(n) is NO
-- all_odd = NO

say "All even checks passed: " + text(all_even)
say "All odd checks passed: " + text(all_odd)
