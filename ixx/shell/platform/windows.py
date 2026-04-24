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
