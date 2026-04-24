"""
IXX Shell — REPL

The main interactive loop.  Call run() to start the shell.

Responsibilities:
- Print the welcome banner.
- Read a line of input.
- Tokenize it.
- Handle built-in meta-commands (exit, quit, help, ?, command ?).
- Ask the guidance engine what the tokens mean.
- If executable: dispatch to the handler.
- If incomplete: show hints via the renderer.
- If unknown: fuzzy-suggest and show an error.
- Maintain command history via readline (or pyreadline3 on Windows).
"""

from __future__ import annotations

import sys

from .commands.stubs import register_all
from .guidance import get_guidance
from .registry import CommandRegistry
from .renderer import (
    show_help,
    show_hints,
    show_not_implemented,
    show_top_level,
    show_unknown,
)

PROMPT = "ixx> "
VERSION = "0.3.0-dev"

# ---------------------------------------------------------------------------
# Readline / history (best-effort; silently skipped if unavailable)
# ---------------------------------------------------------------------------

def _setup_readline() -> None:
    try:
        import readline  # noqa: F401  (Unix)
    except ImportError:
        try:
            import pyreadline3  # noqa: F401  (Windows)
        except ImportError:
            pass  # History just won't work; that's fine


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

def _tokenize(line: str) -> list[str]:
    """Split on whitespace, preserving quoted strings as single tokens."""
    tokens: list[str] = []
    current: list[str] = []
    in_quote = False
    quote_char = ""

    for ch in line:
        if in_quote:
            if ch == quote_char:
                in_quote = False
                tokens.append("".join(current))
                current = []
            else:
                current.append(ch)
        elif ch in ('"', "'"):
            in_quote = True
            quote_char = ch
        elif ch in (" ", "\t"):
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(ch)

    if current:
        tokens.append("".join(current))

    return tokens


# ---------------------------------------------------------------------------
# Meta-command helpers
# ---------------------------------------------------------------------------

def _handle_help(registry: CommandRegistry, tokens: list[str]) -> None:
    """Handle: help  |  help <cmd>  |  ? <cmd>  |  <cmd> ?  |  <cmd> help"""
    # "help" alone
    if len(tokens) <= 1:
        show_help(registry)
        return

    # "help <cmd>" or "? <cmd>"  →  topic is second token
    # "<cmd> ?"   or "<cmd> help" →  topic is first token
    topic = tokens[1] if tokens[0] in ("help", "?") else tokens[0]
    show_help(registry, topic)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def _utf8_stdout() -> None:
    """On Windows, reconfigure stdout/stderr to UTF-8 so Unicode output works."""
    if sys.platform == "win32":
        import io
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
        except Exception:
            pass


def _make_registry() -> CommandRegistry:
    registry = CommandRegistry()
    register_all(registry)
    return registry


def run() -> None:
    """Start the IXX interactive shell."""
    _utf8_stdout()
    _setup_readline()
    registry = _make_registry()

    print(f"\nIXX Shell  {VERSION}")
    print("Type a command to get started, or 'help' for a list.")
    print("Type 'exit' to leave.\n")

    while True:
        try:
            raw = input(PROMPT)
        except (EOFError, KeyboardInterrupt):
            # Ctrl-D / Ctrl-C gracefully exits
            print()
            break

        line = raw.strip()
        if not line:
            # Empty Enter — show top-level commands as a nudge
            show_top_level(registry)
            continue

        tokens = _tokenize(line)
        first = tokens[0].lower()

        # ---- exit / quit ----
        if first in ("exit", "quit"):
            print("\nGoodbye.\n")
            break

        # ---- help / ? ----
        if first in ("help", "?") or (len(tokens) >= 2 and tokens[-1] in ("?", "help")):
            _handle_help(registry, tokens)
            continue

        # ---- guidance lookup ----
        result = get_guidance(registry, tokens)

        if result.matched_node is None:
            # Completely unknown first word
            suggestions = registry.suggest(first)
            show_unknown(first, suggestions)
            continue

        if result.is_executable:
            node = result.matched_node
            if node.handler is not None:
                node.handler(result.remaining_args)
            else:
                # Node matched but handler is None — show stub message
                path = " ".join(tokens[:result.depth])
                show_not_implemented(path)
        else:
            # Matched a node but not yet at an executable point — show hints
            show_hints(result)


# ---------------------------------------------------------------------------
# Single-command dispatch  (used by ixx do "...")
# ---------------------------------------------------------------------------

def run_command_once(line: str) -> None:
    """Build the registry, dispatch *line* as a single command, then return.

    Used by ``ixx do "ip wifi"`` — no banner, no loop.
    """
    _utf8_stdout()
    registry = _make_registry()
    tokens = _tokenize(line.strip())
    if not tokens:
        return

    first = tokens[0].lower()

    # Help / ? passthrough
    if first in ("help", "?") or (len(tokens) >= 2 and tokens[-1] in ("?", "help")):
        _handle_help(registry, tokens)
        return

    result = get_guidance(registry, tokens)

    if result.matched_node is None:
        suggestions = registry.suggest(first)
        show_unknown(first, suggestions)
        return

    if result.is_executable:
        node = result.matched_node
        if node.handler is not None:
            node.handler(result.remaining_args)
        else:
            path = " ".join(tokens[:result.depth])
            show_not_implemented(path)
    else:
        show_hints(result)
