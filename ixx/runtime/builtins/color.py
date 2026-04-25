"""Color built-in function (v0.5): color()."""

from __future__ import annotations

import os
import sys

from ...ast_nodes import IXXValue
from ..errors import IXXRuntimeError
from ..values import ixx_type_name

# Map of IXX color names to ANSI SGR codes
_COLOR_CODES: dict[str, str] = {
    "red":    "\033[31m",
    "green":  "\033[32m",
    "yellow": "\033[33m",
    "cyan":   "\033[36m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
}
_COLOR_RESET = "\033[0m"


def _try_enable_win_vtp() -> None:
    """Enable Windows Virtual Terminal Processing for stdout so ANSI codes render."""
    if os.name != "nt":
        return
    try:
        import ctypes
        import ctypes.wintypes
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        mode = ctypes.wintypes.DWORD()
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


def _ansi_enabled() -> bool:
    """Return True if ANSI is currently enabled (checks env vars, tty, enables VTP)."""
    if os.environ.get("NO_COLOR", ""):
        return False
    ixx_color = os.environ.get("IXX_COLOR", "")
    if ixx_color == "0":
        return False
    if ixx_color == "1":
        _try_enable_win_vtp()
        return True
    if not sys.stdout.isatty():
        return False
    _try_enable_win_vtp()
    return True


def _builtin_color(color_name: IXXValue, text_val: IXXValue) -> str:
    if not isinstance(color_name, str):
        raise IXXRuntimeError(
            f"'color' first argument must be a color name (text), "
            f"not {ixx_type_name(color_name)}."
        )
    name = color_name.lower().strip()
    if name not in _COLOR_CODES:
        valid = ", ".join(sorted(_COLOR_CODES))
        raise IXXRuntimeError(
            f"Unknown color '{color_name}'.  Valid colors: {valid}."
        )
    text_str = str(text_val) if text_val is not None else ""
    if not _ansi_enabled():
        return text_str
    return f"{_COLOR_CODES[name]}{text_str}{_COLOR_RESET}"


COLOR_BUILTINS: dict[str, object] = {
    "color": _builtin_color,
}
