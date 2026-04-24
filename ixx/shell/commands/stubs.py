"""
IXX Shell — Command Registry

Defines the full command tree: metadata, examples, safety flags, and handlers.

Commands that are live in v0.3.0 are wired to real handler functions.
Commands planned for later releases use the _stub() factory which prints
a "not yet implemented" notice.

To add a new command: register a CommandNode here. The guidance engine,
help system, and fuzzy correction all pick it up automatically.
"""

from __future__ import annotations

from ..registry import CommandNode, CommandRegistry
from ..renderer import show_not_implemented

# Live handlers (v0.3.0)
from .hardware import (
    handle_cpu, handle_cpu_cores, handle_cpu_info, handle_cpu_speed,
    handle_cpu_temperature,
    handle_ram, handle_ram_free, handle_ram_usage, handle_ram_speed,
    handle_gpu, handle_gpu_vram, handle_gpu_driver, handle_gpu_temp,
)
from .network import (
    handle_ip,
    handle_ip_all,
    handle_ip_wifi,
    handle_ip_ethernet,
    handle_ip_local,
    handle_ip_public,
    handle_network,
    handle_wifi,
    handle_ethernet,
)
from .system import (
    handle_disk, handle_disk_space, handle_disk_partitions,
    handle_disk_health, handle_disk_smart, handle_disk_smart_full,
    handle_ports, handle_processes,
)
from .files import handle_folder_size, handle_open, handle_list, handle_find_file
from .setup import handle_setup
from .demo_walk import handle_demo_walk


# ---------------------------------------------------------------------------
# Stub handler factory
# ---------------------------------------------------------------------------

def _stub(path: str, note: str = "planned for a future release"):
    """Return a handler that prints the standard not-implemented notice."""
    def handler(*_args, **_kwargs) -> None:
        show_not_implemented(path, note)
    handler.__name__ = path.replace(" ", "_")
    return handler


# ---------------------------------------------------------------------------
# Command definitions
# ---------------------------------------------------------------------------

def _build_cpu() -> CommandNode:
    return CommandNode(
        "cpu",
        description="CPU name, usage, cores, threads",
        examples=["cpu", "cpu core-count"],
        handler=handle_cpu,
        executable_with_children=True,
        subcommands={
            "core-count": CommandNode(
                "core-count",
                description="Core and thread count",
                aliases=["cores", "threads"],
                examples=["cpu core-count"],
                handler=handle_cpu_cores,
            ),
            "info": CommandNode(
                "info",
                description="Full CPU summary (name, cores, speed, usage)",
                examples=["cpu info"],
                handler=handle_cpu_info,
            ),
            "speed": CommandNode(
                "speed",
                description="CPU clock speed",
                examples=["cpu speed"],
                handler=handle_cpu_speed,
            ),
            "temperature": CommandNode(
                "temperature",
                description="CPU temperature (if available)",
                aliases=["temp"],
                examples=["cpu temperature"],
                handler=handle_cpu_temperature,
            ),
            "usage": CommandNode(
                "usage",
                description="CPU usage percentage (alias: used, load)",
                aliases=["used", "load"],
                examples=["cpu usage"],
                handler=handle_cpu,
            ),
        },
    )


def _build_ram() -> CommandNode:
    return CommandNode(
        "ram",
        description="Total, used, and free RAM",
        aliases=["memory"],
        examples=["ram"],
        handler=handle_ram,
        executable_with_children=True,
        subcommands={
            "free": CommandNode(
                "free",
                description="Free RAM available",
                aliases=["available", "avail"],
                examples=["ram free"],
                handler=handle_ram_free,
            ),
            "usage": CommandNode(
                "usage",
                description="RAM usage percentage",
                aliases=["used", "consumed"],
                examples=["ram usage"],
                handler=handle_ram_usage,
            ),
            "total": CommandNode(
                "total",
                description="Total installed RAM (shows full overview)",
                examples=["ram total"],
                handler=handle_ram,
            ),
            "speed": CommandNode(
                "speed",
                description="RAM speed (MHz)",
                examples=["ram speed"],
                handler=handle_ram_speed,
            ),
        },
    )


def _build_gpu() -> CommandNode:
    return CommandNode(
        "gpu",
        description="GPU name, VRAM, driver, and temperature",
        examples=["gpu", "gpu vram", "gpu driver", "gpu temp"],
        handler=handle_gpu,
        executable_with_children=True,
        subcommands={
            "vram": CommandNode(
                "vram",
                description="GPU VRAM size",
                examples=["gpu vram"],
                handler=handle_gpu_vram,
            ),
            "driver": CommandNode(
                "driver",
                description="GPU driver version",
                examples=["gpu driver"],
                handler=handle_gpu_driver,
            ),
            "temp": CommandNode(
                "temp",
                description="GPU temperature",
                aliases=["temperature"],
                examples=["gpu temp"],
                handler=handle_gpu_temp,
            ),
        },
    )


def _build_disk() -> CommandNode:
    return CommandNode(
        "disk",
        description="List disks, space, health, and SMART status",
        aliases=["storage", "drive", "drives"],
        examples=["disk", "disk space", "disk health", "disk smart"],
        handler=handle_disk,
        executable_with_children=True,
        subcommands={
            "space": CommandNode(
                "space",
                description="Used and free space per disk",
                aliases=["free", "usage", "used"],
                examples=["disk space"],
                handler=handle_disk_space,
            ),
            "partitions": CommandNode(
                "partitions",
                description="Partition table",
                examples=["disk partitions"],
                handler=handle_disk_partitions,
            ),
            "health": CommandNode(
                "health",
                description="Physical disk health status",
                examples=["disk health"],
                handler=handle_disk_health,
            ),
            "smart": CommandNode(
                "smart",
                description="SMART predictive-failure flag",
                examples=["disk smart", "disk smart full"],
                handler=handle_disk_smart,
                executable_with_children=True,
                subcommands={
                    "full": CommandNode(
                        "full",
                        description="Full SMART attribute table (requires admin)",
                        examples=["disk smart full"],
                        handler=handle_disk_smart_full,
                        requires_admin=True,
                    ),
                },
            ),
        },
    )


def _build_network() -> CommandNode:
    return CommandNode(
        "network",
        description="All adapters, IPs, status, gateway",
        examples=["network"],
        handler=handle_network,
        executable_with_children=True,
    )


def _build_ip() -> CommandNode:
    return CommandNode(
        "ip",
        description="Show active local IP addresses",
        examples=["ip", "ip wifi", "ip ethernet", "ip local"],
        handler=handle_ip,
        executable_with_children=True,
        subcommands={
            "all": CommandNode(
                "all",
                description="All active IPs (unfiltered)",
                handler=handle_ip_all,
            ),
            "wifi": CommandNode(
                "wifi",
                description="Wi-Fi IPv4 address",
                handler=handle_ip_wifi,
            ),
            "ethernet": CommandNode(
                "ethernet",
                description="Ethernet IPv4 address",
                handler=handle_ip_ethernet,
            ),
            "local": CommandNode(
                "local",
                description="All local/private IPs",
                handler=handle_ip_local,
            ),
            "public": CommandNode(
                "public",
                description="Public-facing IP address (external lookup)",
                examples=["ip public"],
                handler=handle_ip_public,
            ),
        },
    )


def _build_ethernet() -> CommandNode:
    return CommandNode(
        "ethernet",
        description="Show Ethernet IPv4 address",
        examples=["ethernet"],
        handler=handle_ethernet,
    )


def _build_wifi() -> CommandNode:
    return CommandNode(
        "wifi",
        description="Wi-Fi name, IP, and signal strength",
        examples=["wifi"],
        handler=handle_wifi,
    )


def _build_ports() -> CommandNode:
    return CommandNode(
        "ports",
        description="Listening ports in a readable table",
        examples=["ports"],
        handler=handle_ports,
    )


def _build_processes() -> CommandNode:
    return CommandNode(
        "processes",
        description="Running processes (top 30 by RAM)",
        examples=["processes"],
        handler=handle_processes,
    )


def _build_kill() -> CommandNode:
    return CommandNode(
        "kill",
        description="End a process by name or ID",
        examples=["kill process chrome", "kill process 1234"],
        destructive=True,
        warning_text="this command can stop running programs.",
        subcommands={
            "process": CommandNode(
                "process",
                description="End a process by name or PID",
                arg_hint="<name or PID>",
                examples=["kill process chrome", "kill process 1234"],
                destructive=True,
                warning_text="this command can stop running programs.",
                handler=_stub("kill process"),
            ),
        },
    )


def _build_folder() -> CommandNode:
    return CommandNode(
        "folder",
        description="Folder operations",
        examples=["folder size downloads", "folder size documents"],
        subcommands={
            "size": CommandNode(
                "size",
                description="Size of a folder",
                arg_hint="<path>",
                examples=[
                    "folder size downloads",
                    "folder size desktop",
                    'folder size "desktop/my folder"',
                ],
                handler=handle_folder_size,
            ),
        },
    )


def _build_find() -> CommandNode:
    return CommandNode(
        "find",
        description="Find files by name or pattern",
        subcommands={
            "file": CommandNode(
                "file",
                description="Search for files by name or pattern",
                arg_hint='<pattern> [in <path>]',
                examples=[
                    'find file "invoice"',
                    'find file "*.pdf" in downloads',
                ],
                handler=handle_find_file,
            ),
        },
    )


def _build_open() -> CommandNode:
    return CommandNode(
        "open",
        description="Open a folder or file in the explorer",
        arg_hint="<path>",
        examples=["open downloads", "open desktop", 'open "desktop/my folder"'],
        handler=handle_open,
    )


def _build_list() -> CommandNode:
    return CommandNode(
        "list",
        description="List files and folders",
        arg_hint="<path>",
        examples=["list downloads", "list desktop", "list"],
        handler=handle_list,
    )


def _build_copy() -> CommandNode:
    return CommandNode(
        "copy",
        description="Copy a file or folder to a destination",
        arg_hint="<source> to <destination>",
        examples=[
            "copy report.pdf to desktop",
            "copy downloads/file.zip to documents",
        ],
        handler=_stub("copy"),
    )


def _build_move() -> CommandNode:
    return CommandNode(
        "move",
        description="Move a file or folder to a destination",
        arg_hint="<source> to <destination>",
        examples=["move report.pdf to documents"],
        destructive=True,
        handler=_stub("move"),
    )


def _build_delete() -> CommandNode:
    return CommandNode(
        "delete",
        description="Delete a file, folder, or run cleanup",
        examples=[
            "delete file old.txt",
            "delete folder old-stuff",
            "delete temp",
        ],
        destructive=True,
        subcommands={
            "file": CommandNode(
                "file",
                description="Delete a single file",
                arg_hint="<path>",
                destructive=True,
                examples=["delete file old.txt"],
                handler=_stub("delete file"),
            ),
            "folder": CommandNode(
                "folder",
                description="Delete a folder [recursive] [force] [dry-run]",
                arg_hint="<path> [recursive] [force] [dry-run]",
                destructive=True,
                examples=[
                    "delete folder old-stuff",
                    "delete folder old-stuff recursive",
                ],
                handler=_stub("delete folder"),
            ),
            "temp": CommandNode(
                "temp",
                description="Clean temporary files",
                destructive=True,
                examples=["delete temp"],
                handler=_stub("delete temp"),
            ),
            "empty-trash": CommandNode(
                "empty-trash",
                description="Empty the recycle bin / trash",
                destructive=True,
                examples=["delete empty-trash"],
                handler=_stub("delete empty-trash"),
            ),
        },
    )


def _build_demo() -> CommandNode:
    return CommandNode(
        "demo",
        description="Interactive IXX walkthrough — learn the language step by step",
        examples=["demo"],
        handler=handle_demo_walk,
    )


def _build_setup() -> CommandNode:
    return CommandNode(
        "setup",
        description="Register .ixx file type and icon on Windows",
        examples=["setup"],
        handler=handle_setup,
    )


def _build_native() -> CommandNode:
    return CommandNode(
        "native",
        description="Pass a command to the host shell (escape hatch)",
        arg_hint='"<shell command>"',
        examples=['native "Get-NetIPAddress"', 'native "dir"'],
        handler=_stub("native"),
    )


def _build_ssh() -> CommandNode:
    return CommandNode(
        "ssh",
        description="Connect to a remote server via SSH",
        arg_hint="<user@host or saved-server>",
        examples=["ssh user@192.168.1.50", "ssh my-server"],
        handler=_stub("ssh", note="planned for remote access release"),
    )


def _build_servers() -> CommandNode:
    return CommandNode(
        "servers",
        description="List saved SSH server profiles",
        examples=["servers"],
        handler=_stub("servers", note="planned for remote access release"),
    )


def _build_server() -> CommandNode:
    return CommandNode(
        "server",
        description="Manage saved SSH server profiles",
        examples=["server add my-server", "server list"],
        subcommands={
            "add": CommandNode(
                "add",
                description="Save a new server profile",
                arg_hint="<name>",
                examples=["server add my-server"],
                handler=_stub("server add", note="planned for remote access release"),
            ),
            "list": CommandNode(
                "list",
                description="List saved server profiles",
                examples=["server list"],
                handler=_stub("server list", note="planned for remote access release"),
            ),
        },
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def register_all(registry: CommandRegistry) -> None:
    """Register every command into *registry*."""
    registry.register_all([
        _build_cpu(),
        _build_ram(),
        _build_gpu(),
        _build_disk(),
        _build_network(),
        _build_ip(),
        _build_wifi(),
        _build_ethernet(),
        _build_ports(),
        _build_processes(),
        _build_kill(),
        _build_folder(),
        _build_find(),
        _build_open(),
        _build_list(),
        _build_copy(),
        _build_move(),
        _build_delete(),
        _build_demo(),
        _build_setup(),
        _build_native(),
        _build_ssh(),
        _build_servers(),
        _build_server(),
    ])
