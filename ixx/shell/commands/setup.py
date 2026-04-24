"""
IXX Shell — Setup Command

Registers .ixx file type and icon in the Windows registry (HKCU only).
Safe to re-run. No admin required.
"""

from __future__ import annotations

import importlib.resources
import os
import shutil
import sys
from pathlib import Path


def _get_bundled_ico() -> Path:
    """Return path to the bundled ixx-icon.ico inside the installed package."""
    try:
        import importlib.resources
        ref = importlib.resources.files("ixx.assets").joinpath("ixx-icon.ico")
        with importlib.resources.as_file(ref) as p:
            return Path(p)
    except (FileNotFoundError, ModuleNotFoundError, TypeError):
        return None


def _get_installed_ico() -> Path:
    """Copy bundled ICO to %APPDATA%\\IXX\\ and return that stable path."""
    bundled = _get_bundled_ico()
    if bundled is None or not bundled.exists():
        return None

    dest_dir = Path(os.environ.get("APPDATA", "~")) / "IXX"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "ixx-icon.ico"
    shutil.copy2(bundled, dest)
    return dest


def handle_setup(_args: list[str]) -> None:
    if sys.platform != "win32":
        print("  ixx setup: Windows only for now.")
        print("  File association on macOS/Linux is planned for a future release.")
        return

    try:
        import winreg
    except ImportError:
        print("  ixx setup: winreg not available.")
        return

    print("  Setting up IXX file association...")

    # Get or install the icon
    ico_path = _get_installed_ico()
    if ico_path is None or not ico_path.exists():
        print("  Warning: could not locate ixx-icon.ico — icon will not be set.")
        ico_value = ""
    else:
        ico_value = f'"{ico_path}",0'
        print(f"  Icon: {ico_path}")

    try:
        # HKCU\Software\Classes\.ixx -> ixx_file
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.ixx")
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "ixx_file")
        winreg.CloseKey(key)

        # HKCU\Software\Classes\ixx_file -> "IXX Source File"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\ixx_file")
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "IXX Source File")
        winreg.CloseKey(key)

        # HKCU\Software\Classes\ixx_file\DefaultIcon
        if ico_value:
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER, r"Software\Classes\ixx_file\DefaultIcon"
            )
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, ico_value)
            winreg.CloseKey(key)

        print("  Registered .ixx as IXX Source File")

        # Refresh Explorer icon cache
        os.system("ie4uinit.exe -show >nul 2>&1")
        print("  Done. Open a new Explorer window to see the icon.")

    except OSError as e:
        print(f"  Registry error: {e}")
        print("  Try running as Administrator if this persists.")
