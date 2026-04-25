# Error handling: read missing file, write fallback, read fallback

main_path     = "StressTest/tmp/rw-16-main.txt"
fallback_path = "StressTest/tmp/rw-16-fallback.txt"

content = "no content"
source = "unknown"

try
- content = read(main_path)
- source = "main"
catch
- say "Main file missing, writing fallback..."
- write fallback_path, "DEFAULT CONFIG\nmode=safe\ntimeout=30\nretry=3"
- content = read(fallback_path)
- source = "fallback"

say "Source: " + source
say "Content lines: " + count(split(content, "\n"))
say "First line: " + first(split(content, "\n"))

# Clean up for idempotency: delete known paths by overwriting
write main_path, "real config"
content2 = "no content"
try
- content2 = read(main_path)
- say "Second run (main exists): " + content2
catch
- say "Second run failed unexpectedly"
