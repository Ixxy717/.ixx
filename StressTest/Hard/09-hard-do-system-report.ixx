use "Modules/asserts.ixx"

say color("cyan", "hard 09 do system report")
ram = do("ram used")
cpu = do("cpu info")
disk = do("disk space")
network = do("network")

asserttext "ram text", ram
asserttext "cpu text", cpu
asserttext "disk text", disk
asserttext "network text", network

path = "StressTest/tmp/hard-system-report.txt"
write path, "SYSTEM"
append path, " | RAM="
append path, ram
append path, " | CPU="
append path, cpu
append path, " | DISK="
append path, disk
append path, " | NETWORK="
append path, network

report = read(path)
large = NO
if count(report) more than 100
- large = YES
assert "system report large", large, YES
say color("green", "hard 09 complete")
