"""
IXX Shell — System Command Handlers (disk)
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
