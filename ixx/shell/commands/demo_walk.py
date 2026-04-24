"""
IXX interactive demo walkthrough.

Guides the user through IXX concepts one step at a time.
Each step shows the code, waits for Enter, then runs it live.

The optional `_input_fn` parameter replaces `input()` for testing:
    handle_demo_walk([], _input_fn=lambda _: "")
"""

from __future__ import annotations

import sys
import textwrap
from typing import Callable


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
        "Assign a value with `=`. Use `{name}` inside a string to insert the value.",
        'name = "IXX"\nsay "Hello from {name}"',
    ),
    (
        "Numbers and math",
        "Numbers work as you'd expect. String `+` is concatenation.",
        'x = 10\ny = 3\nsay "Sum: " + text(x + y)\nsay "Product: " + text(x * y)',
    ),
    (
        "Conditions",
        "`if` checks a condition. The `-` block only runs when it is true.",
        'age = 20\nif age less than 18\n- say "Too young"\nelse\n- say "Old enough"',
    ),
    (
        "Lists and contains",
        "Comma-separated values make a list. `count()` gives the length.",
        'fruits = "apple", "banana", "mango"\nsay "Items: " + text(count(fruits))\nif fruits contains "banana"\n- say "Found banana"',
    ),
    (
        "Loops",
        "`loop` keeps running while the condition is true.",
        'n = 3\nloop n more than 0\n- say "Countdown: {n}"\n- n = n - 1\nsay "Done"',
    ),
    (
        "Functions",
        "Define a function with `function`. Call it by name. Multiple params use commas.",
        'function greet person\n- say "Hello, {person}!"\n\ngreet "World"\ngreet "IXX"',
    ),
    (
        "Return values",
        "Use `return` to send a value back. Expression-position calls use parentheses.",
        'function add a, b\n- return a + b\n\nresult = add(10, 7)\nsay "10 + 7 = {result}"',
    ),
    (
        "Recursion",
        "Functions can call themselves. IXX limits recursion to prevent infinite loops.",
        'function factorial n\n- if n at most 1\n-- return 1\n- sub = factorial(n - 1)\n- return n * sub\n\nsay "5! = " + text(factorial(5))',
    ),
    (
        "Built-in functions",
        "`count` `text` `number` `type` are built in. No import needed.",
        'items = "one", "two", "three"\nsay "Count: " + text(count(items))\nsay "Type of 42: " + type(42)\nsay "Number from text: " + text(number("99"))',
    ),
]


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _header(text: str) -> None:
    width = 60
    bar = "─" * width
    try:
        print(f"\n  ┌{bar}┐")
        print(f"  │  {text:<{width - 2}}│")
        print(f"  └{bar}┘")
    except UnicodeEncodeError:
        print(f"\n  === {text} ===")


def _explain(text: str) -> None:
    plain = text.replace("`", "")
    print(f"\n  {plain}\n")


def _show_code(code: str) -> None:
    try:
        print("  ┄ IXX code ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄")
        for line in code.splitlines():
            print(f"    {line}")
        print("  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄")
    except UnicodeEncodeError:
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


def _prompt_continue(
    step: int, total: int, input_fn: Callable[[str], str]
) -> bool:
    """Return False if user wants to quit."""
    try:
        ans = input_fn(
            f"\n  [{step}/{total}]  Press Enter to run  (or q to quit)  › "
        ).strip().lower()
        return ans not in ("q", "quit", "exit")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def _prompt_next(
    step: int, total: int, input_fn: Callable[[str], str]
) -> bool:
    """Return False if user wants to quit."""
    if step >= total:
        return False
    try:
        ans = input_fn(
            "  Press Enter for next  (or q to quit)  › "
        ).strip().lower()
        return ans not in ("q", "quit", "exit")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def handle_demo_walk(
    _args: list[str],
    _input_fn: Callable[[str], str] | None = None,
) -> None:
    """Run the interactive walkthrough.

    Args:
        _args:      Unused; present for shell command compatibility.
        _input_fn:  Override ``input()`` for testing.  Pass a callable that
                    accepts a prompt string and returns a response string.
    """
    if _input_fn is None:
        _input_fn = input

    total = len(_STEPS)

    print()
    print("  IXX Interactive Walkthrough")
    print("  Each step shows the code, then runs it live.")
    print("  Press Enter to advance. Type q to quit.")

    for i, (title, explanation, code) in enumerate(_STEPS, start=1):
        _header(f"{i}. {title}")
        _explain(explanation)
        _show_code(code)

        if not _prompt_continue(i, total, _input_fn):
            print("\n  Walkthrough ended.\n")
            return

        _run_snippet(code)

        if i < total:
            if not _prompt_next(i, total, _input_fn):
                print("\n  Walkthrough ended.\n")
                return

    print()
    print("  That is IXX v0.4.")
    print("  Type IXX code directly in the shell, or run a .ixx file with:")
    print("    ixx yourfile.ixx")
    print()
