"""Value display and predicate helpers for the IXX runtime."""

from __future__ import annotations

from ..ast_nodes import IXXValue


def ixx_type_name(value: IXXValue) -> str:
    """Return the IXX type name for a value (never exposes Python names).
    Used by the type() built-in — callers that rely on 'bool' as the return value.
    """
    if value is None:                     return "nothing"
    if isinstance(value, bool):           return "bool"
    if isinstance(value, (int, float)):   return "number"
    if isinstance(value, str):            return "text"
    if isinstance(value, list):           return "list"
    return "unknown"


def ixx_err_type(value: IXXValue) -> str:
    """Return an IXX-friendly type label for use inside *error messages*.

    Same as ixx_type_name() except booleans are described as
    'a yes-or-no value (YES/NO)' so error messages do not expose the
    Python/internal 'bool' label.  Does not affect the type() built-in.
    """
    if isinstance(value, bool):
        return "a yes-or-no value (YES/NO)"
    return ixx_type_name(value)


def display(value: IXXValue) -> str:
    if isinstance(value, bool): return "YES" if value else "NO"
    if isinstance(value, list): return ", ".join(display(v) for v in value)
    if value is None:           return "nothing"
    if isinstance(value, float):
        # Use up to 10 significant figures so 0.1+0.2 shows 0.3, not
        # 0.30000000000000004.  The g format also strips trailing zeros and the
        # decimal point, so 100000.0 shows as 100000, 1.0 as 1, etc.
        return f"{value:.10g}"
    return str(value)


def truthy(value: IXXValue) -> bool:
    if isinstance(value, bool):  return value
    if isinstance(value, int):   return value != 0
    if isinstance(value, float): return value != 0.0
    if isinstance(value, str):   return value != ""
    if isinstance(value, list):  return len(value) > 0
    return False
