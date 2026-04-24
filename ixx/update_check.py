"""
IXX Update Checker

Checks PyPI every time IXX starts for a newer version.
Runs in a background thread — never blocks execution.
Fails silently if offline or if PyPI is unreachable.
"""

from __future__ import annotations

import os
import sys
import json
import threading
from typing import Optional


_PYPI_URL        = "https://pypi.org/pypi/ixx/json"
_TIMEOUT_SECONDS = 2

_result: Optional[str] = None
_thread: Optional[threading.Thread] = None


def _is_newer(latest: str, current: str) -> bool:
    try:
        def parts(v: str):
            return tuple(int(x) for x in v.split("."))
        return parts(latest) > parts(current)
    except Exception:
        return False


def _fetch_latest() -> Optional[str]:
    try:
        import urllib.request
        with urllib.request.urlopen(_PYPI_URL, timeout=_TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["info"]["version"]
    except Exception:
        return None


def _check_worker(current_version: str) -> None:
    global _result
    latest = _fetch_latest()
    if latest and _is_newer(latest, current_version):
        _result = latest


def start(current_version: str) -> None:
    """Spawn the background check. Call early; collect with notify() later.

    Skipped entirely if the environment variable IXX_NO_UPDATE_CHECK is set
    to any non-empty value.
    """
    if os.environ.get("IXX_NO_UPDATE_CHECK", "").strip():
        return
    global _thread
    _thread = threading.Thread(
        target=_check_worker,
        args=(current_version,),
        daemon=True,
    )
    _thread.start()


def notify(current_version: str, indent: str = "") -> None:
    """
    Wait briefly for the background thread, then print a notice if an update
    is available. Safe to call even if start() was never called.
    """
    global _thread
    if _thread is not None:
        _thread.join(timeout=0.3)
        _thread = None

    if _result and _is_newer(_result, current_version):
        arrow = "->" if sys.stdout.encoding and sys.stdout.encoding.lower().startswith("cp") else "→"
        print(
            f"{indent}  Update available: ixx {current_version} {arrow} {_result}"
            f"   (run: update)"
        )


def latest_version() -> Optional[str]:
    """Return the latest known version string, or None if not yet fetched."""
    return _result
