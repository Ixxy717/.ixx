# try/catch inside loop each — one item fails, rest continue

values = "10", "20", "abc", "40", "xyz", "60", "bad", "80"

total = 0
success_count = 0
fail_count = 0

loop each v in values
- try
-- n = number(v)
-- total = total + n
-- success_count = success_count + 1
- catch
-- fail_count = fail_count + 1
-- say "Skipping: '" + v + "'"

say "Total: " + total
say "Succeeded: " + success_count
say "Failed: " + fail_count
say "Expected total: 210"

if total is 210
- say "PASS: sum correct"

# Same pattern but with file reads
paths = "StressTest/tmp/rw-20-real.txt", "StressTest/tmp/rw-20-missing.txt", "StressTest/tmp/rw-20-real2.txt"
write "StressTest/tmp/rw-20-real.txt", "hello"
write "StressTest/tmp/rw-20-real2.txt", "world"

reads_ok = 0
reads_fail = 0

loop each p in paths
- try
-- content = read(p)
-- reads_ok = reads_ok + 1
-- say "Read OK: " + p
- catch
-- reads_fail = reads_fail + 1
-- say "Read failed: " + p

say "File reads: " + reads_ok + " ok, " + reads_fail + " failed"
