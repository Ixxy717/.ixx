"""
IXX Shell — Network Command Handlers (ip, network)
"""

from __future__ import annotations

from .. import platform as _platform
from ..safety import render_table


def _platform_error(command: str) -> None:
    print(f"\n  [{command} — not yet available on this platform]\n")


# ---------------------------------------------------------------------------
# Adapter classification
# ---------------------------------------------------------------------------

_VPN_NAMES = {
    "vpn", "nordvpn", "nordlynx", "openvpn", "wireguard", "mullvad",
    "cisco", "anyconnect", "fortinet", "checkpoint", "pulse", "juniper",
    "tailscale", "zerotier",
}

_VIRTUAL_NAMES = {
    "vethernet", "wsl", "hyper-v", "vmware", "virtualbox", "vbox",
    "docker", "loopback", "pseudo", "virtual",
}

_WIFI_NAMES = {"wi-fi", "wifi", "wireless", "wlan", "802.11"}


def _classify_adapter(name: str, ip: str) -> str:
    """Return a category string for an adapter/IP pair.

    Categories (in priority order):
        loopback    127.x.x.x
        link-local  169.254.x.x
        vpn         VPN / tunnel adapters by name
        virtual     vEthernet, WSL, VMware, VirtualBox by name or IP range
        wifi        Wi-Fi adapters by name
        ethernet    physical Ethernet by name
        other       anything else
    """
    name_lower = name.lower()

    # IP-based checks first — these override name-based guesses
    if ip.startswith("127."):
        return "loopback"
    if ip.startswith("169.254."):
        return "link-local"

    # VPN / tunnel by name keyword
    if any(kw in name_lower for kw in _VPN_NAMES):
        return "vpn"

    # Virtual / container / hypervisor by name keyword
    if any(kw in name_lower for kw in _VIRTUAL_NAMES):
        return "virtual"

    # VirtualBox host-only and VMware NAT IP ranges
    if ip.startswith("192.168.56.") or ip.startswith("192.168.99."):
        return "virtual"

    # Docker/WSL bridge typically uses 172.17–172.19.
    # RFC 1918 defines 172.16.0.0/12 (172.16–172.31) as private LAN.
    # Only flag as virtual if outside the RFC 1918 range.
    if ip.startswith("172."):
        parts = ip.split(".")
        second = int(parts[1]) if len(parts) > 1 else 0
        if 16 <= second <= 31:
            return "other"   # valid RFC 1918 LAN — treat as real
        return "virtual"     # 172.0–172.15 or 172.32+ — likely VM/container

    # Wi-Fi by name
    if any(kw in name_lower for kw in _WIFI_NAMES):
        return "wifi"

    # Physical Ethernet by name
    if "ethernet" in name_lower or "lan" in name_lower:
        return "ethernet"

    return "other"


# Sort weight for network table rows: lower = appears first
_CATEGORY_ORDER = {
    "ethernet":   0,
    "wifi":       1,
    "vpn":        2,
    "other":      3,
    "virtual":    4,
    "link-local": 5,
    "loopback":   6,
}


def _network_sort_key(a: dict) -> tuple:
    """Sort: connected before disconnected, then by category."""
    connected = 0 if a.get("status") == "connected" else 1
    cat_order = _CATEGORY_ORDER.get(a.get("category", "other"), 3)
    return (connected, cat_order)


# ---------------------------------------------------------------------------
# ip — filtered primary view
# ---------------------------------------------------------------------------

def handle_ip(args: list[str]) -> None:
    """Show the most useful active LAN IPs. Filters noise by default.

    Primary section: physical Ethernet and Wi-Fi only.
    Other active section: VPN / tunnel adapters with real IPs.
    Use 'ip all' for the unfiltered full list.
    """
    try:
        raw = _platform.current().get_ip_info()
    except NotImplementedError:
        _platform_error("ip")
        return
    except Exception as e:
        print(f"\n  ip: could not retrieve info ({e})\n")
        return

    if not raw:
        print("\n  No active network adapters found.\n")
        return

    adapters = [{**a, "category": _classify_adapter(a["adapter"], a["ipv4"])} for a in raw]

    primary = [a for a in adapters if a["category"] in ("ethernet", "wifi")]
    other_active = [
        a for a in adapters
        if a["category"] in ("vpn", "other")
        and not a["ipv4"].startswith("169.254.")
    ]

    # If classification found nothing useful, fall back to the full table
    if not primary and not other_active:
        rows = [[a["adapter"], a["ipv4"]] for a in raw]
        print()
        print(render_table(["Adapter", "IPv4"], rows))
        print(f"\n  (tip: use 'ip all' to see all adapters)")
        print()
        return

    print()
    if primary:
        print("  Primary IP")
        for a in primary:
            label = "Wi-Fi" if a["category"] == "wifi" else "Ethernet"
            print(f"  {label}: {a['ipv4']}")

    if other_active:
        if primary:
            print()
        print("  Other active:")
        for a in other_active:
            print(f"  {a['adapter']}: {a['ipv4']}")

    print(f"\n  (tip: use 'ip all' to see all adapters)\n")


# ---------------------------------------------------------------------------
# ip all — unfiltered
# ---------------------------------------------------------------------------

def handle_ip_all(args: list[str]) -> None:
    """Show every IPv4 address including virtual, VPN, and link-local."""
    try:
        adapters = _platform.current().get_ip_info()
    except NotImplementedError:
        _platform_error("ip all")
        return
    except Exception as e:
        print(f"\n  ip all: could not retrieve info ({e})\n")
        return

    if not adapters:
        print("\n  No active network adapters found.\n")
        return

    rows = [[a["adapter"], a["ipv4"]] for a in adapters]
    print()
    print(render_table(["Adapter", "IPv4"], rows))
    print()


# ---------------------------------------------------------------------------
# ip wifi / ethernet / local
# ---------------------------------------------------------------------------

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
    """Show all local/private IPv4 addresses, excluding link-local."""
    try:
        raw = _platform.current().get_ip_info()
    except NotImplementedError:
        _platform_error("ip local")
        return
    except Exception as e:
        print(f"\n  ip local: could not retrieve info ({e})\n")
        return

    if not raw:
        print("\n  No active network adapters found.\n")
        return

    adapters = [
        {**a, "category": _classify_adapter(a["adapter"], a["ipv4"])}
        for a in raw
    ]
    # Exclude loopback and link-local — those aren't useful local addresses
    filtered = [a for a in adapters if a["category"] not in ("loopback", "link-local")]

    if not filtered:
        print("\n  No local IP addresses found.\n")
        return

    print()
    for a in filtered:
        print(f"  {a['ipv4']:<20}  {a['adapter']}")
    print()


# ---------------------------------------------------------------------------
# network — full adapter table, sorted
# ---------------------------------------------------------------------------

def handle_network(args: list[str]) -> None:
    """Show all adapters with status, IPv4, and gateway, sorted by usefulness."""
    try:
        raw = _platform.current().get_network_info()
    except NotImplementedError:
        _platform_error("network")
        return
    except Exception as e:
        print(f"\n  network: could not retrieve info ({e})\n")
        return

    if not raw:
        print("\n  No network adapters found.\n")
        return

    adapters = [
        {**a, "category": _classify_adapter(a["adapter"], a.get("ipv4", "-"))}
        for a in raw
    ]
    adapters.sort(key=_network_sort_key)

    rows = [
        [a["adapter"], a["status"], a["ipv4"], a["gateway"]]
        for a in adapters
    ]
    print()
    print(render_table(["Adapter", "Status", "IPv4", "Gateway"], rows))
    print()


# ---------------------------------------------------------------------------
# wifi — standalone Wi-Fi info
# ---------------------------------------------------------------------------

def handle_wifi(args: list[str]) -> None:
    """Show current Wi-Fi network name, signal strength, and IP."""
    try:
        info = _platform.current().get_wifi_info()
    except NotImplementedError:
        _platform_error("wifi")
        return
    except Exception as e:
        print(f"\n  wifi: could not retrieve info ({e})\n")
        return

    if not info:
        print("\n  No Wi-Fi connection found.\n")
        return

    print()
    print(f"  Network:  {info.get('ssid', '-')}")
    print(f"  Signal:   {info.get('signal', '-')}")
    print(f"  IP:       {info.get('ipv4', '-')}")
    print()


# ---------------------------------------------------------------------------
# ethernet — standalone Ethernet info
# ---------------------------------------------------------------------------

def handle_ethernet(args: list[str]) -> None:
    """Show the IPv4 address of the connected Ethernet adapter."""
    handle_ip_ethernet(args)


# ---------------------------------------------------------------------------
# ip public
# ---------------------------------------------------------------------------

def handle_ip_public(args: list[str]) -> None:
    """Show public-facing IP via external lookup."""
    try:
        ip = _platform.current().get_public_ip()
    except NotImplementedError:
        _platform_error("ip public")
        return
    except Exception as e:
        print(f"\n  ip public: could not retrieve info ({e})\n")
        return

    if ip:
        print(f"\n  Public IP:  {ip}")
        print(f"  (via external lookup: api.ipify.org)\n")
    else:
        print("\n  Could not reach external service.")
        print("  Check your internet connection and try again.\n")
