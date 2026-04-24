"""IXX Shell — Common Platform Helpers

Shared utilities used by platform-specific adapter modules.
"""

from __future__ import annotations

import subprocess


def run_command(cmd: list[str], timeout: int = 10) -> str:
    """Run *cmd*, return stdout as a stripped string.

    Never raises — returns an empty string on any error (timeout, missing
    executable, non-zero exit code, etc.).
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip()
    except Exception:
        return ""
