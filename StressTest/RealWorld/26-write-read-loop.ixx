# write() then immediately read() in a loop 20 times

path = "StressTest/tmp/rw-26-bounce.txt"
matches = 0
total_chars = 0
counter = 1

loop counter at most 20
- content = "Iteration-" + counter + "-data-" + (counter * counter)
- write path, content
- readback = read(path)
- if readback is content
-- matches = matches + 1
- total_chars = total_chars + count(readback)
- counter = counter + 1

say "Iterations: 20"
say "Matches: " + matches + "/20"
say "Total chars: " + total_chars

if matches is 20
- say "PASS: all write/read cycles matched"
