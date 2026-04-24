"""
IXX Update Checker

Checks PyPI once per day for a newer version of IXX.
Runs in a background thread — never blocks execution.
Fails silently if offline or if PyPI is unreachable.

Cache file: %APPDATA%/IXX/update-check.json  (Windows)
             ~/.ixx/update-check.json          (other)
"""

from __future__ import annotations

import json
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


_PYPI_URL   = "https://pypi.org/pypi/ixx/json"
_CHECK_INTERVAL_HOURS = 24
_TIMEOUT_SECONDS = 2

_result: Optional[str] = None   # latest version string, or None
_thread: Optional[threading.Thread] = None


def _cache_path() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", "~"))
    else:
        base = Path.home() / ".ixx"
    return base / "IXX" / "update-check.json"


def _read_cache() -> dict:
    try:
        return json.loads(_cache_path().read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_cache(data: dict) -> None:
    try:
        p = _cache_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        pass


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

    cache = _read_cache()
    now = datetime.now(timezone.utc).isoformat()

    # Use cached result if it's fresh enough
    last_checked = cache.get("last_checked", "")
    cached_latest = cache.get("latest_version", "")
    try:
        delta_hours = (
            datetime.now(timezone.utc)
            - datetime.fromisoformat(last_checked)
        ).total_seconds() / 3600
        cache_fresh = delta_hours < _CHECK_INTERVAL_HOURS
    except Exception:
        cache_fresh = False

    if cache_fresh and cached_latest:
        latest = cached_latest
    else:
        latest = _fetch_latest()
        if latest:
            _write_cache({"last_checked": now, "latest_version": latest})

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
        _thread.join(timeout=0.3)   # wait at most 300 ms
        _thread = None

    if _result and _is_newer(_result, current_version):
        arrow = "->" if sys.stdout.encoding and sys.stdout.encoding.lower().startswith("cp") else "→"
        print(
            f"{indent}  Update available: ixx {current_version} {arrow} {_result}"
            f"   (pip install --upgrade ixx)"
        )
