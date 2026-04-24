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

import difflib
import sys

from .commands.stubs import register_all
from .guidance import get_guidance
from .registry import CommandRegistry
from .aliases import apply_aliases
from .renderer import (
    show_banner,
    show_help,
    show_hints,
    show_not_implemented,
    show_top_level,
    show_unknown,
    show_unknown_subcommand,
)

PROMPT = "ixx> "
from .._version import VERSION

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


def _normalize(tokens: list[str]) -> list[str]:
    """Lowercase all tokens so commands are case-insensitive.

    Quoted path arguments (free-form strings the user typed) must preserve
    their case, but command keywords are always lowercase in the registry.
    We lowercase everything — path resolution handles case sensitivity at the
    OS level, and quoted strings that reach handlers are reconstructed from
    the original line anyway.
    """
    return [t.lower() for t in tokens]


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


def _try_run_ixx(first_line: str, prompt_fn) -> bool:
    """
    Attempt to parse and run *first_line* (and any continuation lines) as IXX.
    Returns True if the input was recognised as IXX (even if it errored).
    Returns False if it definitely is not IXX (so the caller can show "unknown command").
    """
    from ..parser import parse
    from ..interpreter import Interpreter, IXXRuntimeError
    from ..preprocessor import preprocess
    from lark.exceptions import UnexpectedInput, UnexpectedEOF

    lines = [first_line]

    # Try parsing with increasing number of lines (continuation loop)
    while True:
        source = "\n".join(lines)
        try:
            program = parse(source)
            # Parsed OK — run it
            try:
                Interpreter().run(program)
            except IXXRuntimeError as e:
                print(f"  runtime error: {e}")
            return True
        except UnexpectedEOF:
            # Incomplete — ask for more input
            try:
                cont = prompt_fn("... ")
            except (EOFError, KeyboardInterrupt):
                print()
                return True
            if cont.strip() == "":
                # Blank line — give up continuing, try to run what we have
                try:
                    program = parse(source)
                    Interpreter().run(program)
                except Exception:
                    pass
                return True
            lines.append(cont)
        except UnexpectedInput:
            # Definite parse error — but only report it as IXX if the first
            # token looks like IXX syntax, not a shell command typo.
            ixx_starters = {
                "say", "if", "else", "loop", "not",
            }
            first_token = first_line.strip().split()[0].lower() if first_line.strip() else ""
            is_assignment = "=" in first_line and not first_line.strip().startswith("#")
            if first_token in ixx_starters or is_assignment:
                # Looks like IXX — report the error
                print(f"  ixx: syntax error — check your code")
                return True
            # Looks like a mistyped shell command
            return False
        except Exception as e:
            print(f"  ixx: error: {e}")
            return True


def _dispatch(registry: CommandRegistry, tokens: list[str],
               raw_line: str = "", prompt_fn=None) -> None:
    """Core dispatch logic shared by run() and run_command_once()."""
    result = get_guidance(registry, tokens)

    if result.matched_node is None:
        # Try running the raw input as IXX before giving up
        if raw_line and prompt_fn and _try_run_ixx(raw_line, prompt_fn):
            return
        suggestions = registry.suggest(tokens[0])
        show_unknown(tokens[0], suggestions)
        return

    if result.is_executable:
        node = result.matched_node
        if result.remaining_args and node.subcommands:
            # Token after parent didn't match any subcommand — not free-form args
            unknown_sub = result.remaining_args[0]
            sub_keys = list(node.subcommands.keys())
            # Prefer prefix match (e.g. "temp" → "temperature") over difflib only
            prefix_matches = [k for k in sub_keys if k.startswith(unknown_sub)]
            if len(prefix_matches) == 1:
                suggestions = prefix_matches
            else:
                suggestions = difflib.get_close_matches(
                    unknown_sub, sub_keys, n=1, cutoff=0.6
                )
            show_unknown_subcommand(
                " ".join(tokens[:result.depth]), unknown_sub, suggestions
            )
        elif node.handler is not None:
            node.handler(result.remaining_args)
        else:
            show_not_implemented(" ".join(tokens[:result.depth]))
    else:
        show_hints(result)


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

    show_banner(VERSION)

    # Show update notice directly after banner if one is pending
    from ..update_check import notify as _uc_notify
    _uc_notify(VERSION, indent="")

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

        tokens = apply_aliases(_normalize(_tokenize(line)))
        first = tokens[0]

        # ---- exit / quit ----
        if first in ("exit", "quit"):
            print("\nGoodbye.\n")
            break

        # ---- help / ? ----
        if first in ("help", "?") or (len(tokens) >= 2 and tokens[-1] in ("?", "help")):
            _handle_help(registry, tokens)
            continue

        _dispatch(registry, tokens, raw_line=line, prompt_fn=input)
# ---------------------------------------------------------------------------

def run_command_once(line: str) -> None:
    """Build the registry, dispatch *line* as a single command, then return.

    Used by ``ixx do "ip wifi"`` — no banner, no loop.
    """
    _utf8_stdout()
    registry = _make_registry()
    tokens = apply_aliases(_normalize(_tokenize(line.strip())))
    if not tokens:
        return

    first = tokens[0]

    # Help / ? passthrough
    if first in ("help", "?") or (len(tokens) >= 2 and tokens[-1] in ("?", "help")):
        _handle_help(registry, tokens)
        return

    _dispatch(registry, tokens)
