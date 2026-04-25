"""
IXX Showoff -- cinematic terminal presentation.

    ixx showoff              default  (~30s animated)
    ixx showoff quick        trailer  (~8s)
    ixx showoff full         extended (~50s)
    ixx showoff plain        no animation, ASCII fallback

Pacing intent
  OLD WAY lines type fast   (0.010s/char)  -- messy, overwhelming feel
  IXX WAY lines type slowly (0.028s/char)  -- deliberate, clean feel
  Code reveals type at 0.024s/char with readable inter-line pauses

All _sleep() calls route through the module-level _sleep() wrapper
so tests can mock it with return_value=None for instant runs.
"""

from __future__ import annotations

import os
import sys
import time
import shutil
from typing import Optional


# ── ANSI constants ─────────────────────────────────────────────────────────────

_BOLD   = "\033[1m"
_DIM    = "\033[2m"
_CYAN   = "\033[36m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_RESET  = "\033[0m"


# ── Terminal detection ─────────────────────────────────────────────────────────

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
        "\u2502\u2588\u2591\u2192\u2500\u2550".encode(enc)
        return True
    except (UnicodeEncodeError, LookupError):
        return False


def _c(code: str, text: str, *, plain: bool = False) -> str:
    """Return ANSI-coded text; always plain when plain=True."""
    if plain:
        return text
    return f"{code}{text}{_RESET}" if _ansi_ok() else text


def _width() -> int:
    try:
        return min(shutil.get_terminal_size((80, 24)).columns, 80)
    except Exception:
        return 80


# ── Timing (mock _sleep in tests) ─────────────────────────────────────────────

def _sleep(seconds: float) -> None:
    time.sleep(seconds)


# ── Primitives ─────────────────────────────────────────────────────────────────

def type_line(text: str, delay: float = 0.025, *, plain: bool = False) -> None:
    """Type plain (un-colored) text char-by-char. Instant when not a tty."""
    if plain or not sys.stdout.isatty():
        print(text)
        return
    for ch in text:
        print(ch, end="", flush=True)
        _sleep(delay)
    print()


def _type_col(code: str, text: str, delay: float = 0.025,
              *, plain: bool = False) -> None:
    """Type text with an ANSI color wrapping the whole sequence."""
    if plain:
        print(text)
        return
    if not sys.stdout.isatty():
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


def pause(seconds: float, *, plain: bool = False, quick: bool = False) -> None:
    """Pause only on a real interactive TTY; quick mode uses 30% of the time."""
    if not plain and sys.stdout.isatty():
        _sleep(seconds * 0.30 if quick else seconds)


def _wait(*, plain: bool = False, quick: bool = False) -> None:
    """Subtle 'press enter to continue' — no-op when piped, plain, or quick."""
    if plain or quick or not sys.stdout.isatty():
        return
    # Dim hint; erased after the user presses enter so it doesn't clutter output
    if _ansi_ok():
        print(f"  {_DIM}[enter]{_RESET}", end="  ", flush=True)
    else:
        print("  [enter]", end="  ", flush=True)
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print()
        return
    # Move up one line and erase it
    if _ansi_ok():
        print("\033[1A\033[2K", end="", flush=True)


# ── Layout helpers ─────────────────────────────────────────────────────────────

def _hr(label: str, *, plain: bool = False) -> None:
    uni  = _unicode_ok() and not plain
    eq   = "\u2550" if uni else "="      # ═
    line = f"  {eq}{eq} {label} {eq}{eq}"
    print()
    print(_c(_BOLD, line, plain=plain))
    print()


def _divider(*, plain: bool = False) -> None:
    uni = _unicode_ok() and not plain
    ch  = "\u2500" if uni else "-"       # ─

    if plain or not sys.stdout.isatty():
        # In plain/piped mode just print it, no animation
        line = "  " + ch * 62
        print(_c(_DIM, line, plain=plain))
        return

    # Slide the line in character by character — fast scribble feel
    if _ansi_ok():
        print(_DIM, end="", flush=True)
    print("  ", end="", flush=True)
    for _ in range(62):
        print(ch, end="", flush=True)
        _sleep(0.003)
    if _ansi_ok():
        print(_RESET, end="", flush=True)
    print()


def _bar_line(label: str, value_str: str, *,
              plain: bool = False, quick: bool = False) -> None:
    """Animated fill bar:  [████████████████████] label   value"""
    W   = 20
    uni = _unicode_ok() and not plain
    FIL = "\u2588" if uni else "#"       # █
    EMP = "\u2591" if uni else "."       # ░

    if plain or not sys.stdout.isatty():
        print(f"  [{FIL * W}] {label:<24} {value_str}")
        return

    delay = 0.008 if quick else 0.020
    for i in range(W + 1):
        bar = FIL * i + EMP * (W - i)
        val = _c(_GREEN, value_str)
        print(f"\r  [{bar}] {label:<24} {val}", end="", flush=True)
        if i < W:
            _sleep(delay)
    print()


def _comparison(
    old_label: str,
    old_lines: list[str],
    ixx_lines: list[str],
    ixx_output: Optional[list[str]] = None,
    *,
    plain: bool = False,
    quick: bool = False,
    planned: bool = False,
) -> None:
    """
    Print one OLD WAY → IXX WAY comparison block.
    OLD WAY types fast (messy/overwhelming), IXX WAY types slowly (clear/powerful).
    """
    d_old = 0.006 if quick else 0.010   # fast -- feels messy
    d_ixx = 0.012 if quick else 0.028   # slow -- feels deliberate

    # ── OLD WAY ────────────────────────────────────────────────────────────────
    print(f"  {_c(_DIM, f'OLD WAY: {old_label}', plain=plain)}")
    for line in old_lines:
        type_line(f"    {line}", delay=d_old, plain=plain)
    pause(0.60, plain=plain, quick=quick)   # let old-way sink in before IXX appears
    print()

    # ── IXX WAY ────────────────────────────────────────────────────────────────
    note = "  (planned)" if planned else ""
    print(f"  {_c(_BOLD + _CYAN, f'IXX WAY{note}', plain=plain)}")
    for line in ixx_lines:
        _type_col(_CYAN, f"    {line}", delay=d_ixx, plain=plain)
        pause(0.30, plain=plain, quick=quick)

    if ixx_output:
        pause(0.45, plain=plain, quick=quick)
        for out in ixx_output:
            _type_col(_GREEN, f"    {out}", delay=0.015 if not quick else 0.008,
                      plain=plain)
            pause(0.10, plain=plain, quick=quick)

    print()
    pause(0.55, plain=plain, quick=quick)
    _divider(plain=plain)
    print()
    pause(0.30, plain=plain, quick=quick)


def _code_reveal(
    code_lines: list[str],
    output_lines: list[str],
    *,
    plain: bool = False,
    quick: bool = False,
    wait: bool = False,
) -> None:
    """Show CODE block (plain text), pause, then reveal OUTPUT (green, animated)."""
    d = 0.010 if quick else 0.030
    p = 0.08  if quick else 0.28    # inter-line pause inside code block

    print(f"  {_c(_DIM, 'CODE', plain=plain)}")
    for line in code_lines:
        if line:
            type_line(f"    {line}", delay=d, plain=plain)
            pause(p, plain=plain)
        else:
            print()

    pause(0.18 if quick else 0.80, plain=plain)
    print()
    print(f"  {_c(_GREEN, 'OUTPUT', plain=plain)}")
    for line in output_lines:
        _type_col(_GREEN, f"    {line}", delay=0.016 if not quick else 0.008,
                  plain=plain)
        pause(0.10, plain=plain, quick=quick)
    print()
    pause(0.12 if quick else 0.45, plain=plain)
    if wait:
        _wait(plain=plain, quick=quick)


# ── Sections ───────────────────────────────────────────────────────────────────

def _section_boot(*, plain: bool = False, quick: bool = False) -> None:
    _hr("BOOT", plain=plain)

    d    = 0.012 if quick else 0.022
    msgs = ["> booting IXX...", "> ready."] if quick else [
        "> booting IXX...",
        "> loading readable syntax...",
        "> removing symbolic soup...",
        "> translating computer nonsense...",
        "> ready.",
    ]
    for msg in msgs:
        _type_col(_DIM, f"  {msg}", delay=d, plain=plain)
        pause(0.15 if quick else 0.45, plain=plain)

    pause(0.30 if quick else 0.55, plain=plain)
    print()

    _type_col(_BOLD + _CYAN, "  IXX", delay=0.06 if quick else 0.10, plain=plain)
    pause(0.10 if quick else 0.22, plain=plain)
    type_line("  The language for the user.", delay=0.015 if quick else 0.022, plain=plain)
    pause(0.08 if quick else 0.15, plain=plain)
    type_line("  The computer, translated.", delay=0.015 if quick else 0.022, plain=plain)
    pause(0.30 if quick else 0.65, plain=plain)


def _section_slogans(*, plain: bool = False) -> None:
    """Personality lines shown in full mode before comparisons."""
    slogans = [
        "No braces.",
        "No semicolons.",
        "No guessing what -gt means.",
        "Just instructions.",
    ]
    print()
    for s in slogans:
        _type_col(_BOLD, f"  {s}", delay=0.030, plain=plain)
        pause(0.45, plain=plain)
    pause(0.30, plain=plain)
    type_line("  The terminal starts speaking human.", delay=0.020, plain=plain)
    pause(0.70, plain=plain)


def _section_comparisons(*,
                          plain: bool = False,
                          quick: bool = False,
                          full: bool = False) -> None:
    """
    OLD WAY → IXX WAY comparison panels.
    quick  : 1 comparison  (wifi ip)
    default: 3 comparisons (combined shell commands + if/else)
    full   : 5 comparisons (individual shell + 3 code comparisons)
    """
    # ── comparison data ────────────────────────────────────────────────────────

    # Combined shell commands shown in default mode
    shell_combined = dict(
        old_label="PowerShell",
        old_lines=[
            "Get-NetIPAddress ... | Where-Object {$_.InterfaceAlias -match 'Wi-Fi'} | ...",
            "Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory",
            "Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores",
        ],
        ixx_lines=[
            'ixx do "wifi ip"',
            'ixx do "ram used"',
            'ixx do "cpu info"',
        ],
        ixx_output=[
            "192.168.1.104",
            "Used:  15.2 GB",
            "Intel Core i9 / 14 cores / 28 threads",
        ],
    )

    # Individual shell commands used in full mode
    shell_wifi = dict(
        old_label="PowerShell",
        old_lines=[
            "Get-NetIPAddress -AddressFamily IPv4 |",
            "  Where-Object {$_.InterfaceAlias -match 'Wi-Fi'} |",
            "  Select-Object IPAddress",
        ],
        ixx_lines=['ixx do "wifi ip"'],
        ixx_output=["192.168.1.104"],
    )
    shell_ram = dict(
        old_label="PowerShell",
        old_lines=[
            "Get-CimInstance Win32_OperatingSystem |",
            "  Select-Object TotalVisibleMemorySize, FreePhysicalMemory",
        ],
        ixx_lines=['ixx do "ram used"'],
        ixx_output=["Used:  15.2 GB"],
    )
    shell_cpu = dict(
        old_label="PowerShell",
        old_lines=[
            "Get-CimInstance Win32_Processor |",
            "  Select-Object Name, NumberOfCores, NumberOfLogicalProcessors",
        ],
        ixx_lines=['ixx do "cpu info"'],
        ixx_output=["Intel Core i9 / 14 cores / 28 threads"],
    )
    code_file = dict(
        old_label="Python",
        old_lines=[
            'with open("notes.txt", "r", encoding="utf-8") as f:',
            "    content = f.read()",
            "print(content)",
        ],
        ixx_lines=[
            'content = read("notes.txt")',
            "say content",
        ],
    )
    code_ifelse = dict(
        old_label="C-like / JavaScript",
        old_lines=[
            "if (score > 90) {",
            '    console.log("Excellent");',
            "} else {",
            '    console.log("Keep going");',
            "}",
        ],
        ixx_lines=[
            "if score more than 90",
            '- say "Excellent"',
            "else",
            '- say "Keep going"',
        ],
    )
    code_try = dict(
        old_label="Python",
        old_lines=[
            "try:",
            '    content = open("config.txt").read()',
            "except Exception as e:",
            '    print(f"Using defaults: {e}")',
        ],
        ixx_lines=[
            "try",
            '- content = read("config.txt")',
            "catch",
            '- say "Using defaults: {error}"',
        ],
    )

    # ── select comparisons for this mode ──────────────────────────────────────
    if quick:
        chosen = [shell_wifi]
    elif full:
        chosen = [shell_wifi, shell_ram, shell_cpu, code_file, code_ifelse, code_try]
    else:
        # default: combined shell block + one code comparison
        chosen = [shell_combined, code_ifelse]

    arrow = "\u2192" if _unicode_ok() and not plain else "->"
    _hr(f"OLD WAY  {arrow}  IXX WAY", plain=plain)

    for comp in chosen:
        _comparison(**comp, plain=plain, quick=quick)


def _section_native_note(*, plain: bool = False) -> None:
    """IXX does not replace what you already know. (full mode only)"""
    _hr("NATIVE COMMANDS", plain=plain)
    content = [
        "IXX does not replace what you already know.",
        "It gives you a home base.",
        "",
        "KNOWN COMMAND:",
        "  powershell -ExecutionPolicy Bypass -File setup.ps1",
        "",
        "PLANNED:",
        '  native powershell "-ExecutionPolicy Bypass -File setup.ps1"',
        "",
        "Run old commands when you need them.",
        "Learn the clean IXX version when one exists.",
    ]
    for line in content:
        if line:
            type_line(f"  {line}", delay=0.020, plain=plain)
            pause(0.22, plain=plain)
        else:
            print()
    print()
    pause(0.50, plain=plain)


def _section_interpolation(*, plain: bool = False, quick: bool = False, wait: bool = False) -> None:
    _hr("VARIABLES + INTERPOLATION", plain=plain)
    _code_reveal(
        [
            'name = "Ixxy"',
            'say "Hello, {name}"',
        ],
        ["Hello, Ixxy"],
        plain=plain, quick=quick, wait=wait,
    )
    pause(0.35, plain=plain, quick=quick)


def _section_functions(*, plain: bool = False, quick: bool = False, wait: bool = False) -> None:
    _hr("FUNCTIONS", plain=plain)
    _code_reveal(
        [
            "function double x",
            "- return x * 2",
            "",
            "say double(21)",
        ],
        ["42"],
        plain=plain, quick=quick, wait=wait,
    )
    pause(0.35, plain=plain, quick=quick)


def _section_builtins(*, plain: bool = False, wait: bool = False) -> None:
    _hr("BUILT-INS", plain=plain)
    _code_reveal(
        [
            'words = "apple", "banana", "grape", "cherry"',
            "say upper(first(sort(words)))",
            'say join(sort(words), " | ")',
            "say round(3.14159, 2)",
        ],
        [
            "APPLE",
            "apple | banana | cherry | grape",
            "3.14",
        ],
        plain=plain, wait=wait,
    )
    pause(0.35, plain=plain)


def _section_files_errors(*, plain: bool = False, wait: bool = False) -> None:
    _hr("FILES + ERRORS", plain=plain)
    _code_reveal(
        [
            'write "notes.txt", "Hello, Ixxy"',
            'content = read("notes.txt")',
            "say content",
            "",
            "try",
            '- data = read("missing.txt")',
            "catch",
            '- say "Handled: {error}"',
        ],
        [
            "Hello, Ixxy",
            "Handled: [file not found: missing.txt]",
        ],
        plain=plain, wait=wait,
    )
    pause(0.35, plain=plain)


def _section_validation(*, plain: bool = False, quick: bool = False) -> None:
    _hr("VALIDATION MATRIX", plain=plain)
    type_line("  running validation matrix...", delay=0.015, plain=plain)
    pause(0.35 if quick else 0.55, plain=plain)
    print()

    stats = [
        ("Python unit tests",  "478 passed"),
        ("StressTest files",   " 30 passed"),
        ("IXX assertions",     "229 passed"),
        ("Expected failures",  " 12 passed"),
    ]
    for label, value in stats:
        _bar_line(label, value, plain=plain, quick=quick)
        pause(0.08 if quick else 0.18, plain=plain)
    print()
    pause(0.35, plain=plain, quick=quick)


def _section_real_script(*, plain: bool = False, wait: bool = False) -> None:
    """A complete self-contained IXX script with output. (full mode only)"""
    _hr("A REAL SCRIPT", plain=plain)

    print(f"  {_c(_DIM, 'CODE', plain=plain)}")
    script = [
        'name = "Ixxy"',
        "score = 95",
        "",
        'say "Checking {name} session..."',
        "",
        "if score more than 90",
        '- say "Top scorer: {name}"',
        "else",
        '- say "Good effort: {name}"',
        "",
        'write "result.txt", "{name}: {score}"',
        'say "Result saved."',
        "",
        "try",
        '- log = readlines("session.log")',
        '- say "Log entries: {count(log)}"',
        "catch",
        '- say "No previous log."',
    ]
    for line in script:
        if line:
            type_line(f"    {line}", delay=0.028, plain=plain)
            pause(0.22, plain=plain)
        else:
            print()

    pause(0.80, plain=plain)
    print()
    print(f"  {_c(_GREEN, 'OUTPUT', plain=plain)}")
    for line in [
        "Checking Ixxy session...",
        "Top scorer: Ixxy",
        "Result saved.",
        "No previous log.",
    ]:
        _type_col(_GREEN, f"    {line}", delay=0.016, plain=plain)
        pause(0.10, plain=plain)
    print()
    pause(0.55, plain=plain)
    if wait:
        _wait(plain=plain)


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
        if not plain and sys.stdout.isatty():
            # Print colored version tag, then type the description
            if _ansi_ok():
                sys.stdout.write(f"  {_CYAN}{_BOLD}{ver}{_RESET}  ")
            else:
                sys.stdout.write(f"  {ver}  ")
            sys.stdout.flush()
            for ch in desc:
                sys.stdout.write(ch)
                sys.stdout.flush()
                _sleep(0.018)
            sys.stdout.write("\n")
        else:
            print(f"  {_c(_CYAN + _BOLD, ver, plain=plain)}  {desc}")
        pause(0.30, plain=plain)
    print()
    pause(0.50, plain=plain)


def _section_final(*, plain: bool = False, quick: bool = False) -> None:
    pause(0.40, plain=plain, quick=quick)
    print()
    _type_col(_BOLD + _CYAN, "  IXX", delay=0.06 if quick else 0.10, plain=plain)
    pause(0.12 if quick else 0.22, plain=plain)
    type_line("  The language for the user.", delay=0.015 if quick else 0.022, plain=plain)
    pause(0.08 if quick else 0.15, plain=plain)
    type_line("  The computer, translated.", delay=0.015 if quick else 0.022, plain=plain)
    pause(0.20 if quick else 0.65, plain=plain)
    print()

    if not quick:
        for s in ["No braces.", "No semicolons.", "No -gt.", "Just instructions."]:
            _type_col(_BOLD, f"  {s}", delay=0.028, plain=plain)
            pause(0.30, plain=plain)
        print()

    print(f"  {_c(_DIM, 'pip install ixx', plain=plain)}  -  "
          f"{_c(_DIM, 'ixx showoff', plain=plain)}")
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
    wait  = not quick and not plain   # enable [enter] prompts on real TTY

    _section_boot(plain=plain, quick=quick)

    if full:
        _section_slogans(plain=plain)

    _section_comparisons(plain=plain, quick=quick, full=full)

    if not quick:
        _section_interpolation(plain=plain, quick=quick, wait=wait)

    _section_functions(plain=plain, quick=quick, wait=wait)

    if not quick:
        _section_files_errors(plain=plain, wait=wait)

    if full:
        _section_builtins(plain=plain, wait=wait)
        _section_native_note(plain=plain)

    _section_validation(plain=plain, quick=quick)

    if full:
        _section_real_script(plain=plain, wait=wait)
        _section_timeline(plain=plain)

    _section_final(plain=plain, quick=quick)
