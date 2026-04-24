"""
IXX Shell — Path Alias Resolution

Resolves friendly path aliases (desktop, downloads, etc.) and
forward-slash sub-paths to absolute pathlib.Path objects.

Usage:
    from ixx.shell.paths import resolve, PathNotFoundError

    try:
        path = resolve("downloads")
        path = resolve("desktop/projects")
        path = resolve("desktop/my folder")   # from quoted token
    except PathNotFoundError as e:
        print(f"ixx: path not found\\n  {e.raw}")
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


class PathNotFoundError(Exception):
    """Raised when a resolved path does not exist on disk."""

    def __init__(self, raw: str, resolved: Path | None = None) -> None:
        self.raw = raw
        self.resolved = resolved
        super().__init__(f"path not found: {raw}")


def _aliases() -> dict[str, Path]:
    """Return the alias map freshly each call so 'here' tracks cwd."""
    home = Path.home()
    cwd = Path.cwd()
    return {
        "desktop":   home / "Desktop",
        "downloads": home / "Downloads",
        "documents": home / "Documents",
        "pictures":  home / "Pictures",
        "music":     home / "Music",
        "videos":    home / "Videos",
        "home":      home,
        "temp":      Path(tempfile.gettempdir()),
        "appdata":   Path(os.environ.get("APPDATA", str(home))),
        "here":      cwd,
        "current":   cwd,
        ".":         cwd,
    }


def resolve(raw: str) -> Path:
    """Resolve *raw* (alias or path) to an absolute, existing Path.

    Supported forms:
        "downloads"                  -> ~/Downloads
        "desktop/projects/test"      -> ~/Desktop/projects/test
        "desktop/my folder"          -> ~/Desktop/my folder  (spaces ok after alias)
        "C:/Users/me/file.txt"       -> passed through as absolute path
        "/absolute/unix/style"       -> passed through as absolute path

    Raises PathNotFoundError if the resolved path does not exist.
    """
    raw = raw.strip()
    if not raw:
        return Path.cwd()

    aliases = _aliases()

    # Normalise separators then split on the first / to separate alias from tail
    normalised = raw.replace("\\", "/")
    parts = normalised.split("/", 1)
    head = parts[0].lower()
    tail = parts[1] if len(parts) > 1 else ""

    if head in aliases:
        base = aliases[head]
        path = base / tail if tail else base
    else:
        path = Path(raw)
        if not path.is_absolute():
            path = Path.cwd() / path

    if not path.exists():
        raise PathNotFoundError(raw, path)

    return path.resolve()
