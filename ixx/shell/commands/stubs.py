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
from .hardware import handle_cpu, handle_cpu_cores, handle_ram
from .network import (
    handle_ip,
    handle_ip_all,
    handle_ip_wifi,
    handle_ip_ethernet,
    handle_ip_local,
    handle_network,
)
from .system import handle_disk, handle_disk_space
from .files import handle_folder_size, handle_open, handle_list


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
                examples=["cpu core-count"],
                handler=handle_cpu_cores,
            ),
            "temperature": CommandNode(
                "temperature",
                description="CPU temperature (if available)",
                handler=_stub("cpu temperature"),
            ),
            "speed": CommandNode(
                "speed",
                description="CPU clock speed",
                handler=_stub("cpu speed"),
            ),
            "info": CommandNode(
                "info",
                description="Full CPU summary",
                handler=_stub("cpu info"),
            ),
        },
    )


def _build_ram() -> CommandNode:
    return CommandNode(
        "ram",
        description="Total, used, and free RAM",
        examples=["ram"],
        handler=handle_ram,
        executable_with_children=True,
        subcommands={
            "free": CommandNode(
                "free",
                description="Free RAM available",
                handler=_stub("ram free"),
            ),
            "usage": CommandNode(
                "usage",
                description="RAM usage percentage",
                handler=_stub("ram usage"),
            ),
            "speed": CommandNode(
                "speed",
                description="RAM speed (MHz)",
                handler=_stub("ram speed"),
            ),
        },
    )


def _build_gpu() -> CommandNode:
    return CommandNode(
        "gpu",
        description="GPU name, VRAM, usage, driver",
        examples=["gpu"],
        handler=_stub("gpu"),
    )


def _build_disk() -> CommandNode:
    return CommandNode(
        "disk",
        description="List disks, space, and health",
        examples=["disk", "disk space"],
        handler=handle_disk,
        executable_with_children=True,
        subcommands={
            "space": CommandNode(
                "space",
                description="Used and free space per disk",
                examples=["disk space"],
                handler=handle_disk_space,
            ),
            "health": CommandNode(
                "health",
                description="SMART health status",
                handler=_stub("disk health"),
                requires_admin=True,
            ),
            "partitions": CommandNode(
                "partitions",
                description="Partition table",
                handler=_stub("disk partitions"),
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
                description="Public-facing IP address",
                handler=_stub("ip public"),
            ),
        },
    )


def _build_wifi() -> CommandNode:
    return CommandNode(
        "wifi",
        description="Wi-Fi name, IP, signal strength",
        examples=["wifi"],
        handler=_stub("wifi"),
    )


def _build_ports() -> CommandNode:
    return CommandNode(
        "ports",
        description="Listening ports in a readable table",
        examples=["ports"],
        handler=_stub("ports"),
    )


def _build_processes() -> CommandNode:
    return CommandNode(
        "processes",
        description="Running processes",
        examples=["processes"],
        handler=_stub("processes"),
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
                arg_hint='<name or pattern> [in <path>]',
                examples=[
                    'find file "invoice"',
                    'find file "*.pdf" in downloads',
                ],
                handler=_stub("find file"),
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
        _build_native(),
        _build_ssh(),
        _build_servers(),
        _build_server(),
    ])
