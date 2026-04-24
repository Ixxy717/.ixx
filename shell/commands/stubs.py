"""
IXX Shell — Stub Commands

Every command in this file is registered with the full metadata the
guidance engine and help system need (description, subcommands, examples,
safety flags).  The handler for each command simply prints a
"not yet implemented" notice via the renderer.

When v0.3.0 arrives, replace a stub handler with a real one — the
guidance tree, help text, and fuzzy correction all stay unchanged.
"""

from __future__ import annotations

from ..registry import CommandNode, CommandRegistry
from ..renderer import show_not_implemented


# ---------------------------------------------------------------------------
# Stub handler factory
# ---------------------------------------------------------------------------

def _stub(path: str):
    """Return a handler that prints the standard not-implemented notice."""
    def handler(*_args, **_kwargs) -> None:
        show_not_implemented(path)
    handler.__name__ = path.replace(" ", "_")
    return handler


# ---------------------------------------------------------------------------
# Command definitions
# ---------------------------------------------------------------------------

def _build_cpu() -> CommandNode:
    return CommandNode(
        "cpu",
        description="CPU name, usage, cores, threads, speed, temperature",
        examples=["cpu", "cpu usage", "cpu core-count", "cpu temperature"],
        handler=_stub("cpu"),
        subcommands={
            "usage": CommandNode(
                "usage",
                description="Current CPU usage percentage",
                handler=_stub("cpu usage"),
            ),
            "core-count": CommandNode(
                "core-count",
                description="Core and thread count",
                handler=_stub("cpu core-count"),
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
        description="Total, used, free RAM and speed",
        examples=["ram", "ram free", "ram usage"],
        handler=_stub("ram"),
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
        description="List disks, check health and space",
        examples=["disk", "disk health", "disk space", "disk list"],
        handler=_stub("disk"),
        subcommands={
            "list": CommandNode(
                "list",
                description="List all disks",
                handler=_stub("disk list"),
            ),
            "health": CommandNode(
                "health",
                description="SMART health status",
                handler=_stub("disk health"),
                requires_admin=True,
            ),
            "space": CommandNode(
                "space",
                description="Used and free space per disk",
                handler=_stub("disk space"),
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
        description="All adapters, IPs, status, gateway, DNS",
        examples=["network"],
        handler=_stub("network"),
    )


def _build_ip() -> CommandNode:
    return CommandNode(
        "ip",
        description="Show active local IP addresses",
        examples=["ip", "ip wifi", "ip ethernet", "ip public"],
        handler=_stub("ip"),
        subcommands={
            "all": CommandNode(
                "all",
                description="All active IPs",
                handler=_stub("ip all"),
            ),
            "wifi": CommandNode(
                "wifi",
                description="Wi-Fi IPv4 address",
                handler=_stub("ip wifi"),
            ),
            "ethernet": CommandNode(
                "ethernet",
                description="Ethernet IPv4 address",
                handler=_stub("ip ethernet"),
            ),
            "public": CommandNode(
                "public",
                description="Public-facing IP address",
                handler=_stub("ip public"),
            ),
            "local": CommandNode(
                "local",
                description="Local network IP",
                handler=_stub("ip local"),
            ),
        },
    )


def _build_wifi() -> CommandNode:
    return CommandNode(
        "wifi",
        description="Wi-Fi name, IP, signal strength, adapter info",
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
        subcommands={
            "process": CommandNode(
                "process",
                description="End a process by name or PID",
                arg_hint="<name or PID>",
                examples=["kill process chrome", "kill process 1234"],
                destructive=True,
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
                examples=["folder size downloads", 'folder size "My Documents"'],
                handler=_stub("folder size"),
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
                    'find file "resume" in documents',
                ],
                handler=_stub("find file"),
            ),
        },
    )


def _build_open() -> CommandNode:
    return CommandNode(
        "open",
        description="Open a folder in the file explorer",
        arg_hint="<path>",
        examples=["open downloads", "open desktop", "open documents"],
        handler=_stub("open"),
    )


def _build_list() -> CommandNode:
    return CommandNode(
        "list",
        description="List files in a folder",
        arg_hint="<path>",
        examples=["list downloads", "list desktop", "list desktop/Hardware"],
        handler=_stub("list"),
    )


def _build_copy() -> CommandNode:
    return CommandNode(
        "copy",
        description="Copy a file or folder to a destination",
        arg_hint="<source> to <destination>",
        examples=[
            "copy report.pdf to desktop",
            "copy downloads/file.zip to documents",
            "copy folder project to desktop/backup",
        ],
        handler=_stub("copy"),
    )


def _build_move() -> CommandNode:
    return CommandNode(
        "move",
        description="Move a file or folder to a destination",
        arg_hint="<source> to <destination>",
        examples=[
            "move report.pdf to documents",
            "move folder old-stuff to documents/archive",
        ],
        destructive=True,
        handler=_stub("move"),
    )


def _build_delete() -> CommandNode:
    return CommandNode(
        "delete",
        description="Delete a file, folder, or run cleanup",
        examples=[
            "delete file old.txt",
            "delete folder TargetFolder",
            "delete folder TargetFolder recursive",
            "delete temp",
            "delete empty-trash",
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
                    "delete folder TargetFolder",
                    "delete folder TargetFolder recursive",
                    "delete folder TargetFolder recursive force",
                    "delete folder TargetFolder recursive dry-run",
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
        description="Pass a command directly to the host shell (escape hatch)",
        arg_hint='"<shell command>"',
        examples=[
            'native "Get-NetIPAddress"',
            'native "dir"',
            'native "ls -la"',
        ],
        handler=_stub("native"),
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def register_all(registry: CommandRegistry) -> None:
    """Register every stub command into *registry*."""
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
    ])
