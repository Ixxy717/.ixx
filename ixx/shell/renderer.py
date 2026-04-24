"""
IXX Shell — Renderer

All output formatting lives here.  The REPL calls these functions; it
never formats strings itself.  This makes it easy to later swap in a
richer terminal library without touching the core logic.
"""

from __future__ import annotations

from .guidance import GuidanceResult
from .registry import CommandNode, CommandRegistry

import os
import sys

_BOLD   = "\033[1m"
_DIM    = "\033[2m"
_YELLOW = "\033[33m"
_CYAN   = "\033[36m"
_RED    = "\033[31m"
_RESET  = "\033[0m"


def _enable_ansi() -> bool:
    """Return True if ANSI escape codes will render correctly.

    On Windows, Virtual Terminal Processing must be explicitly enabled via
    SetConsoleMode.  On any other OS, isatty() is sufficient.
    """
    if not sys.stdout.isatty():
        return False
    if os.name == "nt":
        try:
            import ctypes
            import ctypes.wintypes
            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.wintypes.DWORD()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
            return True
        except Exception:
            return False
    return True


_ANSI = _enable_ansi()


def _c(code: str, text: str) -> str:
    """Apply ANSI code only when the terminal supports it."""
    if _ANSI:
        return f"{code}{text}{_RESET}"
    return text


# ---------------------------------------------------------------------------
# Guidance / hints
# ---------------------------------------------------------------------------

def show_hints(result: GuidanceResult) -> None:
    """Print what the user can type next."""
    if result.next_options:
        print()
        for opt in result.next_options:
            node = result.matched_node
            desc = ""
            if node and opt in node.subcommands:
                desc = node.subcommands[opt].description
            if desc:
                print(f"  {_c(_CYAN, opt):<22}  {_c(_DIM, desc)}")
            else:
                print(f"  {_c(_CYAN, opt)}")

    if result.arg_hint:
        print(f"\n  {_c(_DIM, result.arg_hint)}")

    if result.examples:
        print(f"\n  {_c(_DIM, 'Examples:')}")
        for ex in result.examples:
            print(f"    {ex}")

    if result.destructive:
        node = result.matched_node
        text = (node.warning_text if node and node.warning_text
                else "this command can delete or modify files.")
        print(f"\n  {_c(_YELLOW, f'Warning: {text}')}")

    if result.requires_admin:
        print(f"  {_c(_YELLOW, 'Note: may require administrator / root privileges.')}")

    print()


def show_top_level(registry: CommandRegistry) -> None:
    """Print all top-level commands — used when the user types just Enter."""
    print()
    for node in sorted(registry.all_nodes(), key=lambda n: n.name):
        if node.description:
            print(f"  {_c(_CYAN, node.name):<22}  {_c(_DIM, node.description)}")
        else:
            print(f"  {_c(_CYAN, node.name)}")
    print()


# ---------------------------------------------------------------------------
# Help system
# ---------------------------------------------------------------------------

def show_help(registry: CommandRegistry, topic: str | None = None) -> None:
    """Print help for a topic, or broad category help if topic is None."""
    if topic is None:
        _show_broad_help(registry)
        return

    node = registry.get(topic)
    if node is None:
        print(f"\n  No help found for '{topic}'.")
        print(f"  Try: {_c(_CYAN, 'help')} for a full list.\n")
        return

    _show_node_help(node)


def _show_broad_help(registry: CommandRegistry) -> None:
    print()
    print(_c(_BOLD, "IXX Shell commands"))
    print()
    for node in sorted(registry.all_nodes(), key=lambda n: n.name):
        if node.name in ("exit", "quit", "help"):
            continue
        desc = node.description or ""
        print(f"  {_c(_CYAN, node.name):<22}  {desc}")
    print()
    print(_c(_DIM, "  Type a command name to see valid next options."))
    print(_c(_DIM, "  Type 'help <command>' for details."))
    print(_c(_DIM, "  Type 'exit' or 'quit' to leave the shell."))
    print()
    print(_c(_DIM, "  Examples:"))
    _BROAD_EXAMPLES = [
        "ip",
        "ip wifi",
        "cpu",
        "cpu core-count",
        "disk health",
        "folder size downloads",
        "open desktop",
        'find file "invoice"',
        "copy report.pdf to desktop",
        "delete folder old-stuff recursive",
    ]
    for ex in _BROAD_EXAMPLES:
        print(f"    {ex}")
    print()


def _show_node_help(node: CommandNode) -> None:
    print()
    print(_c(_BOLD, f"  {node.name}") + (f"  -  {node.description}" if node.description else ""))
    print()

    if node.subcommands:
        print("  Subcommands:")
        for name, child in node.subcommands.items():
            desc = f"  {_c(_DIM, child.description)}" if child.description else ""
            print(f"    {_c(_CYAN, name)}{desc}")
        print()

    if node.arg_hint:
        print(f"  Arguments:  {node.arg_hint}")
        print()

    if node.examples:
        print("  Examples:")
        for ex in node.examples:
            print(f"    {ex}")
        print()

    if node.destructive:
        text = node.warning_text or "destructive — will prompt before acting."
        print(_c(_YELLOW, f"  Warning: {text}"))
        print()

    if node.requires_admin:
        print(_c(_YELLOW, "  Note: may require administrator privileges."))
        print()


# ---------------------------------------------------------------------------
# Errors and suggestions
# ---------------------------------------------------------------------------

def show_unknown(word: str, suggestions: list[str]) -> None:
    """Print an unknown-command message with optional fuzzy suggestions."""
    print(f"\n  Unknown command: {_c(_BOLD, word)}")
    if suggestions:
        if len(suggestions) == 1:
            print(f"  Did you mean:    {_c(_CYAN, suggestions[0])}?")
        else:
            opts = "  |  ".join(_c(_CYAN, s) for s in suggestions)
            print(f"  Did you mean:    {opts}?")
    else:
        print(f"  Type {_c(_CYAN, 'help')} to see available commands.")
    print()


def show_not_implemented(command_path: str, note: str = "planned for a future release") -> None:
    """Print the standard stub message for commands not yet wired up."""
    print(f"\n  [{_c(_DIM, f'{command_path}  -  not yet implemented, {note}')}]\n")


def show_destructive_prompt(description: str) -> bool:
    """Print a safety confirmation and return True if the user confirms."""
    print(f"\n  {_c(_YELLOW, 'About to')} {description}")
    print(f"  {_c(_YELLOW, 'Continue?')} ", end="", flush=True)
    try:
        answer = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("yes", "y")
