"""
IXX Shell — Hardware Command Handlers (cpu, ram, gpu)
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


def handle_cpu_info(args: list[str]) -> None:
    """Show full CPU summary: name, cores, threads, speed, and usage."""
    try:
        info  = _platform.current().get_cpu_info()
        speed = _platform.current().get_cpu_speed()
    except NotImplementedError:
        _platform_error("cpu info")
        return
    except Exception as e:
        print(f"\n  cpu info: could not retrieve info ({e})\n")
        return

    speed_mhz = speed.get("speed_mhz", 0)
    speed_str = f"{speed_mhz / 1000:.2f} GHz" if speed_mhz else "-"

    print()
    print(f"  CPU:     {info['name']}")
    print(f"  Cores:   {info['cores']}")
    print(f"  Threads: {info['threads']}")
    print(f"  Speed:   {speed_str}")
    print(f"  Usage:   {info['usage_pct']}")
    print()


def handle_cpu_speed(args: list[str]) -> None:
    """Show CPU clock speed."""
    try:
        speed = _platform.current().get_cpu_speed()
    except NotImplementedError:
        _platform_error("cpu speed")
        return
    except Exception as e:
        print(f"\n  cpu speed: could not retrieve info ({e})\n")
        return

    speed_mhz = speed.get("speed_mhz", 0)
    speed_str = f"{speed_mhz / 1000:.2f} GHz" if speed_mhz else "unavailable"

    print()
    print(f"  {speed.get('name', 'CPU')}")
    print(f"  Speed:  {speed_str}")
    print()


def handle_cpu_temperature(args: list[str]) -> None:
    """Show CPU temperature from ACPI thermal zones (Windows 10+)."""
    try:
        zones = _platform.current().get_cpu_temperature()
    except NotImplementedError:
        _platform_error("cpu temperature")
        return
    except Exception as e:
        print(f"\n  cpu temperature: could not retrieve info ({e})\n")
        return

    if not zones:
        print(
            "\n  Temperature data not available.\n"
            "\n"
            "  On AMD Ryzen and many desktop systems, Windows does not expose\n"
            "  CPU temperatures natively. To enable 'cpu temp':\n"
            "\n"
            "  1. Download and run LibreHardwareMonitor (free, no install needed):\n"
            "       https://github.com/LibreHardwareMonitor/LibreHardwareMonitor\n"
            "\n"
            "  2. Or run OpenHardwareMonitor, then retry 'cpu temp'.\n"
            "\n"
            "  Either tool runs in the background and exposes sensor data\n"
            "  through WMI that IXX can read.\n"
        )
        return

    print()
    for z in zones:
        label = z.get("zone") or "Thermal zone"
        # Shorten verbose ACPI instance names for display
        if "\\" in label:
            label = label.rsplit("\\", 1)[-1]
        print(f"  {label:<30}  {z['celsius']} \u00b0C")
    source = zones[0].get("source", "")
    if source in ("OHM", "LHM"):
        print(f"\n  (via {source} — LibreHardwareMonitor/OpenHardwareMonitor)")
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


def handle_ram_free(args: list[str]) -> None:
    """Show free RAM."""
    try:
        info = _platform.current().get_ram_info()
    except NotImplementedError:
        _platform_error("ram free")
        return
    except Exception as e:
        print(f"\n  ram free: could not retrieve info ({e})\n")
        return

    print()
    print(f"  Free:  {format_bytes(info.get('free_bytes', 0))}")
    print()


def handle_ram_usage(args: list[str]) -> None:
    """Show used RAM and percentage."""
    try:
        info = _platform.current().get_ram_info()
    except NotImplementedError:
        _platform_error("ram usage")
        return
    except Exception as e:
        print(f"\n  ram usage: could not retrieve info ({e})\n")
        return

    total = info.get("total_bytes", 0)
    used  = info.get("used_bytes",  0)
    pct   = round(used / total * 100) if total else 0

    print()
    print(f"  Used:  {format_bytes(used)}  ({pct}%)")
    print()


def handle_ram_speed(args: list[str]) -> None:
    """Show RAM speed in MHz."""
    try:
        speed = _platform.current().get_ram_speed()
    except NotImplementedError:
        _platform_error("ram speed")
        return
    except Exception as e:
        print(f"\n  ram speed: could not retrieve info ({e})\n")
        return

    mhz = speed.get("speed_mhz", 0)
    print()
    print(f"  Speed:  {mhz} MHz" if mhz else "  Speed:  unavailable")
    print()


# ---------------------------------------------------------------------------
# gpu
# ---------------------------------------------------------------------------

def handle_gpu(args: list[str]) -> None:
    """Show GPU name, VRAM, and driver version."""
    try:
        gpus = _platform.current().get_gpu_info()
    except NotImplementedError:
        _platform_error("gpu")
        return
    except Exception as e:
        print(f"\n  gpu: could not retrieve info ({e})\n")
        return

    if not gpus:
        print("\n  No GPU information available.\n")
        return

    print()
    for g in gpus:
        vram = format_bytes(g["vram_bytes"]) if g["vram_bytes"] else "-"
        print(f"  GPU:     {g['name']}")
        print(f"  VRAM:    {vram}")
        print(f"  Driver:  {g['driver']}")
        if len(gpus) > 1:
            print()
    print()


def handle_gpu_vram(args: list[str]) -> None:
    """Show GPU VRAM only."""
    try:
        gpus = _platform.current().get_gpu_info()
    except NotImplementedError:
        _platform_error("gpu vram")
        return
    except Exception as e:
        print(f"\n  gpu vram: could not retrieve info ({e})\n")
        return

    if not gpus:
        print("\n  No GPU information available.\n")
        return

    print()
    for g in gpus:
        vram = format_bytes(g["vram_bytes"]) if g["vram_bytes"] else "-"
        print(f"  {g['name']}")
        print(f"  VRAM:  {vram}")
        if len(gpus) > 1:
            print()
    print()


def handle_gpu_driver(args: list[str]) -> None:
    """Show GPU driver version only."""
    try:
        gpus = _platform.current().get_gpu_info()
    except NotImplementedError:
        _platform_error("gpu driver")
        return
    except Exception as e:
        print(f"\n  gpu driver: could not retrieve info ({e})\n")
        return

    if not gpus:
        print("\n  No GPU information available.\n")
        return

    print()
    for g in gpus:
        print(f"  {g['name']}")
        print(f"  Driver:  {g['driver']}")
        if len(gpus) > 1:
            print()
    print()
