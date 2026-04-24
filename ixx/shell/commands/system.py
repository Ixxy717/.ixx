"""
IXX Shell — System Command Handlers (disk, ports, processes)
"""

from __future__ import annotations

from .. import platform as _platform
from ..safety import format_bytes, render_table


def _platform_error(command: str) -> None:
    print(f"\n  [{command} — not yet available on this platform]\n")


# ---------------------------------------------------------------------------
# disk
# ---------------------------------------------------------------------------

def handle_disk(args: list[str]) -> None:
    """Show logical drives with total and free space."""
    try:
        drives = _platform.current().get_disk_info()
    except NotImplementedError:
        _platform_error("disk")
        return
    except Exception as e:
        print(f"\n  disk: could not retrieve info ({e})\n")
        return

    if not drives:
        print("\n  No drives found.\n")
        return

    rows = [
        [
            d["drive"],
            d.get("label") or "-",
            format_bytes(d["total_bytes"]),
            format_bytes(d["free_bytes"]),
        ]
        for d in drives
    ]
    print()
    print(render_table(["Drive", "Label", "Total", "Free"], rows))
    print()


def handle_disk_space(args: list[str]) -> None:
    """Show drive space with used and percent columns."""
    try:
        drives = _platform.current().get_disk_info()
    except NotImplementedError:
        _platform_error("disk space")
        return
    except Exception as e:
        print(f"\n  disk space: could not retrieve info ({e})\n")
        return

    if not drives:
        print("\n  No drives found.\n")
        return

    rows = []
    for d in drives:
        total = d["total_bytes"]
        free  = d["free_bytes"]
        used  = d.get("used_bytes", max(0, total - free))
        pct   = f"{(used / total * 100):.0f}%" if total > 0 else "-"
        rows.append([
            d["drive"],
            d.get("label") or "-",
            format_bytes(total),
            format_bytes(used),
            format_bytes(free),
            pct,
        ])

    print()
    print(render_table(["Drive", "Label", "Total", "Used", "Free", "Used%"], rows))
    print()


# ---------------------------------------------------------------------------
# disk partitions
# ---------------------------------------------------------------------------

def handle_disk_partitions(args: list[str]) -> None:
    """Show partition table for all disks."""
    try:
        partitions = _platform.current().get_disk_partitions()
    except NotImplementedError:
        _platform_error("disk partitions")
        return
    except Exception as e:
        print(f"\n  disk partitions: could not retrieve info ({e})\n")
        return

    if not partitions:
        print("\n  No partition data available.\n")
        return

    rows = [
        [p["letter"], format_bytes(p["size_bytes"]) if p["size_bytes"] else "-", p["type"]]
        for p in partitions
    ]
    print()
    print(render_table(["Drive", "Size", "Type"], rows))
    print()


# ---------------------------------------------------------------------------
# ports
# ---------------------------------------------------------------------------

def handle_ports(args: list[str]) -> None:
    """Show listening TCP ports with owning process names."""
    try:
        ports = _platform.current().get_ports()
    except NotImplementedError:
        _platform_error("ports")
        return
    except Exception as e:
        print(f"\n  ports: could not retrieve info ({e})\n")
        return

    if not ports:
        print("\n  No listening ports found.\n")
        return

    rows = [
        [str(p["port"]), str(p["pid"]), p["process"]]
        for p in ports
    ]
    print()
    print(render_table(["Port", "PID", "Process"], rows))
    print()


# ---------------------------------------------------------------------------
# processes
# ---------------------------------------------------------------------------

def handle_processes(args: list[str]) -> None:
    """Show top running processes sorted by RAM usage."""
    try:
        procs = _platform.current().get_processes()
    except NotImplementedError:
        _platform_error("processes")
        return
    except Exception as e:
        print(f"\n  processes: could not retrieve info ({e})\n")
        return

    if not procs:
        print("\n  No process data available.\n")
        return

    rows = [
        [p["name"], str(p["pid"]), p["cpu"], format_bytes(p["ram_bytes"])]
        for p in procs
    ]
    print()
    print(render_table(["Name", "PID", "CPU", "RAM"], rows))
    print()
