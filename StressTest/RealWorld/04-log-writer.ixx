# Log file writer — append timestamped entries, read back and analyze

log_path = "StressTest/tmp/rw-04-log.txt"

write log_path, "[INFO] Application started\n"
append log_path, "[INFO] Loading configuration\n"
append log_path, "[WARN] Config file missing, using defaults\n"
append log_path, "[INFO] Database connection established\n"
append log_path, "[ERROR] Failed to load module: auth\n"
append log_path, "[INFO] Fallback authentication enabled\n"
append log_path, "[INFO] Service ready on port 8080\n"
append log_path, "[WARN] High memory usage detected\n"
append log_path, "[INFO] Shutdown initiated\n"

lines = readlines(log_path)
say "Log entries: " + count(lines)

errors = 0
warnings = 0
infos = 0

loop each line in lines
- if line contains "[ERROR]"
-- errors = errors + 1
- if line contains "[WARN]"
-- warnings = warnings + 1
- if line contains "[INFO]"
-- infos = infos + 1

say "INFO: " + infos + "  WARN: " + warnings + "  ERROR: " + errors
say "First: " + first(lines)
say "Last:  " + last(lines)
