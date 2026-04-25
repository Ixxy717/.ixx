"""
IXX Showoff -- cinematic terminal presentation.

    ixx showoff              default (~15s animated)
    ixx showoff quick        short trailer (~5s)
    ixx showoff full         extended + release timeline
    ixx showoff plain        no animation, ASCII fallback

All sleep calls go through _sleep() so tests can mock it to return_value=None.
"""

from __future__ import annotations

import os
import sys
import time
import shutil
from typing import Optional


# ── ANSI codes ────────────────────────────────────────────────────────────────

_BOLD   = "\033[1m"
_DIM    = "\033[2m"
_CYAN   = "\033[36m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_RESET  = "\033[0m"


def _ansi_ok() -> bool:
    """True if ANSI escape codes will render (mirrors renderer._enable_ansi)."""
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
        h = k.GetStdHandle(-11)
        m = ctypes.c_ulong(0)
        if not k.GetConsoleMode(h, ctypes.byref(m)):
            return False
        if m.value & 0x0004:
            return True
        return bool(k.SetConsoleMode(h, m.value | 0x0004))
    except Exception:
        return False


def _unicode_ok() -> bool:
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        "│█░".encode(enc)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def _c(code: str, text: str, *, plain: bool = False) -> str:
    """Apply ANSI code to text, respecting plain mode and NO_COLOR."""
    if plain:
        return text
    return f"{code}{text}{_RESET}" if _ansi_ok() else text


def _width() -> int:
    try:
        return min(shutil.get_terminal_size((80, 24)).columns, 80)
    except Exception:
        return 80


# ── Timing (mock this in tests) ────────────────────────────────────────────────

def _sleep(seconds: float) -> None:
    time.sleep(seconds)


# ── Primitives ────────────────────────────────────────────────────────────────

def type_line(text: str, delay: float = 0.025, *, plain: bool = False) -> None:
    """Type plain text char-by-char. Do NOT pass pre-colored text here."""
    if plain or not sys.stdout.isatty():
        print(text)
        return
    for ch in text:
        print(ch, end="", flush=True)
        _sleep(delay)
    print()


def _type_col(code: str, text: str, delay: float = 0.025, *,
              plain: bool = False) -> None:
    """Type text with ANSI color wrapping; plain mode prints without color."""
    if plain:
        print(text)
        return
    if not sys.stdout.isatty():
        print(_c(code, text))
        return
    # Animated path: emit ANSI start, type chars, reset
    if _ansi_ok():
        print(code, end="", flush=True)
    for ch in text:
        print(ch, end="", flush=True)
        _sleep(delay)
    if _ansi_ok():
        print(_RESET, end="", flush=True)
    print()


def pause(seconds: float, *, plain: bool = False, quick: bool = False) -> None:
    if not plain and sys.stdout.isatty():
        _sleep(seconds * 0.30 if quick else seconds)


# ── Layout helpers ─────────────────────────────────────────────────────────────

def _hr(label: str, *, plain: bool = False) -> None:
    """Section header:  == LABEL ==  or  ══ LABEL ══"""
    uni = _unicode_ok() and not plain
    eq  = "\u2550" if uni else "="   # ═
    line = f"  {eq}{eq} {label} {eq}{eq}"
    print()
    print(_c(_BOLD, line, plain=plain))
    print()


def _bar_line(label: str, value_str: str, *, plain: bool = False,
              quick: bool = False) -> None:
    """Animated fill bar.  [████████████████████] label    value"""
    W   = 20
    uni = _unicode_ok() and not plain
    FIL = "\u2588" if uni else "#"   # █
    EMP = "\u2591" if uni else "."   # ░

    if plain or not sys.stdout.isatty():
        print(f"  [{FIL * W}] {label:<22} {value_str}")
        return

    delay = 0.008 if quick else 0.018
    for i in range(W + 1):
        bar  = FIL * i + EMP * (W - i)
        val  = _c(_GREEN, value_str)
        print(f"\r  [{bar}] {label:<22} {val}", end="", flush=True)
        if i < W:
            _sleep(delay)
    print()


# ── Sections ──────────────────────────────────────────────────────────────────

def _section_boot(*, plain: bool = False, quick: bool = False) -> None:
    _hr("BOOT", plain=plain)

    d = 0.012 if quick else 0.026
    msgs = ["> booting IXX...", "> ready."] if quick else [
        "> booting IXX...",
        "> loading readable syntax...",
        "> removing symbolic soup...",
        "> translating computer nonsense...",
        "> ready.",
    ]
    for msg in msgs:
        _type_col(_DIM, f"  {msg}", delay=d, plain=plain)
        pause(0.08, plain=plain, quick=quick)

    pause(0.5, plain=plain, quick=quick)
    print()

    # Big title
    _type_col(_BOLD + _CYAN, "  IXX", delay=0.10, plain=plain)
    pause(0.20, plain=plain, quick=quick)
    type_line("  The language for the user.", delay=0.022, plain=plain)
    pause(0.15, plain=plain, quick=quick)
    type_line("  The computer, translated.", delay=0.022, plain=plain)
    pause(0.65, plain=plain, quick=quick)


def _section_slogans(*, plain: bool = False) -> None:
    lines = [
        "No braces.",
        "No semicolons.",
        "No guessing what -gt means.",
        "Just instructions.",
    ]
    print()
    for line in lines:
        _type_col(_BOLD, f"  {line}", delay=0.032, plain=plain)
        pause(0.10, plain=plain)
    pause(0.35, plain=plain)
    type_line("  The terminal starts speaking human.", delay=0.020, plain=plain)
    pause(0.70, plain=plain)


def _section_before_after(*, plain: bool = False, quick: bool = False) -> None:
    _hr("READABLE CODE", plain=plain)
    d = 0.010 if quick else 0.022

    # Comparison 1: conditional
    print(f"  {_c(_DIM, 'BEFORE', plain=plain)}")
    _type_col(_DIM, '    if ($score -gt 90) { Write-Output "Excellent" }',
              delay=d, plain=plain)
    pause(0.35, plain=plain, quick=quick)
    print()
    print(f"  {_c(_BOLD + _CYAN, 'WITH IXX', plain=plain)}")
    for line in ["if score more than 90", '- say "Excellent"']:
        _type_col(_CYAN, f"    {line}", delay=d, plain=plain)
        pause(0.25, plain=plain, quick=quick)
    print()
    pause(0.40, plain=plain, quick=quick)

    if not quick:
        # Comparison 2: try/catch
        print(f"  {_c(_DIM, 'BEFORE', plain=plain)}")
        for line in [
            "try:",
            '    content = open("config.txt").read()',
            "except Exception as e:",
            "    print(e)",
        ]:
            _type_col(_DIM, f"    {line}", delay=d, plain=plain)
        pause(0.35, plain=plain)
        print()
        print(f"  {_c(_BOLD + _CYAN, 'WITH IXX', plain=plain)}")
        for line in [
            "try",
            '- content = read("config.txt")',
            "catch",
            '- say "Could not read: {error}"',
        ]:
            _type_col(_CYAN, f"    {line}", delay=d, plain=plain)
            pause(0.20, plain=plain)
        print()
        pause(0.55, plain=plain)


def _section_functions(*, plain: bool = False, quick: bool = False) -> None:
    _hr("FUNCTIONS", plain=plain)
    d = 0.010 if quick else 0.022

    print(f"  {_c(_DIM, 'CODE', plain=plain)}")
    code = [
        "function double x",
        "- return x * 2",
        "",
        "numbers = 3, 7, 21",
        "say double(first(numbers))",
        "say double(last(numbers))",
    ]
    for line in code:
        if line:
            _type_col(_CYAN, f"    {line}", delay=d, plain=plain)
        else:
            print()

    pause(0.50, plain=plain, quick=quick)
    print()
    print(f"  {_c(_GREEN, 'OUTPUT', plain=plain)}")
    for line in ["6", "42"]:
        print(f"    {_c(_GREEN, line, plain=plain)}")
    print()
    pause(0.50, plain=plain, quick=quick)


def _section_files_errors(*, plain: bool = False) -> None:
    _hr("FILES + ERRORS", plain=plain)
    d = 0.022

    print(f"  {_c(_DIM, 'CODE', plain=plain)}")
    code = [
        'write "notes.txt", "IXX loaded."',
        'append "notes.txt", "Session started."',
        'lines = readlines("notes.txt")',
        "say count(lines)",
        "",
        "result = nothing",
        "try",
        '- result = read("missing.txt")',
        "catch",
        '- say "Handled: {error}"',
    ]
    for line in code:
        if line:
            _type_col(_CYAN, f"    {line}", delay=d, plain=plain)
        else:
            print()

    pause(0.50, plain=plain)
    print()
    print(f"  {_c(_GREEN, 'OUTPUT', plain=plain)}")
    for line in ["2", "Handled: [file not found: missing.txt]"]:
        print(f"    {_c(_GREEN, line, plain=plain)}")
    print()
    pause(0.50, plain=plain)


def _section_system_commands(*, plain: bool = False, quick: bool = False) -> None:
    _hr("SYSTEM COMMANDS", plain=plain)
    d = 0.010 if quick else 0.022

    cmds = [
        ('ixx do "ram used"',  "Used:  15.2 GB"),
        ('ixx do "cpu temp"',  "Temperature:  62 C"),
        ('ixx do "wifi ip"',   "192.168.1.104"),
    ] if not quick else [
        ('ixx do "ram used"', "Used:  15.2 GB"),
    ]

    for cmd, output in cmds:
        _type_col(_CYAN, f"  {cmd}", delay=d, plain=plain)
        pause(0.20, plain=plain, quick=quick)
        print(f"    {_c(_GREEN, output, plain=plain)}")
        pause(0.30, plain=plain, quick=quick)
        print()


def _section_validation(*, plain: bool = False, quick: bool = False) -> None:
    _hr("VALIDATION", plain=plain)

    type_line("  running validation matrix...", delay=0.015, plain=plain)
    pause(0.40, plain=plain, quick=quick)
    print()

    stats = [
        ("unit tests",        "478 passed"),
        ("stress files",      " 30 passed"),
        ("IXX assertions",    "229 passed"),
        ("expected failures", " 12 passed"),
    ]
    for label, value in stats:
        _bar_line(label, value, plain=plain, quick=quick)
        pause(0.10, plain=plain, quick=quick)
    print()


def _section_timeline(*, plain: bool = False) -> None:
    _hr("TIMELINE", plain=plain)

    milestones = [
        ("v0.1", "language booted"),
        ("v0.2", "interactive shell"),
        ("v0.3", "system commands  (cpu, ram, gpu, disk, ip, wifi)"),
        ("v0.4", "user-defined functions + return values"),
        ("v0.5", "built-in library  (text, math, lists, color)"),
        ("v0.6", "file I/O + try/catch + nothing literal"),
    ]
    for ver, desc in milestones:
        print(f"  {_c(_CYAN + _BOLD, ver, plain=plain)}  {desc}")
        pause(0.18, plain=plain)
    print()


def _section_final(*, plain: bool = False) -> None:
    pause(0.45, plain=plain)
    print()
    _type_col(_BOLD + _CYAN, "  IXX", delay=0.10, plain=plain)
    pause(0.20, plain=plain)
    type_line("  The computer, translated.", delay=0.022, plain=plain)
    print()
    print(f"  {_c(_DIM, 'pip install ixx', plain=plain)}  -  "
          f"{_c(_DIM, 'ixx help', plain=plain)}")
    print()


# ── Entry point ────────────────────────────────────────────────────────────────

def run(mode: str = "default") -> None:
    """
    Run the showoff presentation.
    mode: "default" | "quick" | "full" | "plain"
    """
    plain = (mode == "plain")
    quick = (mode == "quick")
    full  = (mode == "full")

    _section_boot(plain=plain, quick=quick)

    if not quick:
        _section_slogans(plain=plain)

    _section_before_after(plain=plain, quick=quick)
    _section_functions(plain=plain, quick=quick)

    if not quick:
        _section_files_errors(plain=plain)
        _section_system_commands(plain=plain, quick=quick)

    _section_validation(plain=plain, quick=quick)

    if full:
        _section_timeline(plain=plain)

    _section_final(plain=plain)
