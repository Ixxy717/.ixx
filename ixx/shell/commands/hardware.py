"""
IXX Shell — Hardware Command Handlers (cpu, ram)
"""

from __future__ import annotations

from .. import platform as _platform
from ..safety import format_bytes


def _platform_error(command: str) -> None:
    print(f"\n  [{command} — not yet available on this platform]\n")


# ---------------------------------------------------------------------------
# cpu
# ---------------------------------------------------------------------------

def handle_cpu(args: list[str]) -> None:
    """Show CPU name, core count, thread count, and usage."""
    try:
        info = _platform.current().get_cpu_info()
    except NotImplementedError:
        _platform_error("cpu")
        return
    except Exception as e:
        print(f"\n  cpu: could not retrieve info ({e})\n")
        return

    print()
    print(f"  CPU:     {info['name']}")
    print(f"  Cores:   {info['cores']}")
    print(f"  Threads: {info['threads']}")
    print(f"  Usage:   {info['usage_pct']}")
    print()


def handle_cpu_cores(args: list[str]) -> None:
    """Show CPU model, core count, and thread count."""
    try:
        info = _platform.current().get_cpu_core_count()
    except NotImplementedError:
        _platform_error("cpu core-count")
        return
    except Exception as e:
        print(f"\n  cpu core-count: could not retrieve info ({e})\n")
        return

    print()
    print(f"  {info['name']}")
    print(f"  Cores:   {info['cores']}")
    print(f"  Threads: {info['threads']}")
    print()


# ---------------------------------------------------------------------------
# ram
# ---------------------------------------------------------------------------

def handle_ram(args: list[str]) -> None:
    """Show total, used, and free RAM."""
    try:
        info = _platform.current().get_ram_info()
    except NotImplementedError:
        _platform_error("ram")
        return
    except Exception as e:
        print(f"\n  ram: could not retrieve info ({e})\n")
        return

    total = info.get("total_bytes", 0)
    used  = info.get("used_bytes",  0)
    free  = info.get("free_bytes",  0)

    print()
    print("  RAM")
    print(f"  Total: {format_bytes(total)}")
    print(f"  Used:  {format_bytes(used)}")
    print(f"  Free:  {format_bytes(free)}")
    print()
