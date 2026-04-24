"""
IXX interactive demo walkthrough.

Guides the user through IXX concepts one step at a time.
Each step shows the code, waits for Enter, then runs it live.
"""

from __future__ import annotations

import sys
import textwrap


# ---------------------------------------------------------------------------
# Each step: (title, explanation, ixx_code)
# ---------------------------------------------------------------------------

_STEPS: list[tuple[str, str, str]] = [
    (
        "Hello World",
        "The simplest IXX program. `say` prints a line.",
        'say "Hello, World!"',
    ),
    (
        "Variables",
        "Assign a value with `=`. Use `{name}` to drop it into a string.",
        'name = "IXX"\nsay "Hello from {name}"',
    ),
    (
        "Numbers and math",
        "Numbers work as you would expect. Assign results to variables, then say them.",
        'x = 10\ny = 3\nsum = x + y\nproduct = x * y\nsay "Sum: {sum}"\nsay "Product: {product}"',
    ),
    (
        "Conditions",
        "`if` checks a condition. The `-` block only runs when it is true.",
        'age = 20\nif age less than 18\n- say "Too young"\nelse\n- say "Old enough"',
    ),
    (
        "Comparisons",
        "IXX reads like English. All comparison keywords work together.",
        'score = 85\nif score at least 90\n- say "A grade"\nif score at least 80\n- say "B grade"',
    ),
    (
        "Booleans",
        "Use YES and NO instead of true/false.",
        'ready = YES\nif ready is YES\n- say "Let\'s go"\nif ready is NO\n- say "Not ready"',
    ),
    (
        "Logic: and / or / not",
        "Combine conditions with plain English.",
        'x = 15\nif x more than 10 and x less than 20\n- say "x is between 10 and 20"',
    ),
    (
        "Loops",
        "`loop` keeps running while the condition is true.",
        'n = 3\nloop n more than 0\n- say "Countdown: {n}"\n- n = n - 1\nsay "Done"',
    ),
    (
        "Lists and contains",
        "Use comma-separated values to build a list. Use `contains` to check membership.",
        'fruits = "apple", "banana", "mango"\nif fruits contains "banana"\n- say "Found banana"\nif fruits contains "grape"\n- say "Found grape"\nelse\n- say "No grape"',
    ),
    (
        "Nested blocks",
        "Use `--` for a second level of nesting inside a block.",
        'x = 12\nif x more than 5\n- say "x is big"\n- if x less than 20\n-- say "and less than 20"',
    ),
]


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _clear_line() -> None:
    print()


def _header(text: str) -> None:
    width = min(60, 80)
    bar = "─" * width
    try:
        print(f"\n  ┌{bar}┐")
        print(f"  │  {text:<{width - 2}}│")
        print(f"  └{bar}┘")
    except UnicodeEncodeError:
        print(f"\n  === {text} ===")


def _explain(text: str) -> None:
    # Strip inline backticks for plain output
    plain = text.replace("`", "")
    print(f"\n  {plain}\n")


def _show_code(code: str) -> None:
    print("  ┄ IXX code ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄")
    for line in code.splitlines():
        print(f"    {line}")
    print("  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄")


def _show_code_ascii(code: str) -> None:
    print("  -- IXX code ------------------------------------------")
    for line in code.splitlines():
        print(f"    {line}")
    print("  -------------------------------------------------------")


def _run_snippet(code: str) -> None:
    from ...parser import parse
    from ...interpreter import Interpreter, IXXRuntimeError
    from lark.exceptions import UnexpectedInput

    print("\n  Output:")
    print("  ·" * 27)
    try:
        program = parse(code)
        Interpreter().run(program)
    except UnexpectedInput as e:
        print(f"  (syntax error: {e})")
    except IXXRuntimeError as e:
        print(f"  (runtime error: {e})")
    print("  ·" * 27)


def _prompt_continue(step: int, total: int) -> bool:
    """Return False if user wants to quit."""
    try:
        ans = input(f"\n  [{step}/{total}]  Press Enter to run  (or q to quit)  › ").strip().lower()
        return ans not in ("q", "quit", "exit")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def _prompt_next(step: int, total: int) -> bool:
    """Return False if user wants to quit."""
    if step >= total:
        return False
    try:
        ans = input("  Press Enter for next  (or q to quit)  › ").strip().lower()
        return ans not in ("q", "quit", "exit")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def handle_demo_walk(_args: list[str]) -> None:
    _use_unicode = not (
        sys.stdout.encoding and sys.stdout.encoding.lower().startswith("cp")
    )

    total = len(_STEPS)

    print()
    print("  IXX Interactive Walkthrough")
    print("  Each step shows the code, then runs it live.")
    print("  Press Enter to run each step. Type q to quit.")

    for i, (title, explanation, code) in enumerate(_STEPS, start=1):
        _header(f"{i}. {title}")
        _explain(explanation)

        if _use_unicode:
            _show_code(code)
        else:
            _show_code_ascii(code)

        if not _prompt_continue(i, total):
            print("\n  Walkthrough ended.\n")
            return

        _run_snippet(code)

        if i < total:
            if not _prompt_next(i, total):
                print("\n  Walkthrough ended.\n")
                return

    print()
    print("  That is IXX.")
    print("  Type IXX code directly here in the shell, or run a .ixx file with:")
    print("    ixx yourfile.ixx")
    print()
