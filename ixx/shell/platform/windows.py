"""IXX Shell — Windows Platform Adapter

All Windows-specific system query implementations live here.
The command handlers call these functions; they never contain
PowerShell or WMIC syntax themselves.

All public functions return plain Python dicts/lists/strings.
If a query fails, functions return safe empty/fallback values
instead of raising — the caller renders partial info gracefully.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import string
import sys

from .common import run_command


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ps(cmd: str) -> str:
    """Run a PowerShell command and return its stdout."""
    return run_command(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
        timeout=15,
    )


def _parse_json(raw: str) -> list[dict]:
    """Parse JSON that may be a single object or a list. Returns a list."""
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, ValueError):
        pass
    return []


# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------

def get_ip_info() -> list[dict]:
    """Return active IPv4 adapters, excluding loopback.

    Returns:
        [{"adapter": str, "ipv4": str}, ...]
    """
    raw = _ps(
        "Get-NetIPAddress -AddressFamily IPv4 "
        "| Where-Object { $_.IPAddress -notmatch '^127\\.' } "
        "| Select-Object InterfaceAlias, IPAddress "
        "| ConvertTo-Json -Compress"
    )
    items = _parse_json(raw)
    if items:
        return [
            {
                "adapter": str(item.get("InterfaceAlias") or "?"),
                "ipv4": str(item.get("IPAddress") or "-"),
            }
            for item in items
        ]

    # Fallback: use socket
    try:
        hostname = socket.gethostname()
        infos = socket.getaddrinfo(hostname, None, socket.AF_INET)
        seen: set[str] = set()
        results = []
        for entry in infos:
            ip = entry[4][0]
            if ip not in seen and not ip.startswith("127."):
                seen.add(ip)
                results.append({"adapter": hostname, "ipv4": ip})
        return results
    except Exception:
        return []


def get_wifi_ip() -> str | None:
    """Return the IPv4 address of the first connected Wi-Fi adapter, or None."""
    raw = _ps(
        "Get-NetAdapter "
        "| Where-Object { ($_.Name -match 'Wi-Fi|Wireless|WLAN') -and ($_.Status -eq 'Up') } "
        "| ForEach-Object { "
        "  Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue "
        "  | Where-Object { $_.IPAddress -notmatch '^127\\.' } "
        "  | Select-Object -ExpandProperty IPAddress "
        "} "
        "| Select-Object -First 1"
    )
    return raw.strip() or None


def get_ethernet_ip() -> str | None:
    """Return the IPv4 address of the first connected Ethernet adapter, or None."""
    raw = _ps(
        "Get-NetAdapter "
        "| Where-Object { ($_.Name -match 'Ethernet|LAN') -and ($_.Status -eq 'Up') } "
        "| ForEach-Object { "
        "  Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue "
        "  | Where-Object { $_.IPAddress -notmatch '^127\\.' } "
        "  | Select-Object -ExpandProperty IPAddress "
        "} "
        "| Select-Object -First 1"
    )
    return raw.strip() or None


def get_network_info() -> list[dict]:
    """Return all adapters with status, IPv4, and gateway.

    Returns:
        [{"adapter": str, "status": str, "ipv4": str, "gateway": str}, ...]
    """
    raw = _ps(
        "$adapters = Get-NetAdapter; "
        "$result = foreach ($a in $adapters) { "
        "  $ip = (Get-NetIPAddress -InterfaceIndex $a.ifIndex -AddressFamily IPv4 "
        "           -ErrorAction SilentlyContinue "
        "         | Where-Object { $_.IPAddress -notmatch '^127\\.' } "
        "         | Select-Object -First 1 -ExpandProperty IPAddress); "
        "  $gw = (Get-NetRoute -InterfaceIndex $a.ifIndex "
        "           -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue "
        "         | Select-Object -First 1 -ExpandProperty NextHop); "
        "  [PSCustomObject]@{ "
        "    Adapter = $a.Name; "
        "    Status  = if ($a.Status -eq 'Up') { 'connected' } else { 'disconnected' }; "
        "    IPv4    = if ($ip) { $ip } else { '-' }; "
        "    Gateway = if ($gw) { $gw } else { '-' } "
        "  } "
        "}; "
        "$result | ConvertTo-Json -Compress"
    )
    items = _parse_json(raw)
    return [
        {
            "adapter": str(item.get("Adapter") or "?"),
            "status":  str(item.get("Status")  or "-"),
            "ipv4":    str(item.get("IPv4")    or "-"),
            "gateway": str(item.get("Gateway") or "-"),
        }
        for item in items
    ]


# ---------------------------------------------------------------------------
# CPU
# ---------------------------------------------------------------------------

def get_cpu_info() -> dict:
    """Return CPU name, core count, thread count, and usage percentage.

    Returns:
        {"name": str, "cores": str, "threads": str, "usage_pct": str}
    """
    raw = _ps(
        "Get-CimInstance Win32_Processor "
        "| Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, LoadPercentage "
        "| ConvertTo-Json -Compress"
    )
    items = _parse_json(raw)
    info: dict[str, str] = {
        "name": "unavailable",
        "cores": "-",
        "threads": "-",
        "usage_pct": "-",
    }
    if items:
        item = items[0]
        name = (item.get("Name") or "").strip()
        if name:
            info["name"] = name
        cores = item.get("NumberOfCores")
        if cores is not None:
            info["cores"] = str(cores)
        threads = item.get("NumberOfLogicalProcessors")
        if threads is not None:
            info["threads"] = str(threads)
        usage = item.get("LoadPercentage")
        if usage is not None:
            info["usage_pct"] = f"{usage}%"

    # Fallbacks
    if info["threads"] == "-":
        count = os.cpu_count()
        if count:
            info["threads"] = str(count)
    if info["name"] == "unavailable":
        import platform as _p
        name = _p.processor()
        if name:
            info["name"] = name

    return info


def get_cpu_core_count() -> dict:
    """Return CPU name, core count, and thread count (no usage query).

    Returns:
        {"name": str, "cores": str, "threads": str}
    """
    raw = _ps(
        "Get-CimInstance Win32_Processor "
        "| Select-Object Name, NumberOfCores, NumberOfLogicalProcessors "
        "| ConvertTo-Json -Compress"
    )
    items = _parse_json(raw)
    info: dict[str, str] = {"name": "unavailable", "cores": "-", "threads": "-"}
    if items:
        item = items[0]
        name = (item.get("Name") or "").strip()
        if name:
            info["name"] = name
        cores = item.get("NumberOfCores")
        if cores is not None:
            info["cores"] = str(cores)
        threads = item.get("NumberOfLogicalProcessors")
        if threads is not None:
            info["threads"] = str(threads)

    if info["threads"] == "-":
        count = os.cpu_count()
        if count:
            info["threads"] = str(count)

    return info


# ---------------------------------------------------------------------------
# RAM
# ---------------------------------------------------------------------------

def get_ram_info() -> dict:
    """Return total, used, and free RAM in bytes.

    Returns:
        {"total_bytes": int, "used_bytes": int, "free_bytes": int}
    """
    raw = _ps(
        "$os = Get-CimInstance Win32_OperatingSystem; "
        "[PSCustomObject]@{ "
        "  Total = $os.TotalVisibleMemorySize; "
        "  Free  = $os.FreePhysicalMemory "
        "} | ConvertTo-Json -Compress"
    )
    info = {"total_bytes": 0, "used_bytes": 0, "free_bytes": 0}
    items = _parse_json(raw)
    if items:
        item = items[0]
        # Win32_OperatingSystem reports in kilobytes
        total_kb = item.get("Total") or 0
        free_kb  = item.get("Free")  or 0
        total = int(total_kb) * 1024
        free  = int(free_kb)  * 1024
        info["total_bytes"] = total
        info["free_bytes"]  = free
        info["used_bytes"]  = max(0, total - free)
    return info


# ---------------------------------------------------------------------------
# Disk
# ---------------------------------------------------------------------------

def _get_drive_label(letter: str) -> str:
    """Return the volume label for *letter* drive, or '' on failure."""
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(261)
        ctypes.windll.kernel32.GetVolumeInformationW(  # type: ignore[attr-defined]
            f"{letter}:\\", buf, ctypes.sizeof(buf),
            None, None, None, None, 0,
        )
        return buf.value or ""
    except Exception:
        return ""


def get_disk_info() -> list[dict]:
    """Return logical drive info for all present drives.

    Returns:
        [{"drive": str, "label": str, "total_bytes": int, "free_bytes": int,
          "used_bytes": int}, ...]
    """
    drives = []
    for letter in string.ascii_uppercase:
        path = f"{letter}:\\"
        if os.path.exists(path):
            try:
                usage = shutil.disk_usage(path)
                label = _get_drive_label(letter)
                drives.append({
                    "drive":       f"{letter}:",
                    "label":       label,
                    "total_bytes": usage.total,
                    "free_bytes":  usage.free,
                    "used_bytes":  usage.used,
                })
            except PermissionError:
                pass
    return drives


# ---------------------------------------------------------------------------
# CPU extended
# ---------------------------------------------------------------------------

def get_cpu_speed() -> dict:
    """Return CPU name and max clock speed.

    Returns:
        {"name": str, "speed_mhz": int}
    """
    raw = _ps(
        "Get-CimInstance Win32_Processor "
        "| Select-Object Name, MaxClockSpeed "
        "| ConvertTo-Json -Compress"
    )
    items = _parse_json(raw)
    info: dict = {"name": "unavailable", "speed_mhz": 0}
    if items:
        item = items[0]
        name = (item.get("Name") or "").strip()
        if name:
            info["name"] = name
        speed = item.get("MaxClockSpeed")
        if speed is not None:
            info["speed_mhz"] = int(speed)
    return info


def get_cpu_temperature() -> list[dict]:
    """Return thermal zone temperatures via ACPI WMI (Windows 10+).

    Returns:
        [{"zone": str, "celsius": float}, ...]
        Returns [] if no thermal zone data is available — not an error.
    """
    raw = _ps(
        "try { "
        "  $zones = Get-WmiObject -Namespace root/wmi "
        "           -Class MSAcpi_ThermalZoneTemperature "
        "           -ErrorAction SilentlyContinue; "
        "  if ($zones) { "
        "    $zones | ForEach-Object { "
        "      [PSCustomObject]@{ "
        "        Zone    = $_.InstanceName; "
        "        TenthsK = $_.CurrentTemperature "
        "      } "
        "    } | ConvertTo-Json -Compress "
        "  } "
        "} catch { }"
    )
    items = _parse_json(raw)
    results = []
    for item in items:
        tenths_k = item.get("TenthsK")
        zone = str(item.get("Zone") or "").strip()
        if tenths_k is not None:
            celsius = round((int(tenths_k) / 10) - 273.15, 1)
            # Sanity-check: ignore obviously wrong values
            if -20 <= celsius <= 150:
                results.append({"zone": zone, "celsius": celsius})
    return results


# ---------------------------------------------------------------------------
# RAM extended
# ---------------------------------------------------------------------------

def get_ram_speed() -> dict:
    """Return the maximum RAM speed across all physical memory sticks.

    Returns:
        {"speed_mhz": int}  — 0 if unavailable
    """
    raw = _ps(
        "Get-CimInstance Win32_PhysicalMemory "
        "| Select-Object Speed "
        "| ConvertTo-Json -Compress"
    )
    items = _parse_json(raw)
    speeds = []
    for item in items:
        s = item.get("Speed")
        if s is not None:
            try:
                speeds.append(int(s))
            except (TypeError, ValueError):
                pass
    return {"speed_mhz": max(speeds) if speeds else 0}


# ---------------------------------------------------------------------------
# GPU
# ---------------------------------------------------------------------------

def get_gpu_info() -> list[dict]:
    """Return info for all detected video controllers.

    Returns:
        [{"name": str, "vram_bytes": int, "driver": str}, ...]
    """
    raw = _ps(
        "Get-CimInstance Win32_VideoController "
        "| Select-Object Name, AdapterRAM, DriverVersion "
        "| ConvertTo-Json -Compress"
    )
    items = _parse_json(raw)
    results = []
    for item in items:
        name = (item.get("Name") or "").strip()
        if not name:
            continue
        vram = item.get("AdapterRAM") or 0
        driver = (item.get("DriverVersion") or "unavailable").strip()
        try:
            vram = int(vram)
        except (TypeError, ValueError):
            vram = 0
        results.append({"name": name, "vram_bytes": vram, "driver": driver})
    return results


# ---------------------------------------------------------------------------
# Network extended
# ---------------------------------------------------------------------------

def get_wifi_info() -> dict:
    """Return current Wi-Fi connection details.

    Returns:
        {"ssid": str, "signal": str, "ipv4": str, "adapter": str}
        Returns {} if no Wi-Fi is connected.
    """
    raw = _ps(
        "$w = netsh wlan show interfaces 2>$null; "
        "if ($w) { $w | Out-String } else { '' }"
    )
    if not raw.strip():
        return {}

    info: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("SSID") and "BSSID" not in line and ":" in line:
            info["ssid"] = line.split(":", 1)[1].strip()
        elif line.startswith("Signal") and ":" in line:
            info["signal"] = line.split(":", 1)[1].strip()
        elif line.startswith("Name") and ":" in line and "adapter" not in line.lower():
            info.setdefault("adapter", line.split(":", 1)[1].strip())

    if not info.get("ssid"):
        return {}

    # Get IP for the Wi-Fi adapter
    adapter = info.get("adapter", "")
    if adapter:
        ip_raw = _ps(
            f"Get-NetIPAddress -InterfaceAlias '{adapter}' "
            f"-AddressFamily IPv4 -ErrorAction SilentlyContinue "
            f"| Select-Object -ExpandProperty IPAddress"
        )
        info["ipv4"] = ip_raw.strip() or "-"
    else:
        info["ipv4"] = get_wifi_ip() or "-"

    return info


def get_public_ip() -> str | None:
    """Return the public-facing IP by querying api.ipify.org.

    Returns the IP string, or None if the request fails or times out.
    Never raises.
    """
    try:
        import urllib.request
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Ports
# ---------------------------------------------------------------------------

def get_ports() -> list[dict]:
    """Return listening TCP ports with owning process names.

    Returns:
        [{"port": int, "pid": int, "process": str}, ...]
    """
    raw = _ps(
        "$conns = Get-NetTCPConnection -State Listen "
        "         -ErrorAction SilentlyContinue "
        "         | Sort-Object LocalPort; "
        "$result = foreach ($c in $conns) { "
        "  $proc = (Get-Process -Id $c.OwningProcess "
        "           -ErrorAction SilentlyContinue).Name; "
        "  [PSCustomObject]@{ "
        "    Port    = $c.LocalPort; "
        "    PID     = $c.OwningProcess; "
        "    Process = if ($proc) { $proc } else { '?' } "
        "  } "
        "}; "
        "$result | ConvertTo-Json -Compress"
    )
    items = _parse_json(raw)
    results = []
    seen: set[int] = set()
    for item in items:
        port = item.get("Port")
        if port is None:
            continue
        port = int(port)
        if port in seen:
            continue
        seen.add(port)
        results.append({
            "port":    port,
            "pid":     int(item.get("PID") or 0),
            "process": str(item.get("Process") or "?"),
        })
    return results


# ---------------------------------------------------------------------------
# Processes
# ---------------------------------------------------------------------------

def get_processes() -> list[dict]:
    """Return top 30 running processes sorted by RAM usage (descending).

    Returns:
        [{"name": str, "pid": int, "cpu": str, "ram_bytes": int}, ...]
    """
    raw = _ps(
        "Get-Process "
        "| Select-Object Name, Id, CPU, WorkingSet "
        "| Sort-Object WorkingSet -Descending "
        "| Select-Object -First 30 "
        "| ConvertTo-Json -Compress"
    )
    items = _parse_json(raw)
    results = []
    for item in items:
        name = str(item.get("Name") or "?")
        pid  = int(item.get("Id") or 0)
        cpu  = item.get("CPU")
        cpu_str = f"{float(cpu):.1f}s" if cpu is not None else "-"
        ram = int(item.get("WorkingSet") or 0)
        results.append({"name": name, "pid": pid, "cpu": cpu_str, "ram_bytes": ram})
    return results


# ---------------------------------------------------------------------------
# Disk partitions
# ---------------------------------------------------------------------------

def get_disk_partitions() -> list[dict]:
    """Return partition info for all disks.

    Returns:
        [{"letter": str, "size_bytes": int, "type": str}, ...]
    """
    raw = _ps(
        "Get-Partition "
        "| Select-Object DriveLetter, Size, Type "
        "| ConvertTo-Json -Compress"
    )
    items = _parse_json(raw)
    results = []
    for item in items:
        letter = str(item.get("DriveLetter") or "").strip()
        size   = int(item.get("Size") or 0)
        ptype  = str(item.get("Type") or "Unknown").strip()
        results.append({
            "letter":     f"{letter}:" if letter and letter != "None" else "-",
            "size_bytes": size,
            "type":       ptype,
        })
    return results
