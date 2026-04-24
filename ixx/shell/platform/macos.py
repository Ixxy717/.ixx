"""IXX Shell — macOS Platform Adapter (placeholder)

Real implementations are planned for a future release.
"""

from __future__ import annotations


def _not_yet(name: str):
    raise NotImplementedError(f"{name} is not yet available on macOS")


def get_ip_info() -> list[dict]:
    _not_yet("ip")


def get_wifi_ip() -> str | None:
    _not_yet("ip wifi")


def get_ethernet_ip() -> str | None:
    _not_yet("ip ethernet")


def get_network_info() -> list[dict]:
    _not_yet("network")


def get_cpu_info() -> dict:
    _not_yet("cpu")


def get_cpu_core_count() -> dict:
    _not_yet("cpu core-count")


def get_ram_info() -> dict:
    _not_yet("ram")


def get_disk_info() -> list[dict]:
    _not_yet("disk")
