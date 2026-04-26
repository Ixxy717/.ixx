"""
IXX Shell — File System Command Handlers (folder size, open, list)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from ..paths import resolve, PathNotFoundError
from ..safety import format_bytes, render_table


def _path_error(raw: str, hint: str | None = None) -> None:
    print(f"\n  ixx: path not found\n    {raw}")
    if hint:
        print(f"\n  Try:\n    {hint}")
    print()


# ---------------------------------------------------------------------------
# folder size
# ---------------------------------------------------------------------------

def handle_folder_size(args: list[str]) -> None:
    """Calculate and display the total size of a folder."""
    if not args:
        print("\n  Usage:    folder size <path>")
        print("  Example:  folder size downloads\n")
        return

    raw = " ".join(args)
    try:
        path = resolve(raw)
    except PathNotFoundError as e:
        alias = raw.split("/")[0].lower()
        _path_error(e.raw, hint=f"folder size {alias}" if alias != raw else None)
        return

    if not path.is_dir():
        print(f"\n  {path} is not a folder.\n")
        return

    total = 0
    errors = 0
    for dirpath, _dirnames, filenames in os.walk(path, onerror=lambda _: None):
        for fname in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, fname))
            except OSError:
                errors += 1

    print(f"\n  {path.name}: {format_bytes(total)}")
    if errors:
        print(f"  ({errors} file(s) skipped — no read permission)")
    print()


# ---------------------------------------------------------------------------
# open
# ---------------------------------------------------------------------------

def handle_open(args: list[str]) -> None:
    """Open a folder or file with the OS default application."""
    if not args:
        print("\n  Usage:    open <path>")
        print("  Example:  open downloads\n")
        return

    raw = " ".join(args)
    try:
        path = resolve(raw)
    except PathNotFoundError as e:
        alias = raw.split("/")[0].lower()
        _path_error(e.raw, hint=f"open {alias}" if alias != raw else None)
        return

    try:
        os.startfile(str(path))  # type: ignore[attr-defined]
        print(f"\n  Opened: {path}\n")
    except AttributeError:
        # Non-Windows fallback — wrap subprocess in its own guard so
        # FileNotFoundError (xdg-open/open not installed) stays friendly.
        import subprocess
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=False)
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
            print(f"\n  Opened: {path}\n")
        except FileNotFoundError:
            print(f"\n  Could not open: {path}")
            print("  No application found to open this type of file.\n")
        except Exception as e:
            print(f"\n  Could not open: {path}\n  {e}\n")
    except Exception as e:
        print(f"\n  Could not open: {path}\n  {e}\n")


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

def handle_list(args: list[str]) -> None:
    """List files and folders at a path (folders first)."""
    if args:
        raw = " ".join(args)
        try:
            path = resolve(raw)
        except PathNotFoundError as e:
            alias = raw.split("/")[0].lower()
            _path_error(e.raw, hint=f"list {alias}" if alias != raw else None)
            return
    else:
        path = Path.cwd()

    if not path.is_dir():
        print(f"\n  {path} is not a folder.\n")
        return

    try:
        entries = list(path.iterdir())
    except PermissionError:
        print(f"\n  ixx: no permission to list: {path}\n")
        return

    folders = sorted(
        [e for e in entries if e.is_dir()],
        key=lambda e: e.name.lower(),
    )
    files = sorted(
        [e for e in entries if e.is_file()],
        key=lambda e: e.name.lower(),
    )

    rows: list[list[str]] = []
    for entry in folders:
        rows.append([entry.name, "folder", "-"])
    for entry in files:
        try:
            size = format_bytes(entry.stat().st_size)
        except OSError:
            size = "-"
        rows.append([entry.name, "file", size])

    print(f"\n  {path}\n")
    if not rows:
        print("  (empty)\n")
        return

    print(render_table(["Name", "Type", "Size"], rows))
    print()


# ---------------------------------------------------------------------------
# find file
# ---------------------------------------------------------------------------

def handle_find_file(args: list[str]) -> None:
    """Search for files matching a pattern, with optional path alias.

    Syntax:
        find file <pattern>
        find file <pattern> in <path>
    """
    if not args:
        print("\n  Usage:    find file <pattern> [in <path>]")
        print('  Example:  find file "*.pdf"')
        print('  Example:  find file "invoice" in downloads\n')
        return

    # Parse "in <path>" suffix
    search_path: Path | None = None
    tokens = list(args)
    if len(tokens) >= 2 and tokens[-2].lower() == "in":
        raw_path = tokens[-1]
        tokens = tokens[:-2]
        try:
            search_path = resolve(raw_path)
        except PathNotFoundError as e:
            _path_error(e.raw)
            return

    pattern = " ".join(tokens).strip('"\'')
    if not pattern:
        print('\n  Usage:    find file <pattern> [in <path>]\n')
        return

    base = search_path if search_path else Path.cwd()
    if not base.is_dir():
        print(f"\n  {base} is not a folder.\n")
        return

    # Add wildcard wrapping if user didn't include one
    glob_pattern = pattern if ("*" in pattern or "?" in pattern) else f"*{pattern}*"

    matches: list[Path] = []
    LIMIT = 50
    try:
        for p in base.rglob(glob_pattern):
            if p.is_file():
                matches.append(p)
                if len(matches) >= LIMIT:
                    break
    except PermissionError:
        pass

    if not matches:
        print(f"\n  No files matching '{pattern}' found in {base.name}.\n")
        return

    rows = []
    for m in matches:
        try:
            size = format_bytes(m.stat().st_size)
        except OSError:
            size = "-"
        try:
            rel = m.relative_to(base)
        except ValueError:
            rel = m
        rows.append([m.name, str(rel.parent) if str(rel.parent) != "." else "-", size])

    print(f"\n  Results for '{pattern}' in {base.name}:\n")
    print(render_table(["Name", "Path", "Size"], rows))
    if len(matches) == LIMIT:
        print(f"  (showing first {LIMIT} results)\n")
    else:
        print()
