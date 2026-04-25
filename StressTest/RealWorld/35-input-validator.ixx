# Input validation — type, range, and format checks

function validate_age raw
- valid = NO
- try
-- age = number(raw)
-- if age at least 0 and age at most 150
--- valid = YES
-- else
--- say "  Age out of range: " + age
- catch
-- say "  Invalid age format: '" + raw + "'"
- return valid

function validate_email raw
- if raw contains "@"
-- parts = split(raw, "@")
-- if count(parts) is 2
--- domain = last(parts)
--- if domain contains "."
---- return YES
- return NO

say "=== AGE VALIDATION ==="
ages = "25", "abc", "-5", "200", "30", "17", "0", "150"
valid_ages = 0
loop each age in ages
- if validate_age(age)
-- valid_ages = valid_ages + 1
-- say "  Valid: " + age

say "Valid ages: " + valid_ages + "/" + count(ages)

say "=== EMAIL VALIDATION ==="
emails = "user@example.com", "notanemail", "test@domain.org", "bad@", "@nodomain.com", "a@b.c"
valid_emails = 0
loop each email in emails
- if validate_email(email)
-- valid_emails = valid_emails + 1
-- say "  Valid: " + email
- else
-- say "  Invalid: " + email

say "Valid emails: " + valid_emails + "/" + count(emails)
