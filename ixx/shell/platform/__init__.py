"""IXX Shell — Platform Adapter Selector

Call current() to get the adapter module for the running OS.

Usage:
    from ixx.shell import platform as _platform
    info = _platform.current().get_cpu_info()
"""

from __future__ import annotations

import sys


def current():
    """Return the platform-specific adapter module."""
    if sys.platform == "win32":
        from . import windows
        return windows
    if sys.platform == "darwin":
        from . import macos
        return macos
    from . import linux
    return linux
