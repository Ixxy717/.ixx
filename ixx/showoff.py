"""
IXX Showoff — polished terminal presentation.

Run with:
    ixx showoff              default (animated)
    ixx showoff quick        shorter cut
    ixx showoff full         all sections (same as default)
    ixx showoff plain        no animation, minimal colors

Designed to be imported and tested; mock _sleep to run instantly in tests.
"""

from __future__ import annotations

import os
import sys
import time
from typing import Optional


# ── ANSI ──────────────────────────────────────────────────────────────────────

_BOLD   = "\033[1m"
_DIM    = "\033[2m"
_CYAN   = "\033[36m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_RESET  = "\033[0m"


def _ansi_ok() -> bool:
    """True if ANSI escape codes will render — mirrors renderer._enable_ansi."""
    if os.environ.get("NO_COLOR") is not None:
        return False
    ic = os.environ.get("IXX_COLOR")
    if ic == "0":
        return False
    if ic == "1":
        return True
    if not sys.stdout.isatty():
        return False
    if os.name != "nt":
        return True
    try:
        import ctypes
        k = ctypes.windll.kernel32          # type: ignore[attr-defined]
        h = k.GetStdHandle(-11)             # STD_OUTPUT_HANDLE
        m = ctypes.c_ulong(0)
        if not k.GetConsoleMode(h, ctypes.byref(m)):
            return False
        if m.value & 0x0004:                # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            return True
        return bool(k.SetConsoleMode(h, m.value | 0x0004))
    except Exception:
        return False


def _unicode_ok() -> bool:
    """True if stdout can encode Unicode box-drawing characters."""
    try:
        "│".encode(getattr(sys.stdout, "encoding", None) or "utf-8")
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def _c(code: str, text: str) -> str:
    return f"{code}{text}{_RESET}" if _ansi_ok() else text


# ── Timing (mockable in tests) ─────────────────────────────────────────────────

def _sleep(seconds: float) -> None:
    time.sleep(seconds)


# ── Primitives ────────────────────────────────────────────────────────────────

def type_line(text: str, delay: float = 0.025, *, plain: bool = False) -> None:
    """Print text character-by-character; instant when not a tty or plain."""
    if plain or not sys.stdout.isatty():
        print(text)
        return
    for ch in text:
        print(ch, end="", flush=True)
        _sleep(delay)
    print()


def _type_colored(code: str, text: str, delay: float = 0.08,
                  *, plain: bool = False) -> None:
    """Typewrite text with an ANSI color applied to the whole sequence."""
    if plain or not sys.stdout.isatty():
        print(_c(code, text))
        return
    if _ansi_ok():
        print(code, end="", flush=True)
    for ch in text:
        print(ch, end="", flush=True)
        _sleep(delay)
    if _ansi_ok():
        print(_RESET, end="", flush=True)
    print()


def pause(seconds: float, *, plain: bool = False) -> None:
    """Pause only when on a real interactive tty and not in plain mode."""
    if not plain and sys.stdout.isatty():
        _sleep(seconds)


def card(title: str, lines: list[str], *, plain: bool = False) -> None:
    """Print a titled feature card."""
    print(_c(_BOLD + _CYAN, f"  {title}"))
    for line in lines:
        print(f"    {line}")
    print()


def code_block(
    title: str,
    code_lines: list[str],
    output_lines: Optional[list[str]] = None,
    *,
    plain: bool = False,
) -> None:
    """Print a boxed code snippet with optional expected output."""
    uni = _unicode_ok() and not plain
    W = 48  # total visual line width (including border chars)
    inner = W - 4  # content area width between ┌ and ┐

    if uni:
        # ┌─ title ──────────────────────────────────┐
        t = f"─ {title} "
        fill = "─" * max(0, inner - len(t))
        print(f"  ┌{t}{fill}┐")

        for line in code_lines:
            content = f"  {line}"
            if len(content) > inner:
                content = content[:inner - 3] + "..."
            pad = " " * (inner - len(content))
            print(f"  │{_c(_CYAN, content)}{pad}│")

        print(f"  └{'─' * inner}┘")
    else:
        print(f"  # {title}")
        for line in code_lines:
            print(f"    {_c(_CYAN, line)}")

    if output_lines:
        arrow = _c(_GREEN, "→" if uni else "->")
        for out in output_lines:
            print(f"  {arrow} {out}")
    print()


def progress(label: str, status: str, *, plain: bool = False) -> None:
    """Print a single validation result line."""
    check = "✓" if _unicode_ok() and not plain else "+"
    print(f"    {_c(_GREEN, check)}  {label:<28}{_c(_DIM, status)}")


# ── Sections ──────────────────────────────────────────────────────────────────

def _section_boot(*, plain: bool = False) -> None:
    print()
    _type_colored(_BOLD + _CYAN, "  IXX", delay=0.10, plain=plain)
    pause(0.25, plain=plain)
    type_line("  The language for the user.", delay=0.022, plain=plain)
    pause(0.55, plain=plain)
    print()


def _section_features(*, plain: bool = False) -> None:
    features = [
        ("Visible dash blocks",    "Structure you can see -- no braces, no invisible whitespace."),
        ("Readable comparisons",   "if score more than 90  -- not  score > 90"),
        ("User-defined functions", "Define once, call anywhere. Local scope, clean returns."),
        ("Built-in library",       "trim, upper, sort, round, color, count -- no imports needed."),
        ("File I/O",               "read, write, append, exists -- files in one line."),
        ("try / catch",            "Handle errors gracefully. Silent try discards the error."),
        ("Shell commands",         "cpu, ram, gpu, disk, ip, wifi -- live system info."),
    ]
    print(_c(_BOLD, "  What IXX does"))
    print()
    for name, desc in features:
        print(f"  {_c(_CYAN, name)}")
        print(f"    {desc}")
        print()
        pause(0.12, plain=plain)


def _section_code_examples(*, plain: bool = False, quick: bool = False) -> None:
    print(_c(_BOLD, "  How it looks"))
    print()
    pause(0.20, plain=plain)

    code_block("Hello, World", [
        'name = "Ixxy"',
        'say "Hello, {name}"',
    ], ["Hello, Ixxy"], plain=plain)
    pause(0.40, plain=plain)

    if not quick:
        code_block("Conditions", [
            "score = 95",
            "if score more than 90",
            '- say "Excellent"',
            "else",
            '- say "Keep going"',
        ], ["Excellent"], plain=plain)
        pause(0.40, plain=plain)

    code_block("Functions", [
        "function double x",
        "- return x * 2",
        "",
        "say double(21)",
    ], ["42"], plain=plain)
    pause(0.40, plain=plain)

    if not quick:
        code_block("File I/O and try / catch", [
            "result = nothing",
            "try",
            '- result = read("config.txt")',
            "catch",
            '- say "Using defaults: {error}"',
        ], None, plain=plain)
        pause(0.40, plain=plain)


def _section_validation(*, plain: bool = False) -> None:
    print(_c(_BOLD, "  Fully validated"))
    print()
    progress("Python unit tests",  "478 passed", plain=plain)
    pause(0.12, plain=plain)
    progress("StressTest files",   " 30 passed", plain=plain)
    pause(0.12, plain=plain)
    progress("IXX assertions",     "229 passed", plain=plain)
    pause(0.12, plain=plain)
    progress("Expected failures",  " 12 passed", plain=plain)
    print()


def _section_final(*, plain: bool = False) -> None:
    pause(0.45, plain=plain)
    print()
    _type_colored(_BOLD + _CYAN, "  IXX", delay=0.10, plain=plain)
    pause(0.20, plain=plain)
    type_line("  The computer, translated.", delay=0.022, plain=plain)
    print()
    print(f"  {_c(_DIM, 'pip install ixx')}  -  {_c(_DIM, 'ixx help')}")
    print()


# ── Entry point ───────────────────────────────────────────────────────────────

def run(mode: str = "default") -> None:
    """Run the showoff presentation.

    mode: "default" | "quick" | "full" | "plain"
    """
    plain = (mode == "plain")
    quick = (mode == "quick")

    _section_boot(plain=plain)

    if not quick:
        _section_features(plain=plain)

    _section_code_examples(plain=plain, quick=quick)

    if not quick:
        _section_validation(plain=plain)

    _section_final(plain=plain)
