"""
IXX CLI entry point.

Supported usage:
    ixx <file.ixx>            run a script (shorthand)
    ixx run <file.ixx>        run a script (explicit)
    ixx check <file.ixx>      parse only — report syntax errors, no execution
    ixx version               print the IXX version
    ixx help                  print help overview
    ixx shell                 open the interactive shell
"""

from __future__ import annotations
import sys
import os
import re
import difflib

VERSION = "0.3.0-dev"

_KNOWN_COMMANDS = ["run", "check", "version", "help", "shell", "do"]

HELP_TEXT = """
IXX - executable checklist-style code

Usage:
  ixx <file.ixx>          run a script
  ixx run <file.ixx>      run a script (explicit)
  ixx check <file.ixx>    check syntax without running
  ixx version             print the IXX version
  ixx help                show this help
  ixx                     open the IXX interactive shell
  ixx shell               open the IXX interactive shell
  ixx do "ip wifi"        run one shell command and exit

Language quick-reference:
  say "Hello World"

  name = "Ixxy"
  say "Hello, {name}"

  age = 19
  if age less than 18
  - say "Not adult"
  else
  - say "Adult"

  items = "apple", "banana", "grape"
  if items contains "banana"
  - say "Found it"

  count = 3
  loop count more than 0
  - say count
  - count = count - 1

Comparisons:  is  |  is not  |  less than  |  more than  |  at least  |  at most  |  contains
Logic:        and  |  or  |  not
Booleans:     YES  |  NO
Blocks:       - one level  |  -- two levels  |  --- three levels

Examples:
  ixx examples\\hello.ixx
  ixx run examples\\condition.ixx
  ixx check examples\\advanced.ixx
  ixx version
  ixx help
""".strip()


# ---------------------------------------------------------------------------
# Friendly token names (Lark internal names → readable labels)
# ---------------------------------------------------------------------------
_TOKEN_FRIENDLY: dict[str, str] = {
    "YES":            "yes",
    "NO":             "no",
    "IDENTIFIER":     "variable name",
    "INT":            "number",
    "FLOAT":          "number",
    "ESCAPED_STRING": 'text in quotes (e.g. "hello")',
    "LPAR":           '"("',
    "MINUS":          "number (e.g. -5)",
}

# Ordered longest-first so "is not" is checked before "is"
_INCOMPLETE_COMPARISONS: list[tuple[str, str]] = [
    ("less than", 'if age less than 18'),
    ("more than", 'if score more than 100'),
    ("at least",  'if score at least 90'),
    ("at most",   'if score at most 50'),
    ("is not",    'if name is not "Guest"'),
    ("contains",  'if items contains "apple"'),
    ("is",        'if name is "Ixxy"'),
]


def _orig_line_and_col(source: str, e: Exception) -> tuple[int | None, str | None, int | None]:
    """Return (line_number, original_source_line, adjusted_column).

    The parser runs on the preprocessed source (dashes → spaces), so
    ``e.column`` refers to that expanded layout.  We undo the expansion
    so the caret aligns with what the user actually typed.
    """
    line_num: int | None = getattr(e, "line", None)
    col: int | None = getattr(e, "column", None)
    if not line_num:
        return None, None, None

    orig_lines = source.splitlines()
    if not (1 <= line_num <= len(orig_lines)):
        return line_num, None, col

    orig_line = orig_lines[line_num - 1]

    # Dash lines: preprocessor turned "-+ \s*" into "    " * n_dashes.
    # Adjust the column back to the original coordinate.
    m = re.match(r'^(-+)\s*', orig_line)
    if m and col is not None:
        n_dashes = len(m.group(1))
        n_original_prefix = len(m.group(0))   # dashes + following spaces
        col_offset = n_dashes * 4 - n_original_prefix
        col = max(1, col - col_offset)

    return line_num, orig_line, col


def _friendly_message(orig_line: str, col: int | None, e: Exception) -> str:
    """Build a friendly 'expected' message from the error position."""
    # Text before the caret tells us what partial phrase was written
    if col and col > 0:
        text_before = orig_line[:col - 1].rstrip()
    else:
        text_before = orig_line.rstrip()

    # Detect incomplete comparison phrases (longest-first to avoid "is" matching "is not")
    for phrase, example in _INCOMPLETE_COMPARISONS:
        if text_before.endswith(phrase):
            return (
                f'Expected a value after "{phrase}".\n'
                f'  Example:  {example}'
            )

    # Convert Lark token names to friendly labels
    expected_raw = (
        getattr(e, "expected", None)
        or getattr(e, "allowed", None)
        or set()
    )
    friendly: set[str] = set()
    for tok in expected_raw:
        name = str(tok).strip("'\"")
        if name in _TOKEN_FRIENDLY:
            friendly.add(_TOKEN_FRIENDLY[name])
        # Internal / anonymous tokens are silently skipped

    if friendly:
        parts = sorted(friendly)
        if len(parts) == 1:
            return f"Expected {parts[0]}."
        if len(parts) == 2:
            return f"Expected {parts[0]} or {parts[1]}."
        return "Expected " + ", ".join(parts[:-1]) + f", or {parts[-1]}."

    return "Check the syntax around the marked position."


def _format_syntax_error(path: str, source: str, e: Exception) -> None:
    """Print a clean, human-readable syntax error."""
    line_num, orig_line, col = _orig_line_and_col(source, e)

    loc = f"line {line_num}" if line_num else ""
    print(f"ixx: syntax error in {path} {loc}\n", file=sys.stderr)

    if orig_line is not None:
        print(f"  {orig_line}", file=sys.stderr)
        if col is not None and col >= 1:
            print(f"  {' ' * (col - 1)}^", file=sys.stderr)
    else:
        # No source line available — try get_context as a fallback
        try:
            from .preprocessor import preprocess
            preprocessed = preprocess(source)
            ctx = e.get_context(preprocessed).rstrip()  # type: ignore[attr-defined]
            print(ctx, file=sys.stderr)
        except Exception:
            print(f"  {e}", file=sys.stderr)

    msg = _friendly_message(orig_line or "", col, e)
    print(f"\n{msg}", file=sys.stderr)


def _run_file(path: str, check_only: bool = False) -> None:
    if not os.path.isfile(path):
        print(f"ixx: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"ixx: cannot read file: {e}", file=sys.stderr)
        sys.exit(1)

    from lark.exceptions import UnexpectedInput
    from .parser import parse
    from .interpreter import Interpreter, IXXRuntimeError

    try:
        program = parse(source)
    except UnexpectedInput as e:
        _format_syntax_error(path, source, e)
        sys.exit(1)
    except Exception as e:
        print(f"ixx: parse error in {path}:", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        sys.exit(1)

    if check_only:
        print(f"ixx: {path} - syntax OK")
        return

    try:
        Interpreter().run(program)
    except IXXRuntimeError as e:
        print(f"ixx: runtime error in {path}", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    args = sys.argv[1:]

    if not args:
        from .shell.repl import run as _run_shell
        _run_shell()
        return

    cmd = args[0]

    # --- ixx version ---
    if cmd == "version":
        print(f"ixx {VERSION}")
        return

    # --- ixx help ---
    if cmd in ("help", "--help", "-h"):
        print(HELP_TEXT)
        return

    # --- ixx shell ---
    if cmd == "shell":
        from .shell.repl import run as _run_shell
        _run_shell()
        return

    # --- ixx do "<shell command>" ---
    if cmd == "do":
        if len(args) < 2:
            print("ixx: 'do' requires a command.  Example: ixx do \"ip wifi\"",
                  file=sys.stderr)
            sys.exit(1)
        from .shell.repl import run_command_once
        run_command_once(" ".join(args[1:]))
        return

    # --- ixx run <file> ---
    if cmd == "run":
        if len(args) < 2:
            print("ixx: 'run' requires a file path.  Example: ixx run hello.ixx",
                  file=sys.stderr)
            sys.exit(1)
        _run_file(args[1])
        return

    # --- ixx check <file> ---
    if cmd == "check":
        if len(args) < 2:
            print("ixx: 'check' requires a file path.  Example: ixx check hello.ixx",
                  file=sys.stderr)
            sys.exit(1)
        _run_file(args[1], check_only=True)
        return

    # --- ixx <file.ixx>  (shorthand run) ---
    if cmd.endswith(".ixx"):
        _run_file(cmd)
        return

    # --- unknown command: suggest close matches ---
    print(f"ixx: unknown command '{cmd}'", file=sys.stderr)
    close = difflib.get_close_matches(cmd, _KNOWN_COMMANDS, n=1, cutoff=0.6)
    if close:
        print(f"     Did you mean: ixx {close[0]}?", file=sys.stderr)
    print("     Run 'ixx help' to see available commands.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
