"""
IXX Shell — Network Command Handlers (ip, network)
"""

from __future__ import annotations

from .. import platform as _platform
from ..safety import render_table


def _platform_error(command: str) -> None:
    print(f"\n  [{command} — not yet available on this platform]\n")


# ---------------------------------------------------------------------------
# ip
# ---------------------------------------------------------------------------

def handle_ip(args: list[str]) -> None:
    """Show all active local IPv4 addresses."""
    try:
        adapters = _platform.current().get_ip_info()
    except NotImplementedError:
        _platform_error("ip")
        return
    except Exception as e:
        print(f"\n  ip: could not retrieve info ({e})\n")
        return

    if not adapters:
        print("\n  No active network adapters found.\n")
        return

    rows = [[a["adapter"], a["ipv4"]] for a in adapters]
    print()
    print(render_table(["Adapter", "IPv4"], rows))
    print()


def handle_ip_wifi(args: list[str]) -> None:
    """Show the IPv4 address of the connected Wi-Fi adapter."""
    try:
        ip = _platform.current().get_wifi_ip()
    except NotImplementedError:
        _platform_error("ip wifi")
        return
    except Exception as e:
        print(f"\n  ip wifi: could not retrieve info ({e})\n")
        return

    if ip:
        print(f"\n  Wi-Fi: {ip}\n")
    else:
        print("\n  No connected Wi-Fi adapter found.\n")


def handle_ip_ethernet(args: list[str]) -> None:
    """Show the IPv4 address of the connected Ethernet adapter."""
    try:
        ip = _platform.current().get_ethernet_ip()
    except NotImplementedError:
        _platform_error("ip ethernet")
        return
    except Exception as e:
        print(f"\n  ip ethernet: could not retrieve info ({e})\n")
        return

    if ip:
        print(f"\n  Ethernet: {ip}\n")
    else:
        print("\n  No connected Ethernet adapter found.\n")


def handle_ip_local(args: list[str]) -> None:
    """Show all local/private IPv4 addresses."""
    try:
        adapters = _platform.current().get_ip_info()
    except NotImplementedError:
        _platform_error("ip local")
        return
    except Exception as e:
        print(f"\n  ip local: could not retrieve info ({e})\n")
        return

    if not adapters:
        print("\n  No active network adapters found.\n")
        return

    print()
    for a in adapters:
        print(f"  {a['ipv4']:<20}  {a['adapter']}")
    print()


# ---------------------------------------------------------------------------
# network
# ---------------------------------------------------------------------------

def handle_network(args: list[str]) -> None:
    """Show all adapters with status, IPv4, and gateway."""
    try:
        adapters = _platform.current().get_network_info()
    except NotImplementedError:
        _platform_error("network")
        return
    except Exception as e:
        print(f"\n  network: could not retrieve info ({e})\n")
        return

    if not adapters:
        print("\n  No network adapters found.\n")
        return

    rows = [
        [a["adapter"], a["status"], a["ipv4"], a["gateway"]]
        for a in adapters
    ]
    print()
    print(render_table(["Adapter", "Status", "IPv4", "Gateway"], rows))
    print()
