# Password strength checker

function check_password pwd
- score = 0
- length_ok = NO
- has_digit = NO
- has_upper = NO
- has_special = NO

- if count(pwd) at least 8
-- length_ok = YES
-- score = score + 1

- digits = "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
- loop each d in digits
-- if pwd contains d
--- has_digit = YES

- if has_digit
-- score = score + 1

- if pwd is not lower(pwd)
-- has_upper = YES
-- score = score + 1

- specials = "!", "@", "#", "$", "%", "^", "&", "*"
- loop each sp in specials
-- if pwd contains sp
--- has_special = YES

- if has_special
-- score = score + 1

- strength = "Weak"
- if score at least 2
-- strength = "Fair"
- if score at least 3
-- strength = "Strong"
- if score is 4
-- strength = "Very Strong"

- say "Password: " + pwd
- say "  Length OK: " + text(length_ok) + "  Digit: " + text(has_digit) + "  Upper: " + text(has_upper) + "  Special: " + text(has_special)
- say "  Score: " + score + "/4  Strength: " + strength
- say "---"

check_password("abc")
check_password("password123")
check_password("MyPass1!")
check_password("X9!kQpZ2@mN")
