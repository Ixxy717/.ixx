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


def get_cpu_speed() -> dict:
    _not_yet("cpu speed")


def get_cpu_temperature() -> list[dict]:
    _not_yet("cpu temperature")


def get_gpu_temperature() -> list[dict]:
    _not_yet("gpu temperature")


def get_ram_info() -> dict:
    _not_yet("ram")


def get_ram_speed() -> dict:
    _not_yet("ram speed")


def get_gpu_info() -> list[dict]:
    _not_yet("gpu")


def get_disk_info() -> list[dict]:
    _not_yet("disk")


def get_disk_health() -> list[dict]:
    _not_yet("disk health")


def get_disk_smart() -> list[dict]:
    _not_yet("disk smart")


def get_wifi_info() -> dict:
    _not_yet("wifi")


def get_public_ip() -> str | None:
    _not_yet("ip public")


def get_ports() -> list[dict]:
    _not_yet("ports")


def get_processes() -> list[dict]:
    _not_yet("processes")


def get_disk_partitions() -> list[dict]:
    _not_yet("disk partitions")
