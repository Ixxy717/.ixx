function system_snapshot
- ram = do("ram used")
- cpu = do("cpu info")
- disk = do("disk space")
- ip = do("ip local")
- return "CPU=" + cpu + " | RAM=" + ram + " | DISK=" + disk + " | IP=" + ip

function network_snapshot
- ip = do("ip local")
- wifi = do("wifi ip")
- network = do("network")
- return "IP=" + ip + " | WIFI=" + wifi + " | NETWORK=" + network

function short_health used_score
- if used_score at least 90
-- return "critical"
- if used_score at least 75
-- return "watch"
- return "ok"
