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

_HISTORY_FILE: str = str(__import__("pathlib").Path.home() / ".ixx_history")
_HISTORY_LENGTH: int = 500


def _setup_readline() -> None:
    """Configure readline tab-completion and persistent history.

    Loads ~/.ixx_history on startup and registers an atexit hook to save it.
    Silently skipped on systems where neither readline nor pyreadline3 is
    available (e.g. plain Windows without pyreadline3 installed).
    """
    try:
        import readline
        import atexit
        import os as _os
        readline.set_history_length(_HISTORY_LENGTH)
        if _os.path.exists(_HISTORY_FILE):
            try:
                readline.read_history_file(_HISTORY_FILE)
            except Exception:
                pass
        atexit.register(_safe_write_history)
    except ImportError:
        try:
            import pyreadline3  # noqa: F401  (Windows fallback)
        except ImportError:
            pass  # History unavailable; that's fine
    except Exception:
        pass  # Never block the REPL for history issues


def _safe_write_history() -> None:
    """Write readline history to disk; silently ignores all errors."""
    try:
        import readline
        readline.write_history_file(_HISTORY_FILE)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Block-starter helpers
# ---------------------------------------------------------------------------

# Keywords that open a new indented block in IXX.  When the REPL sees one of
# these as the first word on a line it must NOT try to parse immediately —
# the block body hasn't been typed yet.  Instead it enters continuation mode
# right away and waits for a blank line before submitting.
_BLOCK_STARTERS: frozenset[str] = frozenset({
    "if", "else", "loop", "function", "try", "catch",
})


def _is_block_start(line: str) -> bool:
    """Return True if *line* opens an IXX block (if/else/loop/function/try/catch)."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    first = stripped.split()[0].lower()
    return first in _BLOCK_STARTERS


def _is_orphan_dash(line: str) -> bool:
    """Return True if *line* starts with '-' (a block body line with no header)."""
    return line.strip().startswith("-")


# ---------------------------------------------------------------------------
# Clear-screen helper
# ---------------------------------------------------------------------------

def _handle_clear() -> None:
    """Clear the terminal screen without affecting REPL state or history."""
    import os
    try:
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")
    except Exception:
        pass  # Silent no-op if the terminal can't be cleared


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

def _tokenize_raw(line: str) -> list[tuple[str, bool]]:
    """Split *line* on whitespace, preserving quoted strings as single tokens.

    Returns a list of ``(token, was_quoted)`` pairs.  Quoted tokens retain
    their original casing so file paths on case-sensitive systems are not
    corrupted by ``_normalize``.
    """
    tokens: list[tuple[str, bool]] = []
    current: list[str] = []
    in_quote = False
    quote_char = ""

    for ch in line:
        if in_quote:
            if ch == quote_char:
                in_quote = False
                tokens.append(("".join(current), True))
                current = []
            else:
                current.append(ch)
        elif ch in ('"', "'"):
            in_quote = True
            quote_char = ch
        elif ch in (" ", "\t"):
            if current:
                tokens.append(("".join(current), False))
                current = []
        else:
            current.append(ch)

    if current:
        tokens.append(("".join(current), False))

    return tokens


def _tokenize(line: str) -> list[str]:
    """Public tokeniser — returns a flat list of string tokens.

    Quoted strings are preserved as single tokens (without their surrounding
    quotes), and unquoted tokens are returned as-is.  Callers that need to
    distinguish quoted from unquoted tokens should use ``_tokenize_raw``.
    """
    return [tok for tok, _ in _tokenize_raw(line)]


def _normalize(raw_tokens: list[tuple[str, bool]]) -> list[str]:
    """Lowercase command (unquoted) tokens; preserve casing of quoted strings.

    Command keywords are always lowercase in the registry.  Quoted string
    arguments (e.g. file paths passed to ``open``/``copy``/``move``) must
    retain their original casing for case-sensitive file systems (Linux/macOS).
    """
    return [tok if was_quoted else tok.lower() for tok, was_quoted in raw_tokens]


# ---------------------------------------------------------------------------
# Meta-command helpers
# ---------------------------------------------------------------------------

def _handle_update() -> None:
    """Handle the 'update' meta-command: run pip install --upgrade ixx."""
    import subprocess
    from .renderer import show_success, show_error
    print()
    print("  Checking for the latest IXX version...\n", flush=True)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "ixx"],
            capture_output=False,
        )
        print()
        if result.returncode == 0:
            show_success("Update complete. Restart ixx to use the new version.")
        else:
            show_error("pip exited with an error. Try: pip install --upgrade ixx")
    except Exception as exc:
        show_error(f"Could not run pip: {exc}")
    print()


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


def _try_run_ixx(first_line: str, prompt_fn, interpreter=None) -> bool:
    """
    Attempt to parse and run *first_line* (and any continuation lines) as IXX.

    If *interpreter* is provided it is reused (persistent REPL session state).
    Otherwise a fresh Interpreter is created (one-shot fallback).

    Returns True if the input was recognised as IXX (even if it errored).
    Returns False if it definitely is not IXX (so caller can show "unknown command").

    Block-starter detection:
      Lines that open an IXX block (if/else/loop/function/try/catch) enter
      continuation mode immediately — we do NOT try to parse just the header,
      because the grammar requires a body and raises UnexpectedInput (not
      UnexpectedEOF) for a bare header.  Continuation lines are collected until
      the user types a blank line, then the full source is parsed and executed.

    Orphan dash guard:
      A line starting with '-' outside of continuation mode is a block body
      line with no header.  We show a friendly error instead of letting it
      execute unconditionally.
    """
    import os
    from ..parser import parse
    from ..interpreter import Interpreter, IXXRuntimeError
    from ..modules import resolve_imports, IXXImportError
    from lark.exceptions import UnexpectedInput, UnexpectedEOF

    # Builtin call-statement names that are also valid IXX statement starters.
    # Without this set they would fall through to "unknown shell command".
    _IXX_STARTERS = {
        "say", "if", "else", "loop", "not",
        "function", "try", "use", "return", "catch",
        # builtin call statements (U2)
        "write", "read", "readlines", "append", "exists",
        "do", "ask", "color",
    }

    def _run_program(program) -> None:
        imported = resolve_imports(program, os.getcwd())
        if interpreter is not None:
            interpreter.run_repl_input(program, imported)
        else:
            Interpreter().run(program, imported)

    # ------------------------------------------------------------------
    # Orphan dash guard: a body line with no header must not run alone.
    # ------------------------------------------------------------------
    if _is_orphan_dash(first_line):
        print("  ixx: This line starts with '-' but there is no block to attach it to.")
        return True  # handled — don't fall through to "unknown command"

    lines = [first_line]
    stripped = first_line.strip()
    first_token = stripped.split()[0].lower() if stripped else ""

    # ------------------------------------------------------------------
    # Block-starter: collect all body lines before attempting to parse.
    # Relying on UnexpectedEOF is wrong for block headers — the parser
    # raises UnexpectedInput for a bare header like "if x more than 10".
    # ------------------------------------------------------------------
    if first_token in _BLOCK_STARTERS:
        while True:
            try:
                cont = prompt_fn("... ")
            except (EOFError, KeyboardInterrupt):
                print()
                return True
            if cont.strip() == "":
                break  # blank line → done collecting; fall through to parse
            lines.append(cont)
        # Fall through to the parse/execute loop with the full block source.

    # ------------------------------------------------------------------
    # Parse / execute loop (also handles UnexpectedEOF for nested blocks).
    # ------------------------------------------------------------------
    while True:
        source = "\n".join(lines)
        try:
            program = parse(source)
            try:
                _run_program(program)
            except IXXImportError as e:
                from .renderer import _c, _RED, _ANSI
                label = _c(_RED, "Import error") if _ANSI else "Import error"
                print(f"\n  {label}: {e}\n")
            except IXXRuntimeError as e:
                from .renderer import _c, _RED, _ANSI
                label = _c(_RED, "Error") if _ANSI else "Error"
                print(f"\n  {label}: {e}\n")
            return True
        except UnexpectedEOF:
            # Still incomplete after collecting (e.g. nested block needs more).
            try:
                cont = prompt_fn("... ")
            except (EOFError, KeyboardInterrupt):
                print()
                return True
            if cont.strip() == "":
                # Blank line after incomplete source — show friendly error.
                try:
                    program = parse(source)
                    _run_program(program)
                except IXXRuntimeError as e:
                    from .renderer import _c, _RED, _ANSI
                    label = _c(_RED, "Error") if _ANSI else "Error"
                    print(f"\n  {label}: {e}\n")
                except Exception:
                    print("  ixx: syntax error — check your code")
                return True
            lines.append(cont)
        except UnexpectedInput:
            # Definite parse error — report as IXX only when the first token
            # looks like IXX syntax, not a shell command typo.
            is_assignment = "=" in first_line and not first_line.strip().startswith("#")
            if first_token in _IXX_STARTERS or is_assignment:
                print("  ixx: syntax error — check your code")
                return True
            return False
        except Exception as e:
            print(f"  ixx: error: {e}")
            return True


def _dispatch(registry: CommandRegistry, tokens: list[str],
               raw_line: str = "", prompt_fn=None, interpreter=None) -> None:
    """Core dispatch logic shared by run() and run_command_once()."""
    result = get_guidance(registry, tokens)

    if result.matched_node is None:
        # Try running the raw input as IXX before giving up
        if raw_line and prompt_fn and _try_run_ixx(raw_line, prompt_fn, interpreter):
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

    # One persistent interpreter for the entire session (U1).
    from ..interpreter import Interpreter as _Interpreter
    _session_interp = _Interpreter()

    while True:
        try:
            raw = input(PROMPT)
        except (EOFError, KeyboardInterrupt):
            # Ctrl-D / Ctrl-C gracefully exits
            print()
            break

        line = raw.strip()
        if not line:
            continue

        tokens = apply_aliases(_normalize(_tokenize_raw(line)))
        first = tokens[0]

        # ---- exit / quit ----
        if first in ("exit", "quit"):
            print("\nGoodbye.\n")
            break

        # ---- clear / cls ----
        if first in ("clear", "cls"):
            _handle_clear()
            continue

        # ---- update ----
        if first == "update":
            _handle_update()
            continue

        # ---- showoff ----
        if first == "showoff":
            from ..showoff import run as _showoff_run
            sub = tokens[1] if len(tokens) > 1 else "default"
            if sub not in ("default", "quick", "full", "plain"):
                sub = "default"
            _showoff_run(sub)
            continue

        # ---- help / ? ----
        if first in ("help", "?") or (len(tokens) >= 2 and tokens[-1] in ("?", "help")):
            _handle_help(registry, tokens)
            continue

        _dispatch(registry, tokens, raw_line=line, prompt_fn=input,
                  interpreter=_session_interp)
# ---------------------------------------------------------------------------

def run_command_once(line: str) -> None:
    """Build the registry, dispatch *line* as a single command, then return.

    Used by ``ixx do "ip wifi"`` — no banner, no loop.
    """
    _utf8_stdout()
    registry = _make_registry()
    tokens = apply_aliases(_normalize(_tokenize_raw(line.strip())))
    if not tokens:
        return

    first = tokens[0]

    # Help / ? passthrough
    if first in ("help", "?") or (len(tokens) >= 2 and tokens[-1] in ("?", "help")):
        _handle_help(registry, tokens)
        return

    _dispatch(registry, tokens)


def run_command_capture(line: str) -> str:
    """Run a shell command and return its output as a string instead of printing.

    Used by the ``do()`` built-in.  Raises IXXRuntimeError for unknown,
    incomplete, not-implemented, or erroring commands.
    """
    import io
    import contextlib
    from ..runtime.errors import IXXRuntimeError

    registry = _make_registry()
    tokens = apply_aliases(_normalize(_tokenize_raw(line.strip())))

    if not tokens:
        raise IXXRuntimeError("do() received an empty command.")

    result = get_guidance(registry, tokens)

    if result.matched_node is None:
        suggestions = registry.suggest(tokens[0])
        hint = f"  Did you mean: {suggestions[0]}?" if suggestions else ""
        raise IXXRuntimeError(
            f"Unknown shell command: '{line}'.{hint}\n"
            "  Run 'ixx help' to see available commands."
        )

    if not result.is_executable:
        node = result.matched_node
        example = node.examples[0] if node.examples else "see ixx help"
        raise IXXRuntimeError(
            f"'{line}' is an incomplete command.  Example: {example}"
        )

    node = result.matched_node

    if result.remaining_args and node.subcommands:
        unknown_sub = result.remaining_args[0]
        raise IXXRuntimeError(
            f"Unknown subcommand '{unknown_sub}' for '{tokens[0]}'.\n"
            f"  Run 'ixx help {tokens[0]}' to see valid options."
        )

    if node.handler is None:
        raise IXXRuntimeError(f"'{line}' is not yet implemented.")

    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            node.handler(result.remaining_args)
    except Exception as exc:
        raise IXXRuntimeError(f"Shell command '{line}' failed: {exc}") from exc

    return buf.getvalue().strip()

